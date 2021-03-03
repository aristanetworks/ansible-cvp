#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=bare-except
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import logging
import traceback
from typing import List, Any
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.tools as tools
import ansible_collections.arista.cvp.plugins.module_utils.schema as schema
from ansible_collections.arista.cvp.plugins.module_utils.cv_objects import CvContainerTopology
from ansible.module_utils.basic import AnsibleModule
try:
    from cvprac.cvp_client import CvpClient
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Ansible module preparation
ansible_module: AnsibleModule
CV_CONTAINER_MODE = ['merge', 'delete']
container_topology: CvContainerTopology

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_container_v3')
MODULE_LOGGER.info('Start cv_container_v3 module execution')

# CONSTANTS
MODE_PRESENT = 'present'
MODE_ABSENT = 'absent'

# ------------------------------------------------------------ #
#               Tooling for containers                         #
# ------------------------------------------------------------ #

def is_container_exist(cv_connection: CvpClient(), container: str):
    """
    is_container_exist Test if container exists on Cloudvision

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler
    container : str
        Container name to check

    Returns
    -------
    bool
        True if exists, False if not present
    """
    try:
        if cv_connection.api.get_container_by_name(name=container) is not None:
            return True
    except:  # noqa E722
        MODULE_LOGGER.error("Error getting container %s on CV", str(container))
        return False
    return False


def is_container_empty(cv_connection: CvpClient(), container: str):
    """
    is_container_empty Test if container has subcontainer or device attached to it

    Test if container has something attached to it or if it is ready to be deleted

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler
    container : str
        Container name to check

    Returns
    -------
    bool
        True if container is empty, False in any other case
    """
    container_id = container_get_id(cv_connection=cv_connection, container=container)
    container_info = cv_connection.api.filter_topology(node_id=container_id)['topology']
    MODULE_LOGGER.debug('Get container information from CV for %s (%s): %s', str(container), str(container_id), str(container_info))
    if container_info['childContainerCount'] == 0 and container_info['childNetElementCount'] == 0:
        return True
    return False


def container_get_root(cv_connection: CvpClient):
    """
    container_get_root Helper to get name of root container

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler

    Returns
    -------
    str
        Name of the root container - usually Tenants
    """
    cv_result = dict()
    try:
        cv_result = cv_connection.api.filter_topology(node_id='root')
    except:  # noqa E722  # noqa E722
        MODULE_LOGGER.error('Error to get topology from CV for node ROOT/TENANT')
        return None
    else:
        return cv_result['topology']['name']


def container_get_id(cv_connection: CvpClient(), container: str):
    """
    container_get_id Get container KEY from Cloudvision from its name

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler
    container : str
        Container name

    Returns
    -------
    str
        KEY id of the container, None if none of more than one result
    """
    result = dict()
    MODULE_LOGGER.debug("Get ID for container %s", str(container))
    try:
        result = cv_connection.api.get_container_by_name(name=container)
    except:  # noqa E722
        MODULE_LOGGER.error("Error getting container %s on CV", str(container))

    if result is not None:
        return result['key']
    return None


def list_containers_from_top(container_list, container_root_name: str, parent_field: str = 'parent_container'):
    """
    list_container_from_top Create an ordered list of containers from top to bottom

    Example
    -------

    >>> list_containers_from_top(container_list=user_topology, container_root_name=root_container_name)
     ['DC2', 'Leafs', 'Spines', 'POD01']

    Parameters
    ----------
    container_list : dict
        Dictionary of a topolgoy
    container_root_name : str
        Name of the root container
    parent_field : str
        Name of the field to look for parent container

    Returns
    -------
    list
        List of container ordered from TOP to BOTTOM
    """
    result_list = list()
    MODULE_LOGGER.debug("Build list of container to create from %s", str(container_list))
    while(len(result_list) < len(container_list)):
        MODULE_LOGGER.debug("Built list is : %s", str(result_list))
        for container in container_list:
            if container_list[container][parent_field] == container_root_name:
                result_list.append(container)
            if (any(element == container_list[container][parent_field] for element in result_list)
                and container not in result_list):
                result_list.append(container)
    return result_list


# ------------------------------------------------------------ #
#               Tooling for configlets                         #
# ------------------------------------------------------------ #

def is_configlet_exists(cv_connection: CvpClient(), configlet: str):
    try:
        if cv_connection.api.get_configlet_by_name(name=configlet) is not None:
            return True
    except:  # noqa E722
        MODULE_LOGGER.error("Error getting configlet %s on CV", str(configlet))
        return False
    return False


