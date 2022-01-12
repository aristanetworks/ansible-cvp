#!/usr/bin/env python
# coding: utf-8 -*-
#
# GNU General Public License v3.0+
#
# Copyright 2019 Arista Networks AS-EMEA
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
from typing import List
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
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
# Fields name to use in classes
# ------------------------------------------ #


# CONSTANTS for fields in API data
FIELD_FACTS_DEVICE = 'cvp_devices'
FIELD_FACTS_CONTAINER = 'cvp_containers'
FIELD_FACTS_CONFIGLET = 'cvp_configlets'


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
        self._facts = {FIELD_FACTS_DEVICE: []}

    def facts(self, scope: List[str]):
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
        scope : List[str], optional
            List of elements to get from Cloudvision server, by default ['devices', 'containers']

        Returns
        -------
        dict
            A dictionary of information with all the data from Cloudvision
        """
        if 'devices' in scope:
            self.__fact_devices()
        if 'containers' in scope:
            self.__fact_containers()
        if 'configlets' in scope:
            self.__fact_configlets()
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

    def __containers_get_configlets(self, container_id):
        """
        __containers_get_configlets Build list of configlets attached to a container

        Create list of configlets attached to container and using a valid structure against arista.cvp._cv_container_v3 module

        Parameters
        ----------
        container_id : str
            Container key from Cloudvision

        Returns
        -------
        list
            List of configlets name
        """
        cv_result = self.__cv_client.api.get_configlets_by_container_id(c_id=container_id)
        if cv_result['total'] == 0:
            return []
        return [configlet['name'] for configlet in cv_result['configletList']]

    # TODO: to be removed during code review
    # By using this approach for 18 devices we move from 1.78sec to 3.69sec
    # def __device_get_configlets(self, netid: str):
    #     try:
    #         cv_result = self.__cv_client.api.get_configlets_by_netelement_id(d_id=netid)
    #     except CvpApiError as api_error:
    #         MODULE_LOGGER.error('Device does not exist: {0}'.format(netid))
    #         return []
    #     if cv_result['total'] == 0:
    #         return []
    #     return [configlet['name'] for configlet in cv_result['configletList'] if configlet['containerCount'] == 0]

    # By using this approach for 18 devices we stay at 1.78sec
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

    # Fact management

    def __fact_devices(self, verbose: str = 'short'):
        """
        __fact_devices Collect facts related to device inventory
        """
        try:
            cv_devices = self.__cv_client.api.get_inventory()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting devices facts: %s', str(error_msg))
        for device in cv_devices:
            device_out = {}
            if verbose == 'full':
                device_out = self.__device_update_info(device=device)
            else:
                for key in ['hostname', 'fqdn', 'systemMacAddress']:
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

    def __fact_configlets(self):
        try:
            cv_configlets = self.__cv_client.api.get_configlets()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting configlets facts: %s', str(error_msg))
        self._facts[FIELD_FACTS_CONFIGLET] = {configlet['name']: configlet['config'] for configlet in cv_configlets['data']}
