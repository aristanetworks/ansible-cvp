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
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_CONFIGLETS
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpClientError  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()
# try:
#     import jsonschema
#     HAS_JSONSCHEMA = True
# except ImportError:
#     HAS_JSONSCHEMA = False
import ansible_collections.arista.cvp.plugins.module_utils.schema as schema

MODULE_LOGGER = logging.getLogger('arista.cvp.container_tools_v3')
MODULE_LOGGER.info('Start cv_container_v3 module execution')


# CONSTANTS for fields in API data
FIELD_COUNT_DEVICES = 'childNetElementCount'
FIELD_COUNT_CONTAINERS = 'childContainerCount'
FIELD_PARENT_ID = 'parentContainerId'
FIELD_PARENT_NAME = 'parentContainerName'
FIELD_NAME = 'name'
FIELD_KEY = 'key'
FIELD_TOPOLOGY = 'topology'
FIELD_CONFIGLETS = 'configlets'


class ContainerInput(object):
    """
    ContainerInput Object to manage Container Topology in context of arista.cvp collection.

    [extended_summary]
    """

    def __init__(self, user_topology: dict, container_root_name: str = 'Tenant', schema=schema.SCHEMA_CV_CONTAINER):
        self.__topology = user_topology
        self.__parent_field: str = FIELD_PARENT_NAME
        self.__root_name = container_root_name
        self.__schema = schema

    def __get_container_data(self, container_name: str, key_name: str):
        """
        _get_container_data Get a specific subset of data for a given container

        Parameters
        ----------
        container_name : str
            Name of the container
        key_name : str
            Name of the key to extract

        Returns
        -------
        Any
            Value of the key. None if not found
        """
        MODULE_LOGGER.debug('Receive request to get data for container %s about its %s key', str(
            container_name), str(key_name))
        if container_name in self.__topology:
            if key_name in self.__topology[container_name]:
                MODULE_LOGGER.debug('  -> Found data for container %s: %s', str(
                    container_name), str(self.__topology[container_name][key_name]))
                return self.__topology[container_name][key_name]
        return None

    @property
    def is_valid(self):
        """
        check_schemas Validate schemas for user's input
        """
        MODULE_LOGGER.info('start json schema validation')
        if not schema.validate_cv_inputs(user_json=self.__topology, schema=self.__schema):
            MODULE_LOGGER.error(
                "Invalid configlet input : \n%s\n\n%s", str(self.__topology), self.__schema)
            return False
        return True

    @property
    def ordered_list_containers(self):
        """
        ordered_list_containers List of container from root to the bottom

        Returns
        -------
        list
            List of containers
        """
        result_list = list()
        MODULE_LOGGER.info("Build list of container to create from %s", str(self.__topology))
    
        while(len(result_list) < len(self.__topology)):
            container_added = False
            for container in self.__topology:
                if self.__topology[container][self.__parent_field] == self.__root_name and container not in result_list:
                    container_added = True
                    result_list.append(container)
                if (any(element == self.__topology[container][self.__parent_field] for element in result_list)
                        and container not in result_list):
                    container_added = True
                    result_list.append(container)
            if container_added == False:
                containerWithoutParent = [item for item in self.__topology.keys() if item not in result_list]
                MODULE_LOGGER.warning('Breaking the while loop as the following containers dont have a parent present in the topology %s', str(containerWithoutParent))
                result_list = result_list + containerWithoutParent
                break

        MODULE_LOGGER.info('List of containers to apply on CV: %s', str(result_list))
        return result_list

    def get_parent(self, container_name: str, parent_key: str = FIELD_PARENT_NAME):
        """
        get_parent Expose name of parent container for the given container

        Parameters
        ----------
        container_name : str
            Container Name
        parent_key : str, optional
            Key to use for the parent container name, by default 'parent_container'

        Returns
        -------
        str
            Name of the parent container, None if not found
        """
        return self.__get_container_data(container_name=container_name, key_name=parent_key)

    def get_configlets(self, container_name: str, configlet_key: str = FIELD_CONFIGLETS):
        """
        get_configlets Read and extract list of configlet names for a container

        Parameters
        ----------
        container_name : str
            Name of the container to search configlets
        configlet_key : str, optional
            Key where configlets are saved in inventory, by default 'configlets'

        Returns
        -------
        list
            List of configlet names
        """
        return self.__get_container_data(container_name=container_name, key_name=configlet_key)

    def has_configlets(self, container_name: str, configlet_key: str = FIELD_CONFIGLETS):
        """
        has_configlets Test if container has configlets configured in inventory

        Parameters
        ----------
        container_name : str
            Name of the container
        configlet_key : str, optional
            Field name where configlets are defined, by default 'configlets'

        Returns
        -------
        bool
            True if configlets attached, False if not
        """
        if self.__get_container_data(container_name=container_name, key_name=configlet_key) is None:
            return False
        return True