def configlet_get_id(cv_connection: CvpClient(), configlet: str):
    try:
        data = cv_connection.api.get_configlet_by_name(name=configlet)
    except:  # noqa E722
        MODULE_LOGGER.error("Error getting configlet %s on CV", str(configlet))
        return None
    else:
        if data is not None:
            return data['key']
    return None


def configlets_get_mapping(cv_connection: CvpClient()):
    data = dict()
    try:
        data = cv_connection.api.get_configlets_and_mappers()['data']
    except:
        MODULE_LOGGER.error('Error getting configlets & mappers')
    else:
        for mapper_index in range(len(data['configletMappers'])):
            for configlet in data['configlets']:
                if configlet['key'] == data['configletMappers'][mapper_index]['configletId']:
                    data['configletMappers'][mapper_index]['configletName'] = configlet['name']
        return data
    return None


# ------------------------------------------------------------ #
#               API Action -- Require to return JSON result    #
# ------------------------------------------------------------ #

def container_create(cv_connection: CvpClient(), container: str, parent: str):
    """
    container_create Action to create a single container on Cloudvision

    Create a container in Cloudvision attached to parent_container

    Example
    -------

    >>> container_create(cv_connection, container=TEST, parent=Tenant)
    {
        sucess: True,
        taskIDs: [taskIds],
        container: "container"
    }

    Parameters
    ----------
    cv_connection : CvpClient
        Cvprac connection
    container : str
        Container name
    parent : str
        Parent Container name

    Returns
    -------
    dict
        Response to be added in ansible
    """
    resp = dict()
    taskIds = 'UNSET'
    if ansible_module.check_mode:
        MODULE_LOGGER.debug(
            '[check mode] - Create container %s under %s', str(container), str(parent))
        return {"success": True, "taskIDs": taskIds, "container": container}
    elif container_topology.is_container_exist(container_name=parent):
        parent_id = container_topology.get_container_id(container_name=parent)
        try:
            resp = cv_connection.api.add_container(container_name=container,
                                                   parent_name=parent,
                                                   parent_key=parent_id)
            MODULE_LOGGER.debug('Container %s has been created on CV under %s', str(container), str(parent))
        except:  # noqa E722
            MODULE_LOGGER.error("Error creating container %s on CV", str(container))
        else:
            if resp['data']['status'] == "success":
                taskIds = resp['data']['taskIds']
        MODULE_LOGGER.debug('Start data refresh from CV')
        container_topology.refresh_data()
        MODULE_LOGGER.debug('End data refresh from CV')
        # Return structured data for a container creation
        return {"success": True, "taskIDs": taskIds, "container": container}
    else:
        MODULE_LOGGER.debug('Parent container (%s) is missing for container %s', str(parent), str(container))
    return {"success": False, "taskIDs": taskIds, "container": container}


def container_delete(cv_connection: CvpClient(), container: str, parent: str):
    """
    container_delete Action to delete a single container from Cloudvision

    Delete a container in Cloudvision

    Example
    -------

    >>> container_delete(cv_connection, container=TEST, parent=Tenant)
    {
        sucess: True,
        taskIDs: [taskIds],
        container: "container"
    }

    Parameters
    ----------
    cv_connection : CvpClient
        Cvprac connection
    container : str
        Container name
    parent : str
        Parent Container name

    Returns
    -------
    dict
        Response to be added in ansible
    """
    resp = dict()
    taskIds = 'UNSET'
    if ansible_module.check_mode:
        # TODO: Add additional constraints to reflect CV logic
        MODULE_LOGGER.debug('[check mode] - Delete container %s under %s',
                            str(container), str(parent))
        return {"success": True, "taskIDs": taskIds, "container": container}
    elif (container_topology.is_container_exist(container_name=parent)
          and container_topology.is_container_exist(containcontainer_nameer=container)):
        parent_id = container_topology.get_container_id(container_name=parent)
        container_id = container_topology.get_container_id(
            concontainer_nametainer=container)
        if container_topology.is_container_empty(container_name=container):
            try:
                resp = cv_connection.api.delete_container(container_name=container,
                                                          container_key=container_id,
                                                          parent_name=parent,
                                                          parent_key=parent_id)
                MODULE_LOGGER.debug('Container %s has been deleted from CV under %s', str(container), str(parent))
            except:  # noqa E722
                MODULE_LOGGER.error("Error deleting container %s on CV", str(container))
            else:
                if resp['data']['status'] == "success":
                    taskIds = resp['data']['taskIds']
            MODULE_LOGGER.debug('Start data refresh from CV')
            container_topology.refresh_data()
            MODULE_LOGGER.debug('End data refresh from CV')
            # Return structured data for a container creation
            return {"success": True, "taskIDs": taskIds, "container": container}
        else:
            MODULE_LOGGER.warning('Container (%s) is not empty, cannot delete it', str(container))
    else:
        MODULE_LOGGER.debug('Container (%s) or parent container (%s) is missing', str(container), str(parent))
    return {"success": False, "taskIDs": taskIds, "container": container}


