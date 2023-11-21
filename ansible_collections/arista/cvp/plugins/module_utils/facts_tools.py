#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#
# Copyright 2022 Arista Networks
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
import os
from typing import List
from concurrent.futures import ThreadPoolExecutor
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import FactsResponseFields
import ansible_collections.arista.cvp.plugins.module_utils.tools_schema as schema   # noqa # pylint: disable=unused-import
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
                Api.device.HOSTNAME,
                Api.device.FQDN,
                Api.device.SERIAL,
                Api.device.SYSMAC,
                Api.generic.CONFIGLETS,
                Api.generic.IMAGE_BUNDLE_NAME,
                Api.device.MGMTIP,
            ]
        }
        fact[Api.generic.PARENT_CONTAINER_NAME] = device_fact[Api.device.CONTAINER_NAME]
        return fact

    def __shorten_task_facts(self, task_fact: dict):
        """
        __shorten_task_facts Filter content to return for task type resource

        Parameters
        ----------
        task_fact : dict
            Dictionary of data provided by Cloudvision

        Returns
        -------
        dict
            Dict with only expected fields to be compliant with resource schema
        """

        fact = {
            key: task_fact[key]
            for key in [
                Api.generic.TASK_ID,
                Api.device.AUTHOR,
                Api.device.DESCRIPTION,
                Api.device.STATUS,
                Api.device.STATE,
                Api.device.CCID,
                Api.device.CCIDV2,
                Api.device.TASK_DETAILS,
            ]
        }
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
            return {configlet[Api.generic.NAME]: configlet[Api.generic.CONFIG] for configlet in self._cache}

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
            return {entry[Api.generic.NAME]: {
                Api.generic.PARENT_CONTAINER_NAME: entry[Api.container.PARENT_NAME],
                Api.generic.CONFIGLETS: entry[Api.generic.CONFIGLETS],
                Api.generic.IMAGE_BUNDLE_NAME: entry[Api.generic.IMAGE_BUNDLE_NAME]}
                for entry in self._cache if Api.generic.NAME in entry.keys()}

    def _get_device(self, verbose: str = 'short'):
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
        verbose : str, optional
            Trigger to include or not all fields from CV, by default 'short'

        Returns
        -------
        list
            List of devices
        """
        if verbose == 'long':
            return self._cache
        else:
            return [self.__shorten_device_facts(
                device_fact=device) for device in self._cache]

    def _get_image(self):
        """
        _get_image Generate facts for images resource type

        EXAMPLE:
        --------
        >>> CvFactsResource()._get_image()
        {
            EOS-4.25.4M.swi:
                {
                    imageBundleKeys: ['imagebundle_1658329041200536707']
                    imageFile: ''
                    imageFileName: EOS-4.25.4M.swi
                    imageId: EOS-4.25.4M.swi
                    imageSize: 931.9 MB
                    isHotFix: 'false'
                    isRebootRequired: 'true'
                    key: EOS-4.25.4M.swi
                    md5: ''
                    name: EOS-4.25.4M.swi
                    sha512: 54e6874984a3a46b1371bd6c53196bbd622c922606b65d59ed3fa23e918a43d174d468ac9179146a4d1b00e7094c4755ea90c2df4ab94c562e745c14a402b491
                    swiMaxHwepoch: '2'
                    swiVarient: US
                    uploadedDateinLongFormat: 1658329024667
                    user: cvp system
                    version: 4.25.4M-22402993.4254M
                }
        }

        """
        if isinstance(self._cache, list):
            return {image[Api.generic.NAME]: image for image in self._cache}

    def _get_task(self, verbose: str = 'short'):
        """
        _get_image Generate facts for tasks resource type

        EXAMPLE:
        --------
        >>> CvFactsResource()._get_task()
        {
            "95": {
                    "ccId": "",
                    "ccIdV2": "",
                    "createdBy": "arista",
                    "description": "Device Add: leaf3.atd.lab - To be added to Container pod1",
                    "workOrderDetails": {
                        "ipAddress": "192.168.0.14",
                        "netElementHostName": "leaf3.atd.lab",
                        "netElementId": "00:1c:73:b8:26:81",
                        "serialNumber": "787EDD0A49B06189A8B4810C2982AAEC",
                        "workOrderDetailsId": "",
                        "workOrderId": ""
                    },
                    "workOrderId": "95",
                    "workOrderState": "ACTIVE",
                    "workOrderUserDefinedStatus": "Pending"
                },

        }
        """
        if isinstance(self._cache, list):
            if verbose == 'long':
                return {task[Api.generic.TASK_ID]: task for task in self._cache}
            else:
                return {task[Api.generic.TASK_ID]: self.__shorten_task_facts(task_fact=task) for task in self._cache}

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

    def get(self, resource_model: str, verbose: str = 'short'):
        """
        get Public method to get structured fact for a given resource

        This method transform list of data available in its cache to be exposed using CV module schema.
        Resource_type input will apply correct data transformation to be compatible with cv modules.

        Parameters
        ----------
        resource_model : str
            Name of the resource to apply correct transformation. Can be ['device', 'container', 'configlet']
        verbose : str, optional
            Trigger to include or not all fields from CV, by default 'short'

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
        elif resource_model == 'image':
            return self._get_image()
        elif resource_model == 'task':
            return self._get_task(verbose=verbose)