class CvContainerTools(object):
    """
    CvContainerTools Class to manage container actions for arista.cvp.cv_container module
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None, check_mode: bool = False):
        self.__cvp_client = cv_connection
        self.__ansible = ansible_module
        self.__check_mode = ansible_module.check_mode if ansible_module is not None else check_mode

    #############################################
    #   Private functions
    #############################################

    def __standard_output(self, source: dict):
        """
        __standard_output Filter dict to create a standard output with relevant leys

        Parameters
        ----------
        source : dict
            Original dictionary

        Returns
        -------
        dict
            Standardized dict.
        """
        standard_keys = [FIELD_KEY, FIELD_NAME, FIELD_COUNT_CONTAINERS,
                         FIELD_COUNT_DEVICES, FIELD_PARENT_ID]
        return {k: v for k, v in source.items() if k in standard_keys}

    def __get_attached_configlets(self, container_name: str):
        """
        __get_attached_configlets Extract configlet information for all attached configlets to a container

        Example
        -------

        >>> CvContainerTools._get_attached_configlets(container_name='demo')
        [
            {
                'name': 'test',
                'key': 'container-23243-23234-3423423'
            }
        ]

        Parameters
        ----------
        container_name : str
            Name of the container

        Returns
        -------
        list
            List of dict {key:, name:} of attached configlets
        """
        list_configlet = list()
        info = self.__cvp_client.api.get_configlets_by_container_id(
            c_id=container_name)
        info = {k.lower(): v for k, v in info.items()}
        for attached_configlet in info['configletList']:
            list_configlet.append(
                self.__standard_output(source=attached_configlet))
        return list_configlet

    def __get_all_configlets(self):
        """
        __get_all_configlets Extract information for all configlets

        Example
        -------
        >>> CvContainerTools._get_all_configlets()
        [
            {
                'name': 'test',
                'key': 'container-23243-23234-3423423'
            }
        ]

        Returns
        -------
        list
            List of dict {key:, name:} of attached configlets
        """
        result = list()
        list_configlets = self.__cvp_client.api.get_configlets()
        list_configlets = {k.lower(): v for k, v in list_configlets.items()}
        for configlet in list_configlets['data']:
            result.append(self.__standard_output(source=configlet))
        return result

    def __get_configlet_info(self, configlet_name: str):
        """
        __get_configlet_info Get information of a configlet from CV

        Example

        >>> CvContainerTools._get_configlet_info(configlet_name='test')
        {
            name: 'test',
            key: 'container-sdsaf'
        }

        Parameters
        ----------
        configlet_name : str
            Name of the configlet to get information

        Returns
        -------
        dict
            Configlet information in a filtered maner
        """
        data = self.__cvp_client.api.get_configlet_by_name(name=configlet_name)
        if data is not None:
            return self.__standard_output(source=data)
        return None

    def __configlet_add(self, container: dict, configlets: list, save_topology: bool = True):
        """
        __configlet_add Add a list of configlets to a container on CV

        Only execute an API call to attach a list of configlets to a container.
        All configlets must be provided with information and not only name

        Example
        -------

        >>> CvContainerTools._configlet_add(container='test', configlets=[ {key: 'configlet-xxx-xxx-xxx-xxx', name: 'ASE_DEVICE-ALIASES'} ])
        {
            'success': True,
            'taskIDs': [],
            'container': 'DC3',
            'configlets': ['ASE_DEVICE-ALIASES']
        }

        Parameters
        ----------
        container : dict
            Container information to use in API call. Format: {key:'', name:''}
        configlets : list
            List of configlets information to use in API call
        save_topology : bool, optional
            Send a save-topology, by default True

        Returns
        -------
        dict
            API call result
        """
        configlet_names = list()
        container_name = 'Undefined'
        change_response = CvApiResult(action_name=container_name)

        # Protect aginst non-existing container in check_mode
        if container is not None:
            configlet_names = [entry.get('name')
                               for entry in configlets if entry.get('name')]
            change_response.name = container['name'] + ':' + ':'.join(configlet_names)
            if self.__check_mode:
                change_response.success = True
                change_response.taskIds = ['check_mode']
                change_response.add_entry(
                    container['name'] + ':' + ':'.join(configlet_names))
                MODULE_LOGGER.warning(
                    '[check_mode] - Fake container creation of %s', str(container['name']))
            else:
                try:
                    resp = self.__cvp_client.api.apply_configlets_to_container(
                        app_name="ansible_cv_container",
                        new_configlets=configlets,
                        container=container,
                        create_task=save_topology
                    )
                except CvpApiError as e:
                    message = "Error configuring configlets {} to container {}. Exception: {}".format(str(configlets), str(container), str(e))
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
                else:
                    if 'data' in resp and resp['data']['status'] == 'success':
                        # We assume there is a change as API does not provide information
                        # resp = {'data': {'taskIds': [], 'status': 'success'}}
                        change_response.taskIds = resp['data']['taskIds']
                        change_response.success = True
                        change_response.changed = True

        return change_response

    def __configlet_del(self, container: dict, configlets: list, save_topology: bool = True):
        """
        __configlet_del Remove a list of configlet from container in CV

        Only execute an API call to reemove a list of configlets from a container.
        All configlets must be provided with information and not only name

        Example
        -------

        >>> CvContainerTools._configlet_del(container='test', configlets=[ {key: 'configlet-xxx-xxx-xxx-xxx', name: 'ASE_DEVICE-ALIASES'} ])
        {
            'success': True,
            'taskIDs': [],
            'container': 'DC3',
            'configlets': ['ASE_DEVICE-ALIASES']
        }

        Parameters
        ----------
        container : dict
            Container information to use in API call. Format: {key:'', name:''}
        configlets : list
            List of configlets information to use in API call
        save_topology : bool, optional
            Send a save-topology, by default True

        Returns
        -------
        dict
            API call result
        """
        configlet_names = list()
        configlet_names = [entry.get('name')
                           for entry in configlets if entry.get('name')]
        change_response = CvApiResult(action_name=container['name'] + ':' + ':'.join(configlet_names))
        if self.__check_mode:
            change_response.success = True
            change_response.taskIds = ['check_mode']
            change_response.add_entry(
                container['name'] + ':' + ':'.join(configlet_names))
        else:
            try:
                resp = self.__cvp_client.api.remove_configlets_from_container(
                    app_name="ansible_cv_container",
                    del_configlets=configlets,
                    container=container,
                    create_task=save_topology
                )
            except CvpApiError:
                MODULE_LOGGER.error('Error removing configlets %s from container %s', str(
                    configlets), str(container))
            else:
                if 'data' in resp and resp['data']['status'] == 'success':
                    change_response.taskIds = resp['data']['taskIds']
                    # We assume there is a change as API does not provide information
                    # resp = {'data': {'taskIds': [], 'status': 'success'}}
                    change_response.success = True
                    change_response.changed = True

        return change_response

    #############################################
    #   Generic functions
    #############################################

    def get_container_info(self, container_name: str):
        """
        get_container_info Collect container information from CV

        Extract information from Cloudvision using provisioning/filterTopology call

        Example
        -------

        >>> CvContainerTools.get_container_info(container_name='DC2')
        {
            "key": "container_55effafb-2991-45ca-86e5-bf09d4739248",
            "name": "DC1_L3LEAFS",
            "childContainerCount": 5,
            "childNetElementCount": 0,
            "parentContainerId": "container_614c6678-1769-4acf-9cc1-214728238c2f"
        }

        Parameters
        ----------
        container_name : str
            Name of the searched container

        Returns
        -------
        dict
            A standard dictionary with Key, Name, ParentID, Number of children and devices.
        """
        cv_response = self.__cvp_client.api.get_container_by_name(
            name=container_name)
        MODULE_LOGGER.debug('Get container ID (%s) response from cv for container %s', str(cv_response), str(container_name))
        if cv_response is not None and FIELD_KEY in cv_response:
            container_id = self.__cvp_client.api.get_container_by_name(name=container_name)[
                FIELD_KEY]
            container_facts = self.__cvp_client.api.filter_topology(node_id=container_id)[
                FIELD_TOPOLOGY]
            return self.__standard_output(source=container_facts)
        return None

    def get_container_id(self, container_name: str):
        """
        get_container_id Collect container ID from CV for a given container

        Example
        >>> CvContainerTools.get_container_id(container_name='DC2')
        container_55effafb-2991-45ca-86e5-bf09d4739248

        Parameters
        ----------
        container_name : str
            Name of the container to get ID

        Returns
        -------
        str
            Container ID sent by CV
        """
        container_info = self.__cvp_client.api.get_container_by_name(
            name=container_name)
        if FIELD_KEY in container_info:
            return container_info[FIELD_KEY]
        return None

    #############################################
    #   Boolean & getters functions
    #############################################

    def is_empty(self, container_name: str):
        """
        is_empty Test if container has no child AND no devices attached to it

        Example
        -------
        >>> CvContainerTools.is_empty(container_name='DC2')
        True

        Parameters
        ----------
        container_name : str
            Name of the container to test

        Returns
        -------
        bool
            True if container has no child nor devices
        """
        container = self.get_container_info(container_name=container_name)
        if FIELD_COUNT_CONTAINERS in container and FIELD_COUNT_DEVICES in container:
            if container[FIELD_COUNT_CONTAINERS] == 0 and container[FIELD_COUNT_DEVICES] == 0:
                return True
        return False

    def is_container_exists(self, container_name):
        """
        is_container_exists Test if a given container exists on CV

        Example
        -------
        >>> CvContainerTools.is_container_exists(container_name='DC2')
        True

        Parameters
        ----------
        container_name : [type]
            Name of the container to test

        Returns
        -------
        bool
            True if container exists, False if not
        """
        try:
            cv_data = self.__cvp_client.api.get_container_by_name(name=container_name)
        except (CvpApiError, CvpClientError) as error:
            MODULE_LOGGER.error('Error getting information for container %s: %s', str(container_name), str(error))
            return True
        if cv_data is not None:
            return True
        return False

    #############################################
    #   Public API
    #############################################

    def create_container(self, container: str, parent: str):
        """
        create_container Worker to send container creation API call to CV

        Example
        -------
        >>> CvContainerTools.create_container(container='DC2', parent='DCs')
        {
            "success": True,
            "taskIDs": [],
            "container": 'DC2'
        }

        Parameters
        ----------
        container : str
            Name of the container to create
        parent : str
            Container name where new container will be created

        Returns
        -------
        dict
            Creation status
        """
        resp = dict()
        change_result = CvApiResult(action_name=container)
        if self.is_container_exists(container_name=parent):
            parent_id = self.__cvp_client.api.get_container_by_name(name=parent)[
                FIELD_KEY]
            MODULE_LOGGER.debug('Parent container (%s) for container %s exists', str(parent), str(container))
            if self.is_container_exists(container_name=container) is False:
                if self.__check_mode:
                    change_result.success = True
                    change_result.changed = True
                    change_result.add_entry(container['name'])
                else:
                    try:
                        resp = self.__cvp_client.api.add_container(
                            container_name=container, parent_key=parent_id, parent_name=parent)
                    except CvpApiError:
                        # Add Ansible error management
                        MODULE_LOGGER.error(
                            "Error creating container %s on CV", str(container))
                    else:
                        if resp['data']['status'] == "success":
                            change_result.taskIds = resp['data']['taskIds']
                            change_result.success = True
                            change_result.changed = True
                            change_result.count += 1
        else:
            message = "Parent container ({}) is missing for container {}".format(str(parent), str(container))
            MODULE_LOGGER.error(message)
            self.__ansible.fail_json(msg=message)
        MODULE_LOGGER.info('Container creation result is %s', str(change_result.results))
        return change_result

    def delete_container(self, container: str, parent: str):
        """
        delete_container Worker to send container deletion API call to CV

        Example
        -------
        >>> CvContainerTools.delete_container(container='DC2', parent='DCs')
        {
            "success": True,
            "taskIDs": [],
            "container": 'DC2'
        }

        Parameters
        ----------
        container : str
            Name of the container to delete
        parent : str
            Container name where container will be deleted

        Returns
        -------
        dict
            Deletion status
        """
        resp = dict()
        change_result = CvApiResult(action_name=container)
        if self.is_container_exists(container_name=container) == False:
            message = "Container {} does not exist on CVP - unable to delete it".format(str(container))
            MODULE_LOGGER.error(message)
            self.__ansible.fail_json(msg=message)
        elif self.is_empty(container_name=container) == False:
            message = "Container {} is not empty: either it has child container(s) or device(s) attached on CVP - unable to delete it".format(str(container))
            MODULE_LOGGER.error(message)
            self.__ansible.fail_json(msg=message)
        else:
            parent_id = self.get_container_id(container_name=parent)
            container_id = self.get_container_id(container_name=container)
            # ----------------------------------------------------------------#
            # COMMENT: Check mode does report parial change as there is no    #
            # validation that attached containers would be removed in a       #
            # previous run of this function                                   #
            # ----------------------------------------------------------------#
            if self.__check_mode:
                change_result.success = True
                change_result.add_entry(container['name'])

            else:
                try:
                    resp = self.__cvp_client.api.delete_container(
                        container_name=container, container_key=container_id, parent_key=parent_id, parent_name=parent)
                except CvpApiError as e:
                    # Add Ansible error management
                    message = "Error deleting container {} on CV. Exception: {}".format(str(container), str(e))
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
                else:
                    if resp['data']['status'] == "success":
                        change_result.taskIds = resp['data']['taskIds']
                        change_result.success = True
                        change_result.changed = True
                        change_result.count += 1
        return change_result

    def configlets_attach(self, container: str, configlets: List[str], strict: bool = False):
        """
        configlets_attach Worker to send configlet attach to container API call

        Example
        -------
        >>> CvContainerTools.configlet_attach(container='DC3', configlets=['ASE_DEVICE-ALIASES'])
        {
            'success': True,
            'taskIDs': [],
            'container': 'DC3',
            'configlets': ['ASE_DEVICE-ALIASES']
        }

        Parameters
        ----------
        container : str
            Name of the container
        configlets : List[str]
            List of configlets to attach
        strict : bool, optional
            Remove configlet not listed in configlets var -- NOT SUPPORTED -- , by default False

        Returns
        -------
        dict
            Action result
        """
        container_info = self.get_container_info(container_name=container)
        attach_configlets = list()
        for configlet in configlets:
            data = self.__get_configlet_info(configlet_name=configlet)
            if data is not None:
                attach_configlets.append(data)
        return self.__configlet_add(container=container_info, configlets=attach_configlets)

    def configlets_detach(self, container: str, configlets: List[str], strict: bool = False):
        """
        configlets_attach Worker to send configlet detach from container API call

        Example
        -------
        >>> CvContainerTools.configlets_detach(container='DC3', configlets=['ASE_DEVICE-ALIASES'])
        {
            'success': True,
            'taskIDs': [],
            'container': 'DC3',
            'configlets': ['ASE_DEVICE-ALIASES']
        }

        Parameters
        ----------
        container : str
            Name of the container
        configlets : List[str]
            List of configlets to detach
        strict : bool, optional
            Remove configlet not listed in configlets var -- NOT SUPPORTED -- , by default False

        Returns
        -------
        dict
            Action result
        """
        container_info = self.get_container_info(container_name=container)
        detach_configlets = list()
        for configlet in configlets:
            data = self.__get_configlet_info(configlet_name=configlet)
            if data is not None:
                detach_configlets.append(data)
        return self.__configlet_del(container=container_info, configlets=detach_configlets)

    def build_topology(self, user_topology: ContainerInput, present: bool = True):
        """
        build_topology Class entry point to build container topology on Cloudvision

        Run all actions to provision containers on Cloudvision:
        - Create or delete containers
        - Attach or detach configlets to containers

        Creation or deleation is managed with present flag

        Parameters
        ----------
        user_topology : ContainerInput
            User defined containers topology to build
        present : bool, optional
            Enable creation or deletion process, by default True

        Returns
        -------
        CvAnsibleResponse
            Formatted ansible response message
        """
        response = CvAnsibleResponse()
        container_add_manager = CvManagerResult(builder_name='container_added')
        container_delete_manager = CvManagerResult(
            builder_name='container_deleted')
        configlet_attachment = CvManagerResult(
            builder_name='configlet_attachmenet')

        # Create containers topology in Cloudvision
        if present is True:
            for user_container in user_topology.ordered_list_containers:
                MODULE_LOGGER.info('Start creation process for container %s under %s', str(
                    user_container), str(user_topology.get_parent(container_name=user_container)))
                resp = self.create_container(
                    container=user_container, parent=user_topology.get_parent(container_name=user_container))
                container_add_manager.add_change(resp)

                if user_topology.has_configlets(container_name=user_container):
                    resp = self.configlets_attach(
                        container=user_container, configlets=user_topology.get_configlets(container_name=user_container))
                    configlet_attachment.add_change(resp)

        # Remove containers topology from Cloudvision
        else:
            for user_container in reversed(user_topology.ordered_list_containers):
                MODULE_LOGGER.info('Start deletion process for container %s under %s', str(
                    user_container), str(user_topology.get_parent(container_name=user_container)))
                resp = self.delete_container(
                    container=user_container, parent=user_topology.get_parent(container_name=user_container))
                container_delete_manager.add_change(resp)

        # Create ansible message
        response.add_manager(container_add_manager)
        response.add_manager(container_delete_manager)
        response.add_manager(configlet_attachment)
        MODULE_LOGGER.debug(
            'Container manager is sending result data: %s', str(response))
        return response