def container_attach_configlets(cv_connection: CvpClient(), container: str, configlets: Any, save_topology: bool = True):
    """
    container_attach_configlets Action to map configlet(s) to container

    Map one or many configlets to a container and provides generated Task IDs

    Example
    -------

    >>> container_attach_configlets(cv_connection=cv_connection, container=container, configlets=configlet_list_to_add)
    {
        "success": True,
        "taskIDs": [taskIds],
        "container": "container",
        "configlets": ["configlets"]
    }

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler
    container : str
        Container name to use to map configlets
    configlets : list
        List of configlets dict in {key:, name:} format
    save_topology : bool, optional
        Save topology and return TaskIds, by default True

    Returns
    -------
    dict
        Results from Cloudvision.
    """
    resp = dict()
    taskIds = ['UNSET']
    if ansible_module.check_mode:
        # TODO: Add additional constraints to reflect CV logic
        MODULE_LOGGER.debug('[check mode] - Attach configlets %s to %s', str(configlets), str(container))
        return {"success": True, "taskIDs": taskIds, "container": container, 'configlets': configlets}
    elif is_container_exist(cv_connection=cv_connection, container=container):
        container_id = container_get_id(cv_connection=cv_connection, container=container)
        container_info = {'name': container, 'key': container_id}
        try:
            resp = cv_connection.api.apply_configlets_to_container(app_name="ansible_cv_container",
                                                                   new_configlets=configlets,
                                                                   container=container_info,
                                                                   create_task=save_topology)
        except:
            MODULE_LOGGER.error("Error attaching configlets %s to container %s on CV", str(configlets), str(container))
        else:
            if 'data' in resp and resp['data']['status'] == 'success':
                taskIds = resp['data']['taskIds']
                MODULE_LOGGER.info("Configlets %s attached to container %s on CV", str(configlets), str(container))
        return {"success": True, "taskIDs": taskIds, "container": container, 'configlets': configlets}
    else:
        MODULE_LOGGER.debug('Container (%s) is missing', str(container))
    return {"success": False, "taskIDs": taskIds, "container": container, 'configlets': configlets}


def container_detach_configlets(cv_connection: CvpClient(), container: str, configlets: Any, save_topology: bool = True):
    """
    container_detach_configlets Action to unmap configlet(s) to container

    Unmap one or many configlets to a container and provides generated Task IDs

    Example
    -------

    >>> container_detach_configlets(cv_connection=cv_connection, container=container, configlets=configlet_list_to_add)
    {
        "success": True,
        "taskIDs": [taskIds],
        "container": "container",
        "configlets": ["configlets"]
    }

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler
    container : str
        Container name to use to map configlets
    configlets : list
        List of configlets dict in {key:, name:} format
    save_topology : bool, optional
        Save topology and return TaskIds, by default True

    Returns
    -------
    dict
        Results from Cloudvision.
    """
    resp = dict()
    taskIds = ['UNSET']
    if ansible_module.check_mode:
        # TODO: Add additional constraints to reflect CV logic
        MODULE_LOGGER.debug('[check mode] - detach configlets %s to %s', str(configlets), str(container))
        return {"success": True, "taskIDs": taskIds, "container": container, 'configlets': configlets}
    elif is_container_exist(cv_connection=cv_connection, container=container):
        container_id = container_get_id(cv_connection=cv_connection, container=container)
        container_info = {'name': container, 'key': container_id}
        try:
            resp = cv_connection.api.remove_configlets_from_container(app_name="ansible_cv_container",
                                                                      del_configlets=configlets,
                                                                      container=container_info,
                                                                      create_task=save_topology)
        except:
            MODULE_LOGGER.error("Error detaching configlets %s to container %s on CV", str(configlets), str(container))
        else:
            if 'data' in resp and resp['data']['status'] == 'success':
                taskIds = resp['data']['taskIds']
                MODULE_LOGGER.info("Configlets %s detached from container %s on CV", str(configlets), str(container))
        return {"success": True, "taskIDs": taskIds, "container": container, 'configlets': configlets}
    else:
        MODULE_LOGGER.debug('Container (%s) is missing', str(container))
    return {"success": False, "taskIDs": taskIds, "container": container, 'configlets': configlets}


