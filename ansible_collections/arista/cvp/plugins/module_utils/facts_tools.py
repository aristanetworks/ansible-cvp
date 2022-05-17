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
import asyncio
import re
import ansible_collections.arista.cvp.plugins.module_utils.api as api
from typing import List
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.fields import Facts, ApiFields
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


MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info('Start fact_tools module execution')


# ------------------------------------------ #
# Class
# ------------------------------------------ #

class CvFactResource():
    """
    CvFactResource Helper to render facts based on resource type
    """
    def __init__(self, facts_type: str = 'list'):
        if facts_type == 'list':
            self._cache = []

    def __shorten_device_facts(self, device_fact: dict):
        """
        __shorten_device_facts Filter content to return for device type resource

        Parameters
        ----------
        device_fact : dict
            Dictionary of data provided by Cloudvision

        Returns
        -------
        dict
            Dict with only expected fields to be compliant with resource schema
        """
        fact = {
            key: device_fact[key]
            for key in [
                ApiFields.device.HOSTNAME,
                ApiFields.device.FQDN,
                ApiFields.device.SERIAL,
                ApiFields.device.SYSMAC,
                ApiFields.generic.CONFIGLETS,
            ]
        }
        fact[ApiFields.generic.PARENT_NAME] = device_fact[ApiFields.device.CONTAINER_NAME]
        return fact

    def _get_configlet(self):
        """
        _get_configlets Generate facts for configlets resource type

        EXAMPLE:
        --------
        >>> CvFactsResource()._get_configlet()
        {
            "TEAM01-alias": "alias a1 show version",
            "TEAM01-another-configlet": "alias a2 show version"
        }

        Returns
        -------
        dict
            dictionary of configlets.
        """
        if isinstance(self._cache, list):
            return {configlet[ApiFields.generic.NAME]: configlet['config'] for configlet in self._cache}

    def _get_container(self):
        """
        _get_container Generate facts for containers resource type

        EXAMPLE:
        --------
        >>> CvFactsResource()._get_container()
        {
            "TEAM01": {
                "parentContainerName": "Tenant"
            },
            "TEAM01_DC": {
                "parentContainerName": "TEAM01"
            },
            "TEAM01_LEAFS": {
                "parentContainerName": "TEAM01_DC",
                "configlets": [
                    "GLOBAL-ALIASES"
                ]
            }
        }

        Returns
        -------
        dict
            dictionary of containers
        """
        if isinstance(self._cache, list):
            return {entry[ApiFields.generic.NAME]: {
                ApiFields.generic.PARENT_NAME: entry[ApiFields.container.PARENT_NAME],
                ApiFields.generic.CONFIGLETS: entry[ApiFields.generic.CONFIGLETS]}
                for entry in self._cache if ApiFields.generic.NAME in entry.keys()}

    def _get_device(self, verbose: bool = False):
        """
        _get_device Generate facts for devices resource type

        EXAMPLE:
        --------
        >>> CvFactsResource()._get_device()
        [
            {
                "fqdn": "CV-ANSIBLE-EOS01",
                "parentContainerName": "ANSIBLE",
                "configlets": [
                    "01TRAINING-01"
                ],
                "systemMacAddress": "50:8d:00:e3:78:aa",
                "serialNumber": "64793E1D3DE2240F547E5964354214A4"
            }
        ]

        Parameters
        ----------
        verbose : bool, optional
            Trigger to include or not all fields from CV, by default False

        Returns
        -------
        list
            List of devices
        """
        if verbose:
            return self._cache
        else:
            return [self.__shorten_device_facts(
                device_fact=device) for device in self._cache]

    def add(self, data):
        """
        add Add an entry in the list of facts

        Parameters
        ----------
        data : Any
            Data to add as a new entry in the fact list. Should be a dict
        """
        if isinstance(self._cache, list):
            self._cache.append(data)

    def get(self, resource_model: str, verbose: bool = False):
        """
        get Public method to get structured fact for a given resource

        This method transform list of data available in its cache to be exposed using CV module schema.
        Resource_type input will apply correct data transformation to be compatible with cv modules.

        Parameters
        ----------
        resource_model : str
            Name of the resource to apply correct transformation. Can be ['device', 'container', 'configlet']
        verbose : bool, optional
            Trigger to include or not all fields from CV, by default False

        Returns
        -------
        Any
            Facts based on resource_type data model.
        """
        if resource_model == 'configlet':
            return self._get_configlet()
        elif resource_model == 'container':
            return self._get_container()
        elif resource_model == 'device':
            return self._get_device(verbose=verbose)


