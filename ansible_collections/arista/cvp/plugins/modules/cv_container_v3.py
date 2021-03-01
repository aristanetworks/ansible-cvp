#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=bare-except
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
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.schema as schema
from ansible.module_utils.basic import AnsibleModule
try:
    from cvprac.cvp_client import CvpClient
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Ansible module preparation
ansible_module = ""
CV_CONTAINER_MODE = ['merge', 'override', 'delete']

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_container_v3')
MODULE_LOGGER.info('Start cv_container_v3 module execution')


def facts_get_topology(cv_connection: CvpClient(), root_node: str = 'root'):
    """
    facts_get_topology Collect Containers & Devices topology from Cloudvision

    Parameters
    ----------
    cv_connection : CvpClient
        CV connection handler
    root_node : str, optional
        Root container of the topology, by default 'root'

    Returns
    -------
    dict
        Cloudvision Containers & Devices topology
    """
    topology = dict()
    try:
        topology = cv_connection.api.filter_topology(node_id=root_node)
    except:  # noqa E722
        MODULE_LOGGER.error('Error to get topology from CV for node %s', str(root_node))
    return topology


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


def list_containers_from_top(container_list, container_root_name: str, parent_field='parent_container'):
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
#               API Action -- Require to return JSON result    #
# ------------------------------------------------------------ #

def container_create(cv_connection: CvpClient, container: str, parent: str):
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
    lsit
        Response to be added in ansible
    """
    resp = dict()
    taskIds = 'UNSET'
    if ansible_module.check_mode:
        MODULE_LOGGER.debug(
            '[check mode] - Create container %s under %s', str(container), str(parent))
        return {"success": True, "taskIDs": taskIds, "container": container}
    elif is_container_exist(cv_connection=cv_connection, container=parent):
        parent_id = container_get_id(cv_connection=cv_connection, container=parent)
        try:
            resp = cv_connection.api.add_container(container_name=container, parent_name=parent, parent_key=parent_id)
            MODULE_LOGGER.debug('Container %s has been created on CV under %s', str(container), str(parent))
        except:  # noqa E722
            MODULE_LOGGER.error("Error creating container %s on CV", str(container))
        else:
            if resp['data']['status'] == "success":
                taskIds = resp['data']['taskIds']
        # Return structured data for a container creation
        return {"success": True, "taskIDs": taskIds, "container": container}
    else:
        MODULE_LOGGER.debug('Parent container (%s) is missing for container %s', str(parent), str(container))
        return {"success": False, "taskIDs": taskIds, "container": container}


# ------------------------------------------------------------ #
#               CONTAINER MANAGERS -- Execute API calls         #
# ------------------------------------------------------------ #

def manager_containers_create(cv_connection: CvpClient(), user_topology):
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
    root_container_name = container_get_root(cv_connection=cv_connection)
    MODULE_LOGGER.debug("Container root name is set to %s", root_container_name)
    if ansible_module.check_mode:
        MODULE_LOGGER.info("Running creation process in check_mode")

    # Build a tree of containers expected to be configured on CVP
    user_containers_topology_ordered_list = list_containers_from_top(container_list=user_topology, container_root_name=root_container_name)

    # --- Container creation process
    MODULE_LOGGER.info('Start to create containers for %s', str(user_containers_topology_ordered_list))
    for user_container_name in user_containers_topology_ordered_list:
        # Validate parent container exists
        if (is_container_exist(cv_connection=cv_connection,
                               container=user_topology[user_container_name]['parent_container'])
            or ansible_module.check_mode):
            # Create missing containers
            if is_container_exist(cv_connection=cv_connection, container=user_container_name) is False:
                action_result = container_create(cv_connection=cv_connection,
                                                 container=user_container_name,
                                                 parent=user_topology[user_container_name]["parent_container"])
                MODULE_LOGGER.debug('  - Containers creation manager received %s when creating container %s', str(action_result), str(user_container_name))
                if action_result["success"] is True:
                    containers_created_counter += 1
                    containers_created.append(user_container_name)
    MODULE_LOGGER.debug('End of creation loop with: %s', str(containers_created))
    return {"containers_created": containers_created_counter, "containers_created_list": containers_created}



if __name__ == '__main__':
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        topology=dict(type='dict', required=True),            # Topology to configure on CV side.
        cvp_facts=dict(type='dict', required=False),          # Facts from cv_facts module.
        configlet_filter=dict(type='list', default='none'),   # Filter to protect configlets to be detached
        mode=dict(type='str',
                  required=False,
                  default='merge',
                  choices=CV_CONTAINER_MODE)
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(argument_spec=argument_spec,
                                   supports_check_mode=True)

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

    # Instantiate ansible results
    result = dict(changed=False, data={})
    result['data']['taskIds'] = list()
    result['data']['tasks'] = list()

    if ansible_module.params['mode'] in ['merge', 'override']:
        creation_data = manager_containers_create(cv_connection=ansible_module.client, user_topology=ansible_module.params['topology'])
        if creation_data['containers_created'] > 0:
            result['changed'] = True
            result['data']['creation_result'] = creation_data

    ansible_module.exit_json(**result)
