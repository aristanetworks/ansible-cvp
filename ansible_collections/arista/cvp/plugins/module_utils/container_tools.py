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
import pprint
from typing import List
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger  # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import ContainerResponseFields, ModuleOptionValues
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas import v3 as schema
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import validate_json_schema
from ansible_collections.arista.cvp.plugins.module_utils.resources.exceptions import AnsibleCVPApiError, AnsibleCVPNotFoundError, CVPRessource
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info('Start cv_container_v3 module execution')


class ContainerInput(object):
    """
    ContainerInput Object to manage Container Topology in context of arista.cvp collection.
    """

    def __init__(self, user_topology: dict, container_root_name: str = 'Tenant', schema=schema.SCHEMA_CV_CONTAINER):
        self.__topology = user_topology
        self.__parent_field: str = Api.generic.PARENT_CONTAINER_NAME
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
        if (
            container_name in self.__topology
            and key_name in self.__topology[container_name]
        ):
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
        if not validate_json_schema(user_json=self.__topology, schema=self.__schema):
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
        result_list = []
        MODULE_LOGGER.info("Build list of container to create from %s", str(self.__topology))

        while (len(result_list) < len(self.__topology)):
            container_added = False
            for container in self.__topology:
                if self.__topology[container][self.__parent_field] == self.__root_name and container not in result_list:
                    container_added = True
                    result_list.append(container)
                if (any(element == self.__topology[container][self.__parent_field] for element in result_list)
                        and container not in result_list):
                    container_added = True
                    result_list.append(container)
            if not container_added:
                containerWithoutParent = [item for item in self.__topology.keys() if item not in result_list]
                MODULE_LOGGER.warning(
                    'Breaking the while loop as the following containers dont have a parent present in the topology %s',
                    str(containerWithoutParent))
                result_list += containerWithoutParent
                break

        MODULE_LOGGER.info('List of containers to apply on CV: %s', str(result_list))
        return result_list

    def __str__(self):
        return pprint.pformat(self.__topology)

    def get_parent(self, container_name: str, parent_key: str = Api.generic.PARENT_CONTAINER_NAME):
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

    def get_configlets(self, container_name: str, configlet_key: str = Api.generic.CONFIGLETS):
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

    def has_configlets(self, container_name: str, configlet_key: str = Api.generic.CONFIGLETS):
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
        return bool(
            self.__get_container_data(
                container_name=container_name, key_name=configlet_key
            )
        )