class CvFactsTools():
    """
    CvFactsTools Object to operate Facts from Cloudvision
    """

    def __init__(self, cv_connection):
        self.__cv_client = cv_connection
        self._cache = {FactsResponseFields.CACHE_CONTAINERS: None, FactsResponseFields.CACHE_MAPPERS: None}
        self._max_worker = min(32, (os.cpu_count() or 1) + 4)
        self.__init_facts()

    def __init_facts(self):
        self._facts = {FactsResponseFields.DEVICE: [], FactsResponseFields.CONFIGLET: [],
                       FactsResponseFields.CONTAINER: [], FactsResponseFields.IMAGE: [],
                       FactsResponseFields.TASK: []}

    def facts(self, scope: List[str], regex_filter: str = '.*', verbose: str = 'short'):
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
            List of elements to get from Cloudvision server, by default ['configlets', 'containers', 'devices', 'images', 'tasks']

        regex_filter: str
            Regular expression to filter devices and configlets. Only element with filter in their name will be exported
        verbose : str, optional
            Facts verbosity: full get all data from CV where short get only cv_modules data, by default 'short'

        Returns
        -------
        dict
            A dictionary of information with all the data from Cloudvision
        """
        if 'devices' in scope:
            self.__fact_devices(filter=regex_filter, verbose=verbose)
        if 'containers' in scope:
            self.__fact_containers(filter=regex_filter)
        if 'configlets' in scope:
            self.__fact_configlets(filter=regex_filter)
        if 'images' in scope:
            self.__fact_images(filter=regex_filter)
        if 'tasks' in scope:
            self.__fact_tasks(filter=regex_filter, verbose=verbose)
        return self._facts

    def __get_container_name(self, key: str = Api.container.UNDEFINED_CONTAINER_ID):
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
        if self._cache[FactsResponseFields.CACHE_CONTAINERS] is None:
            MODULE_LOGGER.warning('Build container cache from Cloudvision')
            try:
                self._cache[FactsResponseFields.CACHE_CONTAINERS] = self.__cv_client.api.get_containers()['data']
            except CvpApiError as error:
                MODULE_LOGGER.error('Can\'t get information from CV: %s', str(error))
                return None
        MODULE_LOGGER.debug('Current cache data is: %s', str(self._cache[FactsResponseFields.CACHE_CONTAINERS]))
        for container in self._cache[FactsResponseFields.CACHE_CONTAINERS]:
            if key == container[Api.generic.KEY]:
                return container[Api.generic.NAME]
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
            device[Api.generic.PARENT_CONTAINER_NAME] = self.__get_container_name(key=device[Api.device.PARENT_CONTAINER_KEY])
        else:
            device[Api.generic.PARENT_CONTAINER_NAME] = ''
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
        if self._cache[FactsResponseFields.CACHE_MAPPERS] is None:
            MODULE_LOGGER.warning('Build configlet mappers cache from Cloudvision')
            self._cache[FactsResponseFields.CACHE_MAPPERS] = self.__cv_client.api.get_configlets_and_mappers()['data']
        configlets = self._cache[FactsResponseFields.CACHE_MAPPERS][Api.generic.CONFIGLETS]
        return [configlet[Api.generic.NAME] for configlet in configlets if configlet[Api.generic.KEY] in configletIds]

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
        if self._cache[FactsResponseFields.CACHE_MAPPERS] is None:
            MODULE_LOGGER.warning('Build configlet mappers cache from Cloudvision')
            self._cache[FactsResponseFields.CACHE_MAPPERS] = self.__cv_client.api.get_configlets_and_mappers()['data']
        mappers = self._cache[FactsResponseFields.CACHE_MAPPERS]['configletMappers']
        configletIds = [mapper[Api.configlet.ID] for mapper in mappers if mapper[Api.mappers.OBJECT_ID] == netid]
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
        if self._cache[FactsResponseFields.CACHE_MAPPERS] is None:
            MODULE_LOGGER.warning('Build configlet mappers cache from Cloudvision')
            self._cache[FactsResponseFields.CACHE_MAPPERS] = self.__cv_client.api.get_configlets_and_mappers()['data']
        mappers = self._cache[FactsResponseFields.CACHE_MAPPERS]['configletMappers']
        configletIds = [mapper[Api.configlet.ID]
                        for mapper in mappers
                        if (mapper[Api.container.ID] == container_id or mapper[Api.mappers.OBJECT_ID] == container_id)
                        ]
        # Deduplicate entries as containerID is present for every inherited configlets
        configletIds = list(dict.fromkeys(configletIds))
        MODULE_LOGGER.debug('** Container ID is %s', str(container_id))
        MODULE_LOGGER.debug('** Configlet IDs are %s', str(configletIds))
        return self.__configletIds_to_configletName(configletIds=configletIds)

    def __container_get_image_bundle_name(self, container_id):
        """
        __container_get_image_bundle_name Get the name of the image bundle attached to a container

        Parameters
        ----------
        container_id : str
            CVP Key for the container

        Returns
        -------
        Str
            The name of the image bundle, if assigned.
        """
        bundle_name = ''

        try:
            bundle = self.__cv_client.api.get_image_bundle_by_container_id(container_id)
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting container bundle facts: %s', str(error_msg))

        MODULE_LOGGER.debug('Bundle data assigned to container: %s', str(bundle))
        if len(bundle['imageBundleList']) == 1:
            bundle_name = bundle['imageBundleList'][0]['name']
        elif len(bundle['imageBundleList']) > 1:
            MODULE_LOGGER.error('Number of image bundles is > 1 on %s', str(container_id))
        else:
            pass
        return bundle_name

    def __device_get_image_bundle_name(self, device_id):
        """
        __device_get_image_bundle_name Get the name of the image bundle attached to a device

        Parameters
        ----------
        device_id : str
            MAC address/key for the device

        Returns
        -------
        Str
            The name of the image bundle, if assigned.
        """
        bundle_name = ''

        try:
            bundle = self.__cv_client.api.get_device_image_info(device_id)
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting device bundle facts: %s', str(error_msg))

        MODULE_LOGGER.debug('Bundle data assigned to container: %s', str(bundle))
        if bundle is not None and bundle['bundleName'] is not None:
            return bundle['bundleName']
        else:
            return bundle_name

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
            raise error_msg
        MODULE_LOGGER.info('Extract device data using filter %s', str(filter))
        facts_builder = CvFactResource()
        for device in cv_devices:
            if re.match(filter, device[Api.device.HOSTNAME]):
                MODULE_LOGGER.debug('Filter has been matched: %s - %s', str(filter), str(device[Api.device.HOSTNAME]))
                if verbose == 'long':
                    facts_builder.add(self.__device_update_info(device=device))
                else:
                    device[Api.generic.CONFIGLETS] = self.__device_get_configlets(netid=device[Api.generic.KEY])
                    device[Api.generic.IMAGE_BUNDLE_NAME] = self.__device_get_image_bundle_name(device[Api.generic.KEY])

                    facts_builder.add(device)
        self._facts[FactsResponseFields.DEVICE] = facts_builder.get(resource_model='device', verbose=verbose)

    def __fact_containers(self, filter: str = '.*'):
        """
        __fact_containers Collect facts related to container structure
        """
        try:
            cv_containers = self.__cv_client.api.get_containers()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting containers facts: %s', str(error_msg))
            raise error_msg
        facts_builder = CvFactResource()
        for container in cv_containers['data']:
            if container[Api.generic.NAME] != 'Tenant':
                if re.match(filter, container[Api.generic.NAME]):
                    MODULE_LOGGER.debug('Got following information for container: %s', str(container))
                    container[Api.generic.CONFIGLETS] = self.__containers_get_configlets(container_id=container[Api.container.KEY])
                    container[Api.generic.IMAGE_BUNDLE_NAME] = self.__container_get_image_bundle_name(container_id=container[Api.container.KEY])
                    facts_builder.add(container)
        self._facts[FactsResponseFields.CONTAINER] = facts_builder.get(resource_model='container')

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
        try:
            max_range_calc = self.__cv_client.api.get_configlets(start=0, end=1)['total'] + 1
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting configlets facts: %s', str(error_msg))
            raise error_msg
        futures_list = []
        results = []
        with ThreadPoolExecutor(max_workers=self._max_worker) as executor:
            for configlet_index in range(0, max_range_calc, configlets_per_call):
                futures_list.append(
                    executor.submit(self.__cv_client.api.get_configlets, start=configlet_index, end=configlet_index + configlets_per_call)
                )

            for future in futures_list:
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                except Exception as error:
                    results.append(None)
                    MODULE_LOGGER.critical(
                        'Exception in getting configlet (%s): %s',
                        str(error),
                        str(future.result())
                    )
        facts_builder = CvFactResource()
        for future in results:
            for configlet in future['data']:
                if re.match(filter, configlet[Api.generic.NAME]):
                    MODULE_LOGGER.debug('Adding configlet %s', str(configlet[Api.generic.NAME]))
                    facts_builder.add(configlet)

        MODULE_LOGGER.debug(
            'Final results for configlets: %s',
            str(facts_builder.get(resource_model='configlet').keys())
        )
        self._facts[FactsResponseFields.CONFIGLET] = facts_builder.get(resource_model='configlet')

    def __fact_images(self, filter: str = '.*'):
        """
        __fact_images Collect facts related to images
        """
        try:
            cv_images = self.__cv_client.api.get_images()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting images facts: %s', str(error_msg))
            raise error_msg

        facts_builder = CvFactResource()
        for image in cv_images['data']:
            # filter by image name
            if re.match(filter, image[Api.generic.NAME]):
                MODULE_LOGGER.debug('Got following information for image: %s', str(image))
                facts_builder.add(image)

        MODULE_LOGGER.debug(
            'Final results for images: %s',
            str(facts_builder.get(resource_model='image').keys())
        )
        self._facts[FactsResponseFields.IMAGE] = facts_builder.get(resource_model='image')

    def __fact_tasks(self, filter: str = '.*', verbose: str = 'short'):
        """
        __fact_images Collect facts related to images

        Parameters
        ----------
        filter : str, optional
            Regular Expression to filter tasks - <task_id>,'Failed', 'Pending', 'Completed', 'Cancelled', by default '.*'
        """
        facts_builder = CvFactResource()
        total_tasks = 0
        if filter == '.*':
            try:
                cv_tasks = self.__cv_client.api.get_tasks()
                total_tasks = cv_tasks['total']
                cv_tasks = cv_tasks['data']
            except CvpApiError as error_msg:
                MODULE_LOGGER.error('Error when collecting task facts: %s', str(error_msg))
                raise error_msg
        elif isinstance(filter, str):
            # filter by task status
            try:
                cv_tasks = self.__cv_client.api.get_tasks_by_status(filter)
            except CvpApiError as error_msg:
                MODULE_LOGGER.error('Error when collecting %s task facts: %s', filter, str(error_msg))
                raise error_msg
        elif isinstance(filter, int):
            # filter by task_id
            try:
                cv_tasks = self.__cv_client.api.get_task_by_id(filter)
            except CvpApiError as error_msg:
                MODULE_LOGGER.error('Error when collecting %s task facts: %s', filter, str(error_msg))
                raise error_msg

        for task in cv_tasks:
            MODULE_LOGGER.debug('Got following information for task: %s', str(task))
            facts_builder.add(task)

        final_result = facts_builder.get(resource_model='task', verbose=verbose)

        if not total_tasks:
            total_tasks = len(final_result)

        final_result.update({'total_tasks': total_tasks})

        MODULE_LOGGER.debug(
            'Final results for task: %s',
            str(final_result)
        )

        self._facts[FactsResponseFields.TASK] = final_result
