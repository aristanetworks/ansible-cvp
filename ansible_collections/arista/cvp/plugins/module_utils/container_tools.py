#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import traceback
import logging
import pprint
from functools import lru_cache
from typing import List
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import ContainerResponseFields, ModuleOptionValues
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas import v3 as schema
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import validate_json_schema
from ansible_collections.arista.cvp.plugins.module_utils.resources.exceptions import AnsibleCVPApiError, AnsibleCVPNotFoundError, CVPRessource
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError, CvpRequestError
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info('Start cv_container_v3 module execution')


# TODO - use f-strings
# pylint: disable=consider-using-f-string


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

    def get_image_bundle(self, container_name: str, bundle_key: str = Api.generic.IMAGE_BUNDLE_NAME):
        """
        get_image_bundle Read and extract image bundle name for a container

        Parameters
        ----------
        container_name : str
            Name of the container to search configlets
        bundle_key : str, optional
            Key where the image bundle name is saved in inventory, by default 'imageBundle'

        Returns
        -------
        String
            The name of the assigned image bundle
        """
        return self.__get_container_data(container_name=container_name, key_name=bundle_key)

    def has_image_bundle(self, container_name: str, bundle_key: str = Api.generic.IMAGE_BUNDLE_NAME):
        """
        get_image_bundle Read and extract image bundle name for a container

        Parameters
        ----------
        container_name : str
            Name of the container to search configlets
        bundle_key : str, optional
            Key where the image bundle name is saved in inventory, by default 'imageBundle'

        Returns
        -------
        bool
            True if an image bundle is assigned, False if not
        """
        return bool(
            self.__get_container_data(container_name=container_name, key_name=bundle_key)
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
        __standard_output Filter dict to create a standard output with relevant keys

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
            Api.generic.PARENT_CONTAINER_ID,
            Api.generic.IMAGE_BUNDLE_NAME
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
                except CvpRequestError as e:
                    if "Forbidden" in str(e):
                        message = "Error configuring configlets. User is unauthorized!"
                    else:
                        message = "Error configuring configlets " + str(configlets) + " to container " + str(container) + ". Exception: " + str(e)
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
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
                        change_response.add_entry(f'{container[Api.generic.NAME]}:' + ':'.join(configlet_names))
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
            except CvpRequestError as e:
                if "Forbidden" in str(e):
                    message = "Error removing configlets. User is unauthorized!"
                else:
                    message = "Error removing configlets " + str(configlets) + " to container " + str(container) + ". Exception: " + str(e)
                MODULE_LOGGER.error(message)
                self.__ansible.fail_json(msg=message)
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
                    change_response.add_entry(f'{container[Api.generic.NAME]}:' + ':'.join(configlet_names))
        return change_response

    def __image_bundle_add(self, container: dict, image_bundle: str):
        """__image_bundle_add Add an image bundle to a container on CV

        Execute the API call to add the image bundle to the container in question
        Args:
            container : dict
                Container information to use in API call. Format: {key:'', name:''}
            image_bundle : str
                The name of the image bundle to be applied
        Returns:
            dict
                API call result
        """

        change_response = CvApiResult(action_name=image_bundle)
        change_response.changed = False

        if container is not None:
            if self.__check_mode:
                if self.__cvp_client.api.get_image_bundle_by_name(image_bundle):
                    change_response.success = True
                    change_response.taskIds = ['check_mode']
                    change_response.add_entry(
                        f'{container[Api.generic.NAME]}: {image_bundle}'
                    )
                else:
                    change_response.success = False
                    message = "Error: The image bundle " + str(image_bundle) + " assigned to container " + str(container[Api.generic.NAME]) + " does not exist."
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)

            else:
                # Get the assigned image bundle information
                try:
                    MODULE_LOGGER.info("Getting the image bundle info for bundle: %s", str(image_bundle))
                    assigned_image_facts = self.__cvp_client.api.get_image_bundle_by_name(image_bundle)
                except CvpApiError as e:
                    message = "Error retrieving image bundle info for: " + str(image_bundle) + ". Error was: " + str(e)
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
                # Get the current image bundle
                try:
                    MODULE_LOGGER.info("Checking if container has an image bundle already")
                    current_image_facts = self.__cvp_client.api.get_image_bundle_by_container_id(container[Api.generic.KEY])
                    pass
                # TODO - remove variable e
                # pylint: disable=unused-variable
                except CvpApiError as e:
                    message = "Error retrieving image bundle info for container: " + str(container[Api.generic.KEY])
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)

                if assigned_image_facts is not None:
                    # We have a valid image bundle to assign
                    if len(current_image_facts['imageBundleList']) != 0 and\
                            current_image_facts['imageBundleList'][0][Api.generic.KEY] == assigned_image_facts['id']:
                        # Check that the current image bundle and the assigned image bundle are the same
                        MODULE_LOGGER.info("Nothing to do. Image bundle already assigned to %s container", str(container[Api.generic.NAME]))
                    else:
                        MODULE_LOGGER.debug("Image bundle %s has key %s", str(image_bundle), str(assigned_image_facts['id']))
                        MODULE_LOGGER.info("Applying %s to container %s", str(image_bundle), str(container[Api.generic.NAME]))
                        try:
                            resp = self.__cvp_client.api.apply_image_to_element(
                                assigned_image_facts,
                                container,
                                container[Api.generic.NAME],
                                'container'
                            )
                        except CvpRequestError as e:
                            if "Forbidden" in str(e):
                                message = "Error applying bundle to container. User is unauthorized!"
                            else:
                                message = "Error applying bundle to container " + str(container[Api.generic.NAME]) + ". Exception: " + str(e)
                            MODULE_LOGGER.error(message)
                            self.__ansible.fail_json(msg=message)
                        except CvpApiError as catch_error:
                            MODULE_LOGGER.error('Error applying bundle to device: %s', str(catch_error))
                            self.__ansible.fail_json(msg='Error applying bundle to container' + container[Api.generic.NAME] + ': ' + catch_error)
                        else:
                            if resp['data']['status'] == 'success':
                                change_response.changed = True
                                change_response.success = True
                                change_response.taskIds = resp['data'][Api.task.TASK_IDS]
                                change_response.add_entry(f'{container[Api.generic.NAME]}: {image_bundle}')
                else:
                    message = "Error - assigned image bundle: " + str(image_bundle) + "does not exist."
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)

        return change_response

    def __image_bundle_del(self, container: dict):
        """__image_bundle_del Delete an image bundle from a container on CV

        Execute the API call to delete the image bundle to the container in question
        Args:
            container : dict
                Container information to use in API call. Format: {key:'', name:''}
        Returns:
            dict
                API call result
        """

        container["imageBundle"] = "" if container["imageBundle"] is None else container["imageBundle"]
        change_response = CvApiResult(action_name=container["imageBundle"])
        change_response.changed = False

        if container is not None:
            if self.__check_mode:
                change_response.success = True
                change_response.taskIds = ['check_mode']
                change_response.add_entry(
                    f'{container[Api.generic.NAME]}: Image removed'
                )

            else:
                # Get the assigned image bundle information
                try:
                    MODULE_LOGGER.info("Checking if container has an image bundle already")
                    current_image_facts = self.__cvp_client.api.get_image_bundle_by_container_id(container[Api.generic.KEY])
                    pass
                except CvpApiError as e:
                    message = "Error retrieving image bundle info for container: " + str(container[Api.generic.KEY]) + ". Error was: " + str(e)
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)

                if len(current_image_facts['imageBundleList']) != 0:
                    MODULE_LOGGER.debug('Remove image %s from container %s', str(current_image_facts), str(container))
                    try:
                        resp = self.__cvp_client.api.remove_image_from_element(
                            current_image_facts['imageBundleList'][0],
                            container,
                            container[Api.generic.NAME],
                            'container'
                        )
                    except CvpRequestError as e:
                        if "Forbidden" in str(e):
                            message = "Error removing bundle from container. User is unauthorized!"
                        else:
                            message = "Error removing bundle from container " + str(container[Api.generic.NAME]) + ". Exception: " + str(e)
                        MODULE_LOGGER.error(message)
                        self.__ansible.fail_json(msg=message)
                    except CvpApiError as catch_error:
                        MODULE_LOGGER.error('Error removing bundle from container: %s', str(catch_error))
                        self.__ansible.fail_json(msg='Error removing bundle from container: ' + container[Api.generic.NAME] + ': ' + catch_error)
                    else:
                        if resp['data']['status'] == 'success':
                            change_response.changed = True
                            change_response.success = True
                            change_response.taskIds = resp['data'][Api.task.TASK_IDS]
                            change_response.add_entry(f'{container[Api.generic.NAME]}: Image removed')
                else:
                    # No image assigned, so nothing to do
                    change_response.success = True
                    change_response.taskIds = []

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
            "parentContainerId": "container_614c6678-1769-4acf-9cc1-214728238c2f",
            "imageBundle": "top_level_container"
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
            MODULE_LOGGER.debug('Collecting assigned image bundle name')
            assigned_bundle = self.__cvp_client.api.get_image_bundle_by_container_id(container_id)
            MODULE_LOGGER.debug('Retrieved the bundle information: %s', str(assigned_bundle))
            if len(assigned_bundle['imageBundleList']) == 1:
                container_facts[Api.generic.IMAGE_BUNDLE_NAME] = assigned_bundle['imageBundleList'][0][Api.generic.NAME]
            elif len(assigned_bundle['imageBundleList']) == 0:
                container_facts[Api.generic.IMAGE_BUNDLE_NAME] = None
            else:
                MODULE_LOGGER.error('Image bundle list is larger than expected (%d): %s', int(assigned_bundle['imageBundleList']), str(assigned_bundle))
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

    @lru_cache
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

    @lru_cache
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
                    change_result.add_entry(container)
                else:
                    try:
                        resp = self.__cvp_client.api.add_container(
                            container_name=container, parent_key=parent_id, parent_name=parent)
                    except CvpRequestError as e:
                        if "Forbidden" in str(e):
                            message = "Error creating container. User is unauthorized!"
                        else:
                            message = "Error creating container " + str(container) + ". Exception: " + str(e)
                        MODULE_LOGGER.error(message)
                        self.__ansible.fail_json(msg=message)
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

                            # Invalidate the cached result of is_container_exists
                            self.is_container_exists.cache_clear()

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
                except CvpRequestError as e:
                    if "Forbidden" in str(e):
                        message = "Error deleting container. User is unauthorized!"
                    else:
                        message = "Error deleting container " + str(container) + ". Exception: " + str(e)
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
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

                        # Invalidate the cached result of is_container_exists
                        self.is_container_exists.cache_clear()

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

    def image_bundle_attach(self, container: str, image_name: str):
        """
        image_bundle_attach - send bundle attach to the the element API call

        Example
        -------
        >>> CvContainerTools.image_bundle_attach(container='Test123', image_name='top_level_bundle')
        {
            'success': True,
            'taskIDs': [],
            'container': 'Test123',
            'imageBundle': 'top_level_bundle
        }

        Parameters
        ----------
        container: str
            Name of the container
        image_name: str
            Name of the image bundle to assign

        Returns
        -------
        dict
            Action result
        """
        container_info = self.get_container_info(container_name=container)
        MODULE_LOGGER.debug("Attempting to apply image bundle %s to container %s", str(image_name), str(container))
        return self.__image_bundle_add(container=container_info, image_bundle=image_name)

    def image_bundle_detach(self, container: str):
        """
        image_bundle_detach - send bundle detach to the the element API call

        Example
        -------
        >>> CvContainerTools.image_bundle_detach(container='Test123')
        {
            'success': True,
            'taskIDs': [],
            'container': 'Test123',
            'imageBundle': 'top_level_bundle
        }

        Parameters
        ----------
        container: str
            Name of the container

        Returns
        -------
        dict
            Action result
        """
        container_info = self.get_container_info(container_name=container)
        MODULE_LOGGER.debug("Attampting to remove image bundle from %s", str(container))
        return self.__image_bundle_del(container=container_info)

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
            builder_name=ContainerResponseFields.CONFIGLETS_DETACHED)
        cv_image_bundle_attach = CvManagerResult(
            builder_name=ContainerResponseFields.BUNDLE_ATTACHED)
        cv_image_bundle_detach = CvManagerResult(
            builder_name=ContainerResponseFields.BUNDLE_DETACHED)
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

                    if user_topology.has_image_bundle(container_name=user_container):
                        MODULE_LOGGER.debug('%s container has an image bundle assigned', str(user_container))
                        resp = self.image_bundle_attach(
                            container=user_container, image_name=user_topology.get_image_bundle(container_name=user_container))
                        cv_image_bundle_attach.add_change(resp)
                    elif apply_mode == ModuleOptionValues.APPLY_MODE_STRICT:
                        resp = self.image_bundle_detach(container=user_container)
                        cv_image_bundle_detach.add_change(resp)

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
        response.add_manager(cv_image_bundle_attach)
        response.add_manager(cv_image_bundle_detach)
        MODULE_LOGGER.debug(
            'Container manager is sending result data: %s', str(response))
        return response