class CvContainerTools(object):
    """
    CvContainerTools Class to manage container actions for arista.cvp.cv_container module
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule):
        self.__cvp_client = cv_connection
        self.__ansible = ansible_module
        self.__check_mode = ansible_module.check_mode

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
        standard_keys = [
            Api.generic.KEY,
            Api.generic.NAME,
            Api.container.COUNT_CONTAINER,
            Api.container.COUNT_DEVICE,
            Api.generic.PARENT_CONTAINER_ID
        ]
        return {k: v for k, v in source.items() if k in standard_keys}

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
            Configlet information in a filtered manner
        """
        MODULE_LOGGER.info('Getting information for configlet %s', str(configlet_name))
        data = self.__cvp_client.api.get_configlet_by_name(name=configlet_name)
        if data is not None:
            return self.__standard_output(source=data)
        return None

    def __configlet_add(self, container: dict, configlets: list, save_topology: bool = True):
        # sourcery skip: class-extract-method
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
        configlet_names = []
        container_name = 'Undefined'
        change_response = CvApiResult(action_name=container_name)

        # Protect against non-existing container in check_mode
        if container is not None:
            configlet_names = [entry.get(Api.generic.NAME) for entry in configlets if entry.get(Api.generic.NAME)]
            change_response.name = f'{container[Api.generic.NAME]}:' + ':'.join(configlet_names)

            if self.__check_mode:
                change_response.success = True
                change_response.taskIds = ['check_mode']
                change_response.add_entry(
                    f'{container[Api.generic.NAME]}:' + ':'.join(configlet_names)
                )

                MODULE_LOGGER.warning(
                    '[check_mode] - Fake container creation of %s', str(container[Api.generic.NAME]))
            else:
                try:
                    resp = self.__cvp_client.api.apply_configlets_to_container(
                        app_name="ansible_cv_container",
                        new_configlets=configlets,
                        container=container,
                        create_task=save_topology
                    )
                except CvpApiError as e:
                    message = "Error configuring configlets " + str(configlets) + " to container " + str(container) + ". Exception: " + str(e)
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
                else:
                    if 'data' in resp and resp['data']['status'] == 'success':
                        # We assume there is a change as API does not provide information
                        # resp = {'data': {'taskIds': [], 'status': 'success'}}
                        change_response.taskIds = resp['data'][Api.task.TASK_IDS]
                        change_response.success = True
                        change_response.changed = True
        return change_response

    def __configlet_del(self, container: dict, configlets: list, save_topology: bool = True):
        """
        __configlet_del Remove a list of configlet from container in CV

        Only execute an API call to remove a list of configlets from a container.
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
        configlet_names = []
        configlet_names = [entry.get(Api.generic.NAME)
                           for entry in configlets if entry.get(Api.generic.NAME)]
        change_response = CvApiResult(
            action_name=f'{container[Api.generic.NAME]}:'
            + ':'.join(configlet_names)
        )

        if self.__check_mode:
            change_response.success = True
            change_response.taskIds = ['check_mode']
            change_response.add_entry(
                f'{container[Api.generic.NAME]}:' + ':'.join(configlet_names)
            )

        else:
            try:
                resp = self.__cvp_client.api.remove_configlets_from_container(
                    app_name="ansible_cv_container",
                    del_configlets=configlets,
                    container=container,
                    create_task=save_topology
                )
            except CvpApiError as e:
                message = "Error removing configlets " + str(configlets) + " from container " + str(container) + ". Exception: " + str(e)
                MODULE_LOGGER.error(message)
                self.__ansible.fail_json(msg=message)
            else:
                if 'data' in resp and resp['data']['status'] == 'success':
                    change_response.taskIds = resp['data'][Api.task.TASK_IDS]
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
        if cv_response is not None and Api.generic.KEY in cv_response:
            container_id = cv_response[Api.generic.KEY]
            container_facts = self.__cvp_client.api.filter_topology(node_id=container_id)[Api.container.TOPOLOGY]
            MODULE_LOGGER.debug('Return info for container %s', str(container_name))
            return self.__standard_output(source=container_facts)
        return None

    def get_configlets(self, container_name: str):
        """
        get_configlets Get list of configured configlets for a container

        Example
        -------

        >>> CvContainerTools.get_configlets(container_name='DC2')
        [
            {
                "key": "configlet_267cc5b4-791d-47d4-a79c-000fc0732802",
                "name": "ASE_GLOBAL-ALIASES",
                "reconciled": false,
                "config": "...",
                "user": "ansible",
                "note": "Managed by Ansible",
                "containerCount": 0,
                "netElementCount": 0,
                "dateTimeInLongFormat": 1600694234181,
                "isDefault": "no",
                "isAutoBuilder": "",
                "type": "Static",
                "editable": true,
                "sslConfig": false,
                "visible": true,
                "isDraft": false,
                "typeStudioConfiglet": false
            }
        ]

        Parameters
        ----------
        container_name : str
            Name of the container to lookup

        Returns
        -------
        list
            List of configlets configured on container
        """
        container_id = self.get_container_id(container_name=container_name)
        configlets_and_mappers = self.__cvp_client.api.get_configlets_and_mappers()
        configlets_list = configlets_and_mappers['data'][Api.generic.CONFIGLETS]
        mappers = configlets_and_mappers['data']['configletMappers']
        configlets_configured = []
        MODULE_LOGGER.info('container %s has id %s', str(container_name), str(container_id))
        for mapper in mappers:
            if mapper[Api.mappers.OBJECT_ID] == container_id:
                MODULE_LOGGER.info(
                    'Found 1 mappers for container %s : %s', str(container_name), str(mapper))
                configlets_configured.append(
                    next((x for x in configlets_list if x[Api.generic.KEY] == mapper[Api.configlet.ID])))
        MODULE_LOGGER.debug('List of configlets from CV is: %s', str(
            [x[Api.generic.NAME] for x in configlets_configured]))
        return configlets_configured

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

        Raises
        ------
        AnsibleCVPNotFoundError
            Raised when container is not found in CVP instance
        AnsibleCVPApiError
            Raised when expected API data structure could not be read
        """
        container_info = self.__cvp_client.api.get_container_by_name(
            name=container_name)
        # if [Api.generic.KEY] in container_info:
        #     return container_info[[Api.generic.KEY]]
        # return None
        if not container_info:
            raise AnsibleCVPNotFoundError(container_name, CVPRessource.CONTAINER, "Could not get container ID")
        if Api.generic.KEY not in container_info:
            raise AnsibleCVPApiError(self.__cvp_client.api.get_container_by_name, "Could not get container ID")
        return container_info[Api.generic.KEY]

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
        if (
            Api.container.COUNT_CONTAINER in container
            and Api.container.COUNT_DEVICE in container
            and container[Api.container.COUNT_CONTAINER] == 0
            and container[Api.container.COUNT_DEVICE] == 0
        ):
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
        MODULE_LOGGER.info("Checking if container_name:%s exists", str(container_name))
        try:
            cv_data = self.__cvp_client.api.get_container_by_name(name=container_name)
        except (CvpApiError, CvpClientError) as error:
            message = "Error getting information for container " + \
                str(container_name) + \
                ": " + str(error)
            MODULE_LOGGER.error(message)
            self.__ansible.fail_json(msg=message)
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
        resp = {}
        change_result = CvApiResult(action_name=container)
        MODULE_LOGGER.debug('parent container is set to: %s', str(parent))
        if self.is_container_exists(container_name=parent):
            parent_id = self.__cvp_client.api.get_container_by_name(name=parent)[Api.generic.KEY]
            MODULE_LOGGER.debug('Parent container (%s) for container %s exists', str(parent), str(container))
            if self.is_container_exists(container_name=container) is False:
                if self.__check_mode:
                    change_result.success = True
                    change_result.changed = True
                    change_result.add_entry(container[Api.generic.NAME])
                else:
                    try:
                        resp = self.__cvp_client.api.add_container(
                            container_name=container, parent_key=parent_id, parent_name=parent)
                    except CvpApiError as e:
                        # Add Ansible error management
                        message = "Error creating container " + str(container) + " on CV. Exception: " + str(e)
                        MODULE_LOGGER.error(message)
                        self.__ansible.fail_json(msg=message)
                    else:
                        if resp['data']['status'] == "success":
                            change_result.taskIds = resp['data'][Api.task.TASK_IDS]
                            change_result.success = True
                            change_result.changed = True
                            change_result.count += 1
        else:
            message = "Parent container (" + str(
                parent) + ") is missing for container " + str(container)
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
        resp = {}
        change_result = CvApiResult(action_name=container)
        if self.is_container_exists(container_name=container) is False:
            message = "Unable to delete container " + \
                str(container) + ": container does not exist on CVP"
            MODULE_LOGGER.error(message)
            self.__ansible.fail_json(msg=message)
        elif self.is_empty(container_name=container) is False:
            message = "Unable to delete container " + str(container) + ": container not empty - either it has child container(s) or \
                some device(s) are attached to it on CVP"
            MODULE_LOGGER.error(message)
            self.__ansible.fail_json(msg=message)
        else:
            parent_id = self.get_container_id(container_name=parent)
            container_id = self.get_container_id(container_name=container)
            # ----------------------------------------------------------------#
            # COMMENT: Check mode does report partial change as there is no    #
            # validation that attached containers would be removed in a       #
            # previous run of this function                                   #
            # ----------------------------------------------------------------#
            if self.__check_mode:
                change_result.success = True
                change_result.add_entry(container[Api.generic.NAME])

            else:
                try:
                    resp = self.__cvp_client.api.delete_container(
                        container_name=container, container_key=container_id, parent_key=parent_id, parent_name=parent)
                except CvpApiError as e:
                    # Add Ansible error management
                    message = "Error deleting container " + str(container) + " on CV. Exception: " + str(e)
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
                else:
                    if resp['data']['status'] == "success":
                        change_result.taskIds = resp['data'][Api.task.TASK_IDS]
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
        attach_configlets = []
        for configlet in configlets:
            data = self.__get_configlet_info(configlet_name=configlet)
            if data is not None:
                attach_configlets.append(data)
        return self.__configlet_add(container=container_info, configlets=attach_configlets)

    def configlets_detach(self, container: str, configlets: List[str]):
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

        Returns
        -------
        dict
            Action result
        """
        MODULE_LOGGER.info('Running configlet detach for container %s', str(container))
        container_info = self.get_container_info(container_name=container)
        detach_configlets = []
        for configlet in configlets:
            data = self.__get_configlet_info(configlet_name=configlet[Api.generic.NAME])
            if data is not None:
                detach_configlets.append(data)
        MODULE_LOGGER.info('Sending data to self.__configlet_del: %s', str(detach_configlets))
        return self.__configlet_del(container=container_info, configlets=detach_configlets)

    def build_topology(self, user_topology: ContainerInput, present: bool = True, apply_mode: str = 'loose'):
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
        apply_mode: str, optional
            Define how builder will apply configlets to container: loose (only attach listed configlets) or strict (attach listed configlets, remove others)

        Returns
        -------
        CvAnsibleResponse
            Formatted ansible response message
        """
        response = CvAnsibleResponse()
        container_add_manager = CvManagerResult(
            builder_name=ContainerResponseFields.CONTAINER_ADDED)
        container_delete_manager = CvManagerResult(
            builder_name=ContainerResponseFields.CONTAINER_DELETED)
        cv_configlets_attach = CvManagerResult(
            builder_name=ContainerResponseFields.CONFIGLETS_ATTACHED)
        cv_configlets_detach = CvManagerResult(
            builder_name=ContainerResponseFields.CONFIGLETS_DETACHED, default_success=True)

        try:

            # Create containers topology in Cloudvision
            if present:
                for user_container in user_topology.ordered_list_containers:
                    MODULE_LOGGER.info('Start creation process for container %s under %s', str(
                        user_container), str(user_topology.get_parent(container_name=user_container)))
                    resp = self.create_container(
                        container=user_container, parent=user_topology.get_parent(container_name=user_container))
                    container_add_manager.add_change(resp)

                    if user_topology.has_configlets(container_name=user_container):
                        resp = self.configlets_attach(
                            container=user_container, configlets=user_topology.get_configlets(container_name=user_container))
                        cv_configlets_attach.add_change(resp)
                        if apply_mode == ModuleOptionValues.APPLY_MODE_STRICT:
                            attached_configlets = self.get_configlets(container_name=user_container)
                            configlet_to_remove = [
                                attach_configlet
                                for attach_configlet in attached_configlets
                                if attach_configlet['name']
                                not in user_topology.get_configlets(
                                    container_name=user_container
                                )
                            ]
                            if configlet_to_remove:
                                resp = self.configlets_detach(container=user_container, configlets=configlet_to_remove)
                                cv_configlets_detach.add_change(resp)
                    elif apply_mode == ModuleOptionValues.APPLY_MODE_STRICT:
                        configlet_to_remove = self.get_configlets(container_name=user_container)
                        if len(configlet_to_remove) > 0:
                            resp = self.configlets_detach(container=user_container, configlets=configlet_to_remove)
                            cv_configlets_detach.add_change(resp)

            else:
                for user_container in reversed(user_topology.ordered_list_containers):
                    MODULE_LOGGER.info('Start deletion process for container %s under %s', str(
                        user_container), str(user_topology.get_parent(container_name=user_container)))
                    resp = self.delete_container(
                        container=user_container, parent=user_topology.get_parent(container_name=user_container))
                    container_delete_manager.add_change(resp)

        except (AnsibleCVPApiError, AnsibleCVPNotFoundError) as e:
            self.__ansible.fail_json(msg=str(e))
        # Create ansible message
        response.add_manager(container_add_manager)
        response.add_manager(container_delete_manager)
        response.add_manager(cv_configlets_attach)
        response.add_manager(cv_configlets_detach)
        MODULE_LOGGER.debug(
            'Container manager is sending result data: %s', str(response))
        return response
