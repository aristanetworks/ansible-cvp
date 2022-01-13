#!/usr/bin/env python
# coding: utf-8 -*-
#
# GNU General Public License v3.0+
#
# Copyright 2022 Arista Networks AS-EMEA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import traceback
import logging
import re
from typing import List
from concurrent.futures import ThreadPoolExecutor
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.fields import FIELD_FACTS_DEVICE, FIELD_FACTS_CONFIGLET, FIELD_FACTS_CONTAINER
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_PARENT_NAME, FIELD_CONFIGLETS
import ansible_collections.arista.cvp.plugins.module_utils.schema_v3 as schema   # noqa # pylint: disable=unused-import
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()
try:
    import jsonschema  # noqa # pylint: disable=unused-import
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


MODULE_LOGGER = logging.getLogger('arista.cvp.fact_tools_v3')
MODULE_LOGGER.info('Start fact_tools module execution')


# ------------------------------------------ #
# CONSTANTS
# ------------------------------------------ #

MAX_WORKERS = 40

# ------------------------------------------ #
# Class
# ------------------------------------------ #


class CvFactsTools():
    """
    CvFactsTools Object to operate Facts from Cloudvision
    """

    def __init__(self, cv_connection):
        self.__cv_client = cv_connection
        self._cache = {'containers': None, 'configlets_mappers': None}
        self.__init_facts()

    def __init_facts(self):
        self._facts = {FIELD_FACTS_DEVICE: [], FIELD_FACTS_CONTAINER: [], FIELD_FACTS_CONFIGLET: []}

    def facts(self, scope: List[str], regex_filter: str = '.*'):
        """
        facts Public API to collect facts from Cloudvision

        Examples
        --------
        >>> result = self.inventory.facts(scope=['configlets'])
        {
            "cvp_containers": {
                "Tenant": {
                    "parentContainerName": "None",
                    "configlets": []
                },
                "Undefined": {
                    "parentContainerName": "Tenant",
                    "configlets": []
                },
                "EAPI": {
                    "parentContainerName": "Tenant",
                    "configlets": [
                        "demo"
                    ]
                }
            }
        }

        Parameters
        ----------
        scope : List[str]
            List of elements to get from Cloudvision server, by default ['devices', 'containers']

        regex_filter: str
            Regular expression to filter devices and configlets. Only element with filter in their name will be exported

        Returns
        -------
        dict
            A dictionary of information with all the data from Cloudvision
        """
        if 'devices' in scope:
            self.__fact_devices(filter=regex_filter)
        if 'containers' in scope:
            self.__fact_containers()
        if 'configlets' in scope:
            self.__fact_configlets(filter=regex_filter)
        return self._facts

    def __get_container_name(self, key: str = 'undefined_container'):
        """
        __get_container_name Helper to get container name from its key

        Send a call to CV to get name of a container key

        Parameters
        ----------
        key : str, optional
            Container key, by default 'undefined_container'

        Returns
        -------
        str
            Container name
        """
        if self._cache['containers'] is None:
            MODULE_LOGGER.warning('Build container cache from Cloudvision')
            try:
                self._cache['containers'] = self.__cv_client.api.get_containers()['data']
            except CvpApiError as error:
                MODULE_LOGGER.error('Can\'t get information from CV: %s', str(error))
                return None
        MODULE_LOGGER.debug('Current cache data is: %s', str(self._cache['containers']))
        for container in self._cache['containers']:
            if key == container['key']:
                return container['name']
        return None

    def __device_update_info(self, device: dict):
        """
        __device_update_info Helper to add missing information for device facts

        Add or update fields from CV response to make output valid with arista.cvp.cv_device_v3 schema

        Parameters
        ----------
        device : dict
            Device data from Cloudvision

        Returns
        -------
        dict
            Updated information
        """
        if device['status'] != '':
            device[FIELD_PARENT_NAME] = self.__get_container_name(key=device['parentContainerKey'])
        else:
            device[FIELD_PARENT_NAME] = ''
        return device

    def __configletIds_to_configletName(self, configletIds: List[str]):
        """
        __configletIds_to_configletName Build a list of configlets name from a list of configlets ID

        Extract list of configlets name from CVP mappers based on a list of configlets ID provided as an input

        Parameters
        ----------
        configletIds : List[str]
            List of configlet IDs

        Returns
        -------
        List[str]
            List of configlets name
        """
        if not configletIds:
            return []
        configlets = self._cache['configlets_mappers']['configlets']
        return [configlet['name'] for configlet in configlets if configlet['key'] in configletIds]

    def __device_get_configlets(self, netid: str):
        # sourcery skip: class-extract-method
        """
        __device_get_configlets Get list of attached configlets to a given device

        Read Configlet Mappers to build a list of configlets name attached to a device identified by is KEY

        Parameters
        ----------
        netid : str
            CVP Key mostly sysMac

        Returns
        -------
        List[str]
            List of configlets name
        """
        if self._cache['configlets_mappers'] is None:
            MODULE_LOGGER.warning('Build configlet mappers cache from Cloudvision')
            self._cache['configlets_mappers'] = self.__cv_client.api.get_configlets_and_mappers()['data']
        mappers = self._cache['configlets_mappers']['configletMappers']
        configletIds = [mapper['configletId'] for mapper in mappers if mapper['objectId'] == netid]
        MODULE_LOGGER.debug('** NetelementID is %s', str(netid))
        MODULE_LOGGER.debug('** Configlet IDs are %s', str(configletIds))
        return self.__configletIds_to_configletName(configletIds=configletIds)

    def __containers_get_configlets(self, container_id):
        """
        __containers_get_configlets Get list of attached configlets to a given container

        Read Configlet Mappers to build a list of configlets name attached to a container identified by is KEY

        Parameters
        ----------
        container_id : str
            CVP Key for the container

        Returns
        -------
        List[str]
            List of configlets name
        """
        if self._cache['configlets_mappers'] is None:
            MODULE_LOGGER.warning('Build configlet mappers cache from Cloudvision')
            self._cache['configlets_mappers'] = self.__cv_client.api.get_configlets_and_mappers()['data']
        mappers = self._cache['configlets_mappers']['configletMappers']
        configletIds = [mapper['configletId'] for mapper in mappers if mapper['containerId'] == container_id]
        # Deduplicate entries as containerID is present for every inherited configlets
        configletIds = list(dict.fromkeys(configletIds))
        MODULE_LOGGER.debug('** Container ID is %s', str(container_id))
        MODULE_LOGGER.debug('** Configlet IDs are %s', str(configletIds))
        return self.__configletIds_to_configletName(configletIds=configletIds)

    # Fact management

    def __fact_devices(self, filter: str = '.*', verbose: str = 'short'):
        """
        __fact_devices Collect facts related to device inventory

        [extended_summary]

        Parameters
        ----------
        filter : str, optional
            Regular Expression to filter device. Search is done against FQDN to allow domain filtering, by default .*
        verbose : str, optional
            Facts verbosity: full get all data from CV where short get only cv_modules data, by default 'short'
        """
        try:
            cv_devices = self.__cv_client.api.get_inventory()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting devices facts: %s', str(error_msg))
        MODULE_LOGGER.info('Extract device data using filter %s', str(filter))
        for device in cv_devices:
            if re.match(filter, device['hostname']):
                MODULE_LOGGER.debug('Filter has been matched: %s - %s', str(filter), str(device['hostname']))
                device_out = {}
                if verbose == 'full':
                    device_out = self.__device_update_info(device=device)
                else:
                    for key in ['hostname', 'fqdn', 'systemMacAddress', 'serialNumber']:
                        device_out[key] = device[key]
                device_out[FIELD_PARENT_NAME] = device['containerName']
                device_out[FIELD_CONFIGLETS] = self.__device_get_configlets(netid=device['key'])
                self._facts[FIELD_FACTS_DEVICE].append(device_out)

    def __fact_containers(self):
        """
        __fact_containers Collect facts related to container structure
        """
        try:
            cv_containers = self.__cv_client.api.get_containers()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting containers facts: %s', str(error_msg))
        for container in cv_containers['data']:
            if container['name'] != 'Tenant':
                self._facts[FIELD_FACTS_CONTAINER] = {
                    container['name']: {
                        FIELD_PARENT_NAME: container['parentName'],
                        FIELD_CONFIGLETS: self.__containers_get_configlets(container_id=container['key'])
                    }
                }

    def __fact_configlets(self, filter: str = '.*', configlets_per_call: int = 10):
        """
        __fact_configlets Collect facts related to configlets structure

        Execute parallel calls to get a list of all static configlets from CVP

        Parameters
        ----------
        filter : str, optional
            Regular Expression to filter configlets, by default .*
        configlets_per_call : int, optional
            Number of configlets to retrieve per API call, by default 10
        """
        max_range_calc = self.__cv_client.api.get_configlets(start=0, end=1)['total'] + 1
        futures_list = []
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for i in range(0, max_range_calc, configlets_per_call):
                futures_list.append(
                    executor.submit(self.__cv_client.api.get_configlets, start=i, end=i + configlets_per_call)
                )

            for future in futures_list:
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                except Exception as error:
                    results.append(None)
                    MODULE_LOGGER.critical('Exception in getting configlet (%s): %s', str(error), str(future.result()))
        configlets_result = {}
        for future in results:
            for configlet in future['data']:
                if re.match(filter, configlet['name']):
                    configlets_result[configlet['name']] = configlet['config']

        MODULE_LOGGER.debug('Final results for configlets: %s', str(configlets_result.keys()))
        self._facts[FIELD_FACTS_CONFIGLET] = configlets_result