class CvFactsTools():
    """
    CvFactsTools Object to operate Facts from Cloudvision
    """

    def __init__(self, cv_connection):
        self.__cv_client = cv_connection
        self._cache = {Facts.CACHE_CONTAINERS: None, Facts.CACHE_MAPPERS: None}
        self._facts = {Facts.DEVICE: [], Facts.CONFIGLET: [], Facts.CONTAINER: []}

    def _get_configlets_and_mappers(self, ids: List[str] = None, force_refresh: bool = False):
        """
        Implements cache for the get_configlets_and_mappers() API call.

        Parameters
        ----------
        id : str, optional
            _description_, by default None
        force_refresh : bool, optional
            _description_, by default False

        Returns
        -------
        _type_
            _description_
        """
        if self._cache[Facts.CACHE_MAPPERS] is None or force_refresh:
            MODULE_LOGGER.info('Building configlet mappers cache from Cloudvision')
            # get_configlets_and_mappers() (at least the cvprac method) does not use pagination, not implementing any concurrent logic
            self._cache[Facts.CACHE_MAPPERS] = self.__cv_client.api.get_configlets_and_mappers()['data']
            return self._cache[Facts.CACHE_MAPPERS]
        if ids:
            # Check if we need to refresh the cache
            cache_ids = [configlet[ApiFields.generic.KEY] for configlet in self._cache[Facts.CACHE_MAPPERS]['configlets']]
            if not all(id in cache_ids for id in ids):
                MODULE_LOGGER.info('Cache does not contain the configlets we are looking for, refreshing cache')
                return self._get_configlets_and_mappers(force_refresh=True)
            MODULE_LOGGER.info('Found objects with IDs %s in cache', ids)
        return self._cache[Facts.CACHE_MAPPERS]

    async def gather(self, scope: List[str], regex_filter: str = '.*'):
        # Create tasks to collect data from CloudVision
        tasks = []
        if 'devices' in scope:
            task = asyncio.create_task(self.__fact_devices(filter=regex_filter))
            tasks.append(task)
        if 'containers' in scope:
            task = asyncio.create_task(self.__fact_containers())
            tasks.append(task)
        if 'configlets' in scope:
            task = asyncio.create_task(self.__fact_configlets(filter=regex_filter))
            tasks.append(task)

        # Wait until the tasks have finished
        futures = await asyncio.gather(*tasks, return_exceptions=True)
        for f in futures:
            # All tasks should return None except if they raised an exception
            if isinstance(f, Exception):
                MODULE_LOGGER.error('Failed to execute task, got exception: %s', str(f))
        return self._facts

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
        return asyncio.run(self.gather(scope, regex_filter=regex_filter))

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
        if self._cache[Facts.CACHE_CONTAINERS] is None:
            MODULE_LOGGER.info('Build container cache from Cloudvision')
            try:
                self._cache[Facts.CACHE_CONTAINERS] = self.__cv_client.api.get_containers()['data']
            except CvpApiError as error:
                MODULE_LOGGER.error('Can\'t get information from CV: %s', str(error))
                return None
        MODULE_LOGGER.debug('Current cache data is: %s', str(self._cache[Facts.CACHE_CONTAINERS]))
        for container in self._cache[Facts.CACHE_CONTAINERS]:
            if key == container[ApiFields.generic.KEY]:
                return container[ApiFields.generic.NAME]
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
            device[ApiFields.container.PARENT_CONTAINER_NAME] = self.__get_container_name(key=device[ApiFields.container.PARENT_KEY])
        else:
            device[ApiFields.container.PARENT_CONTAINER_NAME] = ''
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
        configlets = self._get_configlets_and_mappers(ids=configletIds)['configlets']
        return [configlet[ApiFields.generic.NAME] for configlet in configlets if configlet[ApiFields.generic.KEY] in configletIds]

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
        mappers = self._get_configlets_and_mappers()['configletMappers']
        configletIds = [mapper[ApiFields.configlet.ID] for mapper in mappers if mapper[ApiFields.mappers.OBJECT_ID] == netid]
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
        mappers = self._get_configlets_and_mappers()['configletMappers']
        configletIds = [mapper[ApiFields.configlet.ID]
                        for mapper in mappers
                        if (mapper[ApiFields.container.ID] == container_id or mapper[ApiFields.mappers.OBJECT_ID] == container_id)
                        ]
        # Deduplicate entries as containerID is present for every inherited configlets
        configletIds = list(dict.fromkeys(configletIds))
        MODULE_LOGGER.debug('** Container ID is %s', str(container_id))
        MODULE_LOGGER.debug('** Configlet IDs are %s', str(configletIds))
        return self.__configletIds_to_configletName(configletIds=configletIds)

    # Fact management

    async def __fact_devices(self, filter: str = '.*', verbose: bool = False):
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
            cv_devices = await api.call_batch(self.__cv_client.api.get_inventory)
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting devices facts: %s', str(error_msg))
        MODULE_LOGGER.info('Extract device data using filter %s', str(filter))
        facts_builder = CvFactResource()
        for device in cv_devices:
            if re.match(filter, device[ApiFields.device.HOSTNAME]):
                MODULE_LOGGER.debug('Filter has been matched: %s - %s', str(filter), str(device[ApiFields.device.HOSTNAME]))
                if verbose:
                    facts_builder.add(self.__device_update_info(device=device))
                else:
                    device[ApiFields.generic.CONFIGLETS] = self.__device_get_configlets(netid=device[ApiFields.generic.KEY])
                    facts_builder.add(device)
        self._facts[Facts.DEVICE] = facts_builder.get(resource_model='device', verbose=verbose)

    async def __fact_containers(self):
        """
        __fact_containers Collect facts related to container structure
        """
        try:
            cv_containers = await api.call_batch(self.__cv_client.api.get_containers)
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting containers facts: %s', str(error_msg))
        facts_builder = CvFactResource()
        for container in cv_containers['data']:
            if container[ApiFields.generic.NAME] != 'Tenant':
                MODULE_LOGGER.debug('Got following information for container: %s', str(container))
                container[ApiFields.generic.CONFIGLETS] = self.__containers_get_configlets(container_id=container[ApiFields.container.KEY])
                facts_builder.add(container)
        self._facts[Facts.CONTAINER] = facts_builder.get(resource_model='container')

    async def __fact_configlets(self, filter: str = '.*'):
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

        result = await api.call_batch(self.__cv_client.api.get_configlets)
        facts_builder = CvFactResource()
        for configlet in result['data']:
            if re.match(filter, configlet[ApiFields.generic.NAME]):
                MODULE_LOGGER.debug('Adding configlet %s', str(configlet['name']))
                facts_builder.add(configlet)

        MODULE_LOGGER.debug(
            'Final results for configlets: %s',
            str(facts_builder.get(resource_model='configlet').keys())
        )
        self._facts[Facts.CONFIGLET] = facts_builder.get(resource_model='configlet')