def container_move_devices(cv_connection: CvpClient(), container: str, device: str):
    resp = dict()
    taskids = ['UNSET']
    if ansible_module.check_mode:
        # TODO: Add additional constraints to reflect CV logic
        MODULE_LOGGER.debug(
            '[check mode] - move device %s to %s', str(device), str(container))


# ------------------------------------------------------------ #
#               CONTAINER MANAGERS -- Execute API calls        #
# ------------------------------------------------------------ #

def manager_containers_create(cv_connection: CvpClient(), user_topology: Any):
    """
    manager_containers_create Create new containers from user's intended topology

    Example
    -------

    >>> manager_containers_create()
    {
        "containers_created": containers_created_counter,
        "containers_created_list": ["containers_created"]
    }

    Returns
    -------
    dict
        A structured data with number of new containers and list of new containers created
    """
    # Counter of container's created
    containers_created_counter: int = 0
    # List of created containers
    containers_created = list()

    # Get name on root container in CV topology
    # root_container_name = container_get_root(cv_connection=cv_connection)
    root_container_name = container_topology.root_container['name']
    MODULE_LOGGER.debug("Container root name is set to %s", root_container_name)

    if ansible_module.check_mode:
        MODULE_LOGGER.info("Running creation process in check_mode")

    # Build a tree of containers expected to be configured on CVP
    user_containers_topology_ordered_list = list_containers_from_top(container_list=user_topology, container_root_name=root_container_name)

    # --- Container creation process
    MODULE_LOGGER.info('Start to create containers for %s', str(user_containers_topology_ordered_list))
    for user_container_name in user_containers_topology_ordered_list:
        # Validate parent container exists
        # if (is_container_exist(cv_connection=cv_connection,container=user_topology[user_container_name]['parent_container'])
        if (container_topology.is_container_exist(container_name=user_topology[user_container_name]['parent_container'])
            or ansible_module.check_mode):
            # Create missing containers
            # if is_container_exist(cv_connection=cv_connection, container=user_container_name) is False:
            if container_topology.is_container_exist(container_name=user_container_name) is False:
                action_result = container_create(cv_connection=cv_connection,
                                                 container=user_container_name,
                                                 parent=user_topology[user_container_name]["parent_container"])
                MODULE_LOGGER.debug('  - Containers creation manager received %s when creating container %s', str(action_result), str(user_container_name))
                if action_result["success"] is True:
                    containers_created_counter += 1
                    containers_created.append(user_container_name)
                    container_topology.refresh_data()
    MODULE_LOGGER.debug('End of creation loop with: %s', str(containers_created))
    return {"containers_created": containers_created_counter, "containers_created_list": containers_created}


def manager_container_delete(cv_connection: CvpClient(), user_topology: Any):
    """
    manager_container_delete Delete containers from user's intended topology

    Example
    -------

    >>> manager_container_delete()
    {
        "containers_deleted": containers_created_counter,
        "containers_deleted_list": ["containers_created"]
    }

    Returns
    -------
    dict
        A structured data with number of new containers and list of new containers created
    """
    # Counter of container's created
    containers_deleted_counter: int = 0
    # List of created containers
    containers_deleted = list()
    # Get name on root container in CV topology
    root_container_name = container_get_root(cv_connection=cv_connection)
    MODULE_LOGGER.debug("Container root name is set to %s", root_container_name)
    if ansible_module.check_mode:
        MODULE_LOGGER.info("Running deletion process in check_mode")

    # Build a tree of containers expected to be removed from CVP
    user_containers_topology_ordered_list = list_containers_from_top(container_list=user_topology, container_root_name=root_container_name)
    for user_container_name in reversed(user_containers_topology_ordered_list):
        if is_container_exist(cv_connection=cv_connection, container=user_container_name):
            action_result = container_delete(cv_connection=cv_connection,
                                             container=user_container_name,
                                             parent=user_topology[user_container_name]["parent_container"])
            MODULE_LOGGER.debug('  - Containers deletion manager received %s when deleting container %s', str(action_result), str(user_container_name))
            if action_result["success"] is True:
                containers_deleted_counter += 1
                containers_deleted.append(user_container_name)
    MODULE_LOGGER.debug('End of creation loop with: %s', str(containers_deleted))
    return {"containers_deleted": containers_deleted_counter, "containers_deleted_list": containers_deleted}


