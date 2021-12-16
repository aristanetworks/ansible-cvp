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
from ansible.module_utils.basic import AnsibleModule   # noqa # pylint: disable=unused-import
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_PARENT_NAME
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


# ------------------------------------------ #
# Class
# ------------------------------------------ #

class CvFactsTools():
    """
    CvFactsTools Object to operate Facts from Cloudvision
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module
        self._cache = {'containers': {}}
        self._facts = {FIELD_FACTS_DEVICE: []}

    def facts(self, scope: List[str] = ['devices', 'containers']):   # noqa # pylint: disable=dangerous-default-value
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
            self._fact_devices()
        if 'containers' in scope:
            self._fact_containers()
        return self._facts

    def _get_container_name(self, key: str = 'undefined_container'):
        """
        _get_container_name Helper to get container name from its key

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
        if key in self._cache['containers'].keys():
            return self._cache['containers'][key]
        try:
            result = self.__cv_client.api.get_container_by_id(key=key)['name']
        except CvpApiError as error:
            MODULE_LOGGER.error('Can\'t get information from CV: %s', str(error))
            return None
        else:
            self._cache['containers'][key] = result
            return result

    def device_update_info(self, device: dict):
        """
        device_update_info Helper to add missing information for device facts

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
            device[FIELD_PARENT_NAME] = self._get_container_name(key=device['parentContainerKey'])
        else:
            device[FIELD_PARENT_NAME] = ''
        return device

    def containers_get_configlets(self, container_id):
        """
        containers_get_configlets Build list of configlets attached to a container

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

    ### Fact management

    def _fact_devices(self):
        """
        _fact_devices Collect facts related to device inventory
        """
        try:
            cv_devices = self.__cv_client.api.get_inventory()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting devices facts: %s', str(error_msg))
        for device in cv_devices:
            device = self.device_update_info(device=device)
            self._facts[FIELD_FACTS_DEVICE].append(device)

    def _fact_containers(self):
        """
        _fact_containers Collect facts related to container structure
        """
        try:
            cv_containers = self.__cv_client.api.get_containers()
        except CvpApiError as error_msg:
            MODULE_LOGGER.error('Error when collecting devices facts: %s', str(error_msg))
        self._facts[FIELD_FACTS_CONTAINER] = {
            container['name']: {
                FIELD_PARENT_NAME: container['parentName'],
                'configlets': self.containers_get_configlets(container_id=container['key'])
            }
            for container in cv_containers['data']
        }