def manager_container_configlets(cv_connection: CvpClient(), user_topology: Any, configlet_filter: List[str] = ['all'], filter_mode: str = 'loose', state: str = 'present'):  # noqa W0102
    """
    manager_container_configlets Manage configlets on containers

    Addition process: state=present

    - if configlet from intended match filter: configlet is attached
    - if configlet from intended does not match filter: configlet is
    ignored
    - if configlet is attached, not in intended and match filter: configlet is removed
    - if configlet is attached, in intended and match filter: configlet is kept
    - configlet_filter = ['none'] filtering is ignored and configlet is
    attached


    Deletion process: state=delete

    - if configlet is not part of intended and filter is not matched: we do
    not remove it
    - if configlet is not part of intended and filter is matched: we
    detach configlet.
    - configlet_filter = ['none'], configlet is ignored and not detached

    Example
    -------

    >>> manager_container_configlets(cv_connection=ansible_module.client, user_topology=ansible_module.params['topology'])
    {
        "configlet_add":
            "configlet_attached": 2,
            "configlet_attached_list": [
                "configlets"
            ]
        }
    }

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler
    user_topology : dict
        Container topology to provision on Cloudvision
    configlet_filter : List[str], optional
        Configlet filter to test configlets, by default ['all']
    filter_mode : str, optional
        Filter mode: loose or strict, by default 'loose'

    Returns
    -------
    list
        List of Cloudvision results
    """
    response = dict()
    for container in user_topology:
        # List of configlets to attach to container
        configlet_list_to_add = list()
        # List of confilgets to detach from container
        configlet_list_to_remove = list()
        # List of intended configlets for container
        configlet_intended = list()
        if 'configlets' in user_topology[container]:
            configlet_intended = user_topology[container]['configlets']
        # Container ID from Cloudvision
        container_id = container_get_id(cv_connection=cv_connection, container=container)
        # Add existing configlets matching filter.
        try:
            configlet_attached_list = cv_connection.api.get_configlets_by_container_id(c_id=container_id)['configletList']
        except CvpApiError:
            # Handle error if container ID is incorrect
            error_message = 'Error getting configlets for container {}'.format(str(container))
            MODULE_LOGGER.error(error_message)
            ansible_module.fail_json(msg=error_message)

        # Manage configlets attached to container in Cloudvision
        for configlet in configlet_attached_list:
            if tools.match_filter(input=configlet['name'], filter=configlet_filter):
                if configlet['name'] in configlet_intended and state == MODE_PRESENT:
                    if state == MODE_PRESENT:
                        configlet_list_to_add.append({"name": configlet['name'], "key": configlet['key']})
                    if state == MODE_ABSENT:
                        configlet_list_to_remove.append({"name": configlet['name'], "key": configlet['key']})
                else:
                    configlet_list_to_remove.append({"name": configlet['name'], "key": configlet['key']})

        # Add new configlets matching filter.
        if 'configlets' in user_topology[container]:
            for configlet in user_topology[container]['configlets']:
                if tools.match_filter(input=configlet, filter=configlet_filter):
                    configlet_id = configlet_get_id(cv_connection=cv_connection, configlet=configlet)
                    if configlet_id is not None and not any(configlet != entry['name'] for entry in configlet_list_to_add):
                        if state == MODE_PRESENT:
                            configlet_list_to_add.append({"name": configlet, "key": configlet_id})
                        else:
                            configlet_list_to_remove.append({"name": configlet, "key": configlet_id})

            # Apply changes on Cloudvision
            # Attach configlets
            if len(configlet_list_to_add) > 0:
                apply_configlets = container_attach_configlets(cv_connection=cv_connection, container=container, configlets=configlet_list_to_add)
                MODULE_LOGGER.debug('  - Containers configlet manager received %s when applying configlets %s', str(apply_configlets), str(configlet_list_to_add))
                if apply_configlets["success"] is True:
                    response['configlet_add'] = {"configlet_attached": len(apply_configlets["configlets"]), "configlet_attached_list": apply_configlets["configlets"]}

            # detach configlets
            if len(configlet_list_to_remove) > 0:
                apply_configlets = container_detach_configlets(cv_connection=cv_connection, container=container, configlets=configlet_list_to_remove)
                MODULE_LOGGER.debug('  - Containers configlet manager received %s when applying configlets %s',
                                    str(apply_configlets), str(configlet_list_to_add))
                if apply_configlets["success"] is True:
                    response['configlet_detach'] = {"configlet_detached": len(apply_configlets["configlets"]),
                                                    "configlet_detached_list": apply_configlets["configlets"]}

    return response


# ------------------------------------------------------------ #
#               MAIN section -- starting point                 #
# ------------------------------------------------------------ #

if __name__ == '__main__':
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        topology=dict(type='dict', required=True),            # Topology to configure on CV side.
        cvp_facts=dict(type='dict', required=False, ),          # Facts from cv_facts module.
        configlet_filter=dict(type='list', default='none'),   # Filter to protect configlets to be detached
        mode=dict(type='str',
                  required=False,
                  default='merge',
                  choices=CV_CONTAINER_MODE,
                  removed_in_version='3.1.0',),
        state=dict(type='str', required=False, default='present')
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(argument_spec=argument_spec,
                                   supports_check_mode=True)
    # Instantiate ansible results
    result = dict(changed=False, data={})
    result['data']['taskIds'] = list()
    result['data']['tasks'] = list()

    if ansible_module.params['mode'] in ['delete']:
        ansible_module.params['state'] = MODE_ABSENT
    else:
        ansible_module.params['state'] = MODE_PRESENT

    # Test all libs are correctly installed
    if HAS_CVPRAC is False:
        ansible_module.fail_json(msg='cvprac required for this module. Please install using pip install cvprac')

    if not schema.HAS_JSONSCHEMA:
        ansible_module.fail_json(msg="JSONSCHEMA is required. Please install using pip install jsonschema")

    # Test user input against schema definition
    if not schema.validate_cv_inputs(user_json=ansible_module.params['topology'], schema=schema.SCHEMA_CV_CONTAINER):
        MODULE_LOGGER.error("Invalid configlet input : %s", str(ansible_module.params['configlets']))
        ansible_module.fail_json(msg='Container input data are not compliant with module.')

    # Create CVPRAC client
    ansible_module.client = tools_cv.cv_connect(ansible_module)

    # Start CV Container Topology client
    container_topology = CvContainerTopology(cv_connection=ansible_module.client)

    # Build Container topology
    if ansible_module.params['state'] == MODE_PRESENT:

        #-- Create Containers
        creation_data = manager_containers_create(cv_connection=ansible_module.client,
                                                  user_topology=ansible_module.params['topology'])
        if creation_data['containers_created'] > 0:
            result['changed'] = True
            result['data']['creation_result'] = creation_data

        #-- Manage configlets at container level
        # configlets_data = manager_container_configlets(cv_connection=ansible_module.client,
        #                                                user_topology=ansible_module.params['topology'],
        #                                                state=ansible_module.params['state'])
        # #---- Add configlet to containers
        # if 'configlet_add' in configlets_data:
        #     if configlets_data['configlet_add']['configlet_attached'] > 0:
        #         result['changed'] = True
        #         result['data']['configlet_attached'] = configlets_data['configlet_add']['configlet_attached']
        #         result['data']['configlet_attached_result'] = configlets_data['configlet_add']['configlet_attached_list']
        # #---- Remove configlet from containers
        # if 'configlet_detach' in configlets_data:
        #     if configlets_data['configlet_detach']['configlet_detached'] > 0:
        #         result['changed'] = True
        #         result['data']['configlet_detached'] = configlets_data['configlet_detach']['configlet_detached']
        #         result['data']['configlet_detached_result'] = configlets_data['configlet_detach']['configlet_detached_list']

    # Remove containers topology from Cloudvision
    if ansible_module.params['state'] == MODE_ABSENT:
        deletion_data = manager_container_delete(cv_connection=ansible_module.client, user_topology=ansible_module.params['topology'])
        if deletion_data['containers_deleted'] > 0:
            result['changed'] = True
            result['data']['deletion_result'] = deletion_data

    # Ansible output
    ansible_module.exit_json(**result)
