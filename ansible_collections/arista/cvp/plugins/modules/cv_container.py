#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=bare-except
#
# FIXME: required to pass ansible-test
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

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

import sys
import json
import traceback
import logging
import ansible_collections.arista.cvp.plugins.module_utils.cv_tools as cv_tools
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
# from ansible_collections.arista.cvp.plugins.module_utils.cv_client import CvpClient
# from ansible_collections.arista.cvp.plugins.module_utils.cv_client_errors import CvpLoginError
try:
    from cvprac.cvp_client import CvpClient
    from cvprac.cvp_client_errors import CvpLoginError, CvpApiError
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()

from ansible.module_utils.six import string_types
TREELIB_IMP_ERR = None
try:
    from treelib import Tree
    HAS_TREELIB = True
except ImportError:
    HAS_TREELIB = False
    TREELIB_IMP_ERR = traceback.format_exc()

# List of Ansible default containers
builtin_containers = ['Undefined', 'root']


DOCUMENTATION = r'''
---
module: cv_container
version_added: "2.9"
author: EMEA AS Team (@aristanetworks)
short_description: Manage Provisioning topology.
description:
  - CloudVision Portal Configlet configuration requires a dictionary of containers with their parent,
    to create and delete containers on CVP side.
  - Returns number of created and/or deleted containers
options:
  topology:
    description: Yaml dictionary to describe intended containers
    required: true
    type: dict
  cvp_facts:
    description: Facts from CVP collected by cv_facts module
    required: true
    type: dict
  mode:
    description: Allow to save topology or not
    required: false
    default: merge
    choices:
      - merge
      - override
      - delete
    type: str
  configlet_filter:
    description: Filter to apply intended set of configlet on containers.
                 If not used, then module only uses ADD mode. configlet_filter
                 list configlets that can be modified or deleted based
                 on configlets entries.
    required: false
    default: ['none']
    type: list
'''

EXAMPLES = r'''
- name: Create container topology on CVP
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    verbose: False
    containers:
        Fabric:
            parent_container: Tenant
        Spines:
            parent_container: Fabric
            configlets:
                - container_configlet
            images:
                - 4.22.0F
            devices:
                - veos01
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      cv_facts:
      register: cvp_facts
    - name: "Build Container topology on {{inventory_hostname}}"
      cv_container:
        cvp_facts: '{{cvp_facts.ansible_facts}}'
'''


MODULE_LOGGER = logging.getLogger('arista.cvp.cv_container')
MODULE_LOGGER.info('Start cv_container module execution')


def create_builtin_containers(facts):
    """
    Update builtin containers with root container name

    Parameters
    ----------
    facts : dict
        CloudVision facts from cv_facts
    debug : bool, optional
        Activate debug output, by default False
    """
    root = get_root_container(containers_fact=facts['containers'])
    builtin_containers.append(root)


def get_root_container(containers_fact, debug=True):
    """
    Extract name of the root container provided by cv_facts.

    Parameters
    ----------
    containers_fact : list
        List of containers to read from cv_facts

    Returns
    -------
    string
        Name of the root container, if not found, return Tenant as default value
    """
    for container in containers_fact:
        MODULE_LOGGER.debug('working on container %s', str(container))
        if container['Key'] == 'root':
            # if debug:
            MODULE_LOGGER.info('! ROOT container has name %s', container['Name'])
            return container['Name']
    return 'Tenant'


def tree_to_list(json_data, myList):
    """
    Transform a tree structure into a list of object to create CVP.

    Because some object have to be created in a specific order on CVP side,
    this function parse a tree to provide an ordered list of elements to create

    Example:
    --------
        >>> containers = {"Tenant": {"children": [{"Fabric": {"children": [{"Leaves": {"children": ["MLAG01", "MLAG02"]}}, "Spines"]}}]}}
        >>> print tree_to_list(containers=containers, myList=list())
        [u'Tenant', u'Fabric', u'Leaves', u'MLAG01', u'MLAG02', u'Spines']

    Parameters
    ----------
    json_data : [type]
        [description]
    myList : list
        Ordered list of element to create on CVP / recursive function

    Returns
    -------
    list
        Ordered list of element to create on CVP
    """
    # Cast input to be encoded as JSON structure.
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    # If it is a dictionary object,
    # it means we have to go through it to extract content
    if isinstance(json_data, dict):
        # Get key as it is a container name we want to save.
        for k1, v1 in json_data.items():
            # Ensure we are getting children element.
            if isinstance(v1, dict):
                for k2, v2 in v1.items():
                    if 'children' == k2:
                        # Save entry as we are dealing with an object to create
                        myList.append(k1)
                        for e in v2:
                            # Move to next element with a recursion
                            tree_to_list(json_data=json.dumps(e), myList=myList)
    # We are facing a end of a branch with a list of leaves.
    elif isinstance(json_data, list):
        for entry in json_data:
            myList.append(entry)
    # We are facing a end of a branch with a single leaf.
    elif isinstance(json_data, string_types):
        myList.append(json_data)
    return myList


def tree_build_from_dict(containers=None, root='Tenant'):
    """
    Build a tree based on a unsorted dictConfig(config).

    Build a tree of containers based on an unsorted dict of containers.

    Example:
    --------
        >>> containers = {'Fabric': {'parent_container': 'Tenant'},
            'Leaves': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Fabric'},
            'MLAG01': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Leaves'},
            'MLAG02': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Leaves'},
            'Spines': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Fabric'}}
        >>> print(tree_build_from_dict(containers=containers))
            {"Tenant": {"children": [{"Fabric": {"children": [{"Leaves": {"children": ["MLAG01", "MLAG02"]}}, "Spines"]}}]}}
    Parameters
    ----------
    containers : dict, optional
        Container topology to create on CVP, by default None
    root: string, optional
        Name of container to consider as root for topology, by default Tenant

    Returns
    -------
    json
        tree topology
    """
    # Create tree object
    tree = Tree()  # Create the base node
    previously_created = list()
    # Create root node to mimic CVP behavior
    MODULE_LOGGER.debug('containers list is %s', str(containers))
    MODULE_LOGGER.debug('root container is set to: %s', str(root))
    tree.create_node(root, root)
    # Iterate for first level of containers directly attached under root.
    for container_name, container_info in containers.items():
        if container_info['parent_container'] in [root]:
            previously_created.append(container_name)
            tree.create_node(container_name, container_name, parent=container_info['parent_container'])
            MODULE_LOGGER.debug(
                'create root tree entry with: %s', str(container_name))
    # Loop since expected tree is not equal to number of entries in container topology
    while (len(tree.all_nodes()) < len(containers)):
        MODULE_LOGGER.debug(
            ' Tree has size: %s - Containers has size: %s', str(len(tree.all_nodes())), str(len(containers)))
        for container_name, container_info in containers.items():
            if tree.contains(container_info['parent_container']) and container_info['parent_container'] not in [root]:
                try:
                    MODULE_LOGGER.debug(
                        'create new node with: %s', str(container_name))
                    tree.create_node(container_name, container_name, parent=container_info['parent_container'])
                except:  # noqa E722
                    continue
    return tree.to_json()


def tree_build_from_list(containers, root='Tenant'):
    """
    Build a tree based on a unsorted list.

    Build a tree of containers based on an unsorted list of containers.

    Example:
    --------
        >>> containers = [
            {
                "childContainerKey": null,
                "configlets": [],
                "devices": [],
                "imageBundle": "",
                "key": "root",
                "name": "Tenant",
                "parentName": null
            },
            {
                "childContainerKey": null,
                "configlets": [
                    "veos3-basic-configuration"
                ],
                "devices": [
                    "veos-1"
                ],
                "imageBundle": "",
                "key": "container_43_840035860469981",
                "name": "staging",
                "parentName": "Tenant"
            }]
        >>> print(tree_build_from_list(containers=containers))
            {"Tenant": {"children": [{"Fabric": {"children": [{"Leaves": {"children": ["MLAG01", "MLAG02"]}}, "Spines"]}}]}}
    Parameters
    ----------
    containers : dict, optional
        Container topology to create on CVP, by default None
    root: string, optional
        Name of container to consider as root for topology, by default Tenant

    Returns
    -------
    json
        tree topology
    """
    # Create tree object
    tree = Tree()  # Create the base node
    previously_created = list()
    # Create root node to mimic CVP behavior
    MODULE_LOGGER.debug('containers list is %s', str(containers))
    tree.create_node(root, root)
    # Iterate for first level of containers directly attached under root.
    for cvp_container in containers:
        if cvp_container['parentName'] is None:
            continue
        if cvp_container['parentName'] in [root]:
            MODULE_LOGGER.debug('found container attached to %s: %s', str(root), str(cvp_container))
            previously_created.append(cvp_container['name'])
            tree.create_node(cvp_container['name'], cvp_container['name'], parent=cvp_container['parentName'])
    # Loop since expected tree is not equal to number of entries in container topology
    while len(tree.all_nodes()) < len(containers):
        for cvp_container in containers:
            if tree.contains(cvp_container['parentName']):  # and cvp_container['parentName'] not in ['Tenant']
                try:
                    tree.create_node(cvp_container['name'], cvp_container['name'], parent=cvp_container['parentName'])
                except:  # noqa E722
                    continue
    return tree.to_json()


def tree_build(containers=None, root='Tenant'):
    """
    Triage function to build a tree.

    Call appropriate function wether we are using list() or dict() as input.

    Parameters
    ----------
    containers : dict or list, optional
        Containers' structure to use to build tree, by default None
    root: string, optional
        Name of container to consider as root for topology, by default Tenant

    """
    if isinstance(containers, dict):
        return tree_build_from_dict(containers=containers, root=root)
    elif isinstance(containers, list):
        return tree_build_from_list(containers=containers, root=root)
    return None


def isIterable(testing_object=None):
    """
    Test if an object is iterable or not.

    Test if an object is iterable or not. If yes return True, else return False.

    Parameters
    ----------
    testing_object : any, optional
        Object to test if it is iterable or not, by default None

    """
    try:
        some_object_iterator = iter(testing_object)  # noqa # pylint: disable=unused-variable
        return True
    except TypeError:
        return False


def connect(module):
    """
    Create a connection to CVP server to use API

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection

    Returns
    -------
    CvpClient
        CvpClient object to manager API calls.
    """
    client = CvpClient()
    connection = Connection(module._socket_path)
    host = connection.get_option("host")
    port = connection.get_option("port")
    user = connection.get_option("remote_user")
    pswd = connection.get_option("password")
    try:
        client.connect([host],
                       user,
                       pswd,
                       protocol="https",
                       port=port,
                       )
    except CvpLoginError as e:
        module.fail_json(msg=str(e))

    return client


def process_container(module, container, parent, action):
    """
    Execute action on CVP side to create / delete container.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    container : string
        Name of container to manage
    parent : string
        Name of parent of container to manage
    action : string
        Action to run on container. Must be one of: 'show/add/delete'
    """
    containers = module.client.api.get_containers()
    # Ensure the parent exists
    parent = next((item for item in containers['data'] if
                   item['name'] == parent), None)
    if not parent:
        module.fail_json(msg=str('Parent container (' + str(parent) + ') does not exist for container ' + str(container)))

    cont = next((item for item in containers['data'] if
                 item['name'] == container), None)
    if cont:
        if action == "show":
            return [False, {'container': cont}]
        elif action == "add":
            return [False, {'container': cont}]
        elif action == "delete":
            resp = module.client.api.delete_container(cont['name'],
                                                      cont['key'],
                                                      parent['name'],
                                                      parent['key'])
            if resp['data']['status'] == "success":
                return [True, {'taskIDs': resp['data']['taskIds']},
                        {'container': cont}]
    else:
        if action == "show":
            return [False, {'container': "Not Found"}]
        elif action == "add":
            resp = module.client.api.add_container(container, parent['name'],
                                                   parent['key'])
            if resp['data']['status'] == "success":
                return [True, {'taskIDs': resp['data']['taskIds']},
                        {'container': cont}]
        if action == "delete":
            return [False, {'container': "Not Found"}]


def create_new_containers(module, intended, facts):
    """
    Create missing container to CVP Topology.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : dict
        Facts from CVP collected by cv_facts module
    """
    count_container_creation = 0
    # Get root container of topology
    topology_root = get_root_container(containers_fact=facts['containers'])
    # Build ordered list of containers to create: from Tenant to leaves.
    container_intended_tree = tree_build_from_dict(containers=intended, root=topology_root)
    container_intended_ordered_list = tree_to_list(json_data=container_intended_tree, myList=list())
    # Parse ordered list of container and check if they are configured on CVP.
    # If not, then call container creation process.
    for container_name in container_intended_ordered_list:
        found = False
        # Check if container name is found in CVP Facts.
        for fact_container in facts['containers']:
            if container_name == fact_container['name']:
                found = True
                break
        # If container has not been found, we create it
        if not found:
            # module.fail_json(msg='** Create container'+container_name+' attached to '+intended[container_name]['parent_container'])
            response = process_container(module=module,
                                         container=container_name,
                                         parent=intended[container_name]['parent_container'],
                                         action='add')
            # If a container has been created, increment creation counter
            if response[0]:
                count_container_creation += 1
    # Build module message to return for creation.
    if count_container_creation > 0:
        return [True, {'containers_created': "" + str(count_container_creation) + ""}]
    return [False, {'containers_created': "0"}]


def is_empty(module, container_name, facts):
    """
    Check if container can be removed safely.

    To be removed, a container shall not have any container or
    device attached to it. Current function parses facts to see if a device or
    a container is attached. If not, we can remove container

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    container_name : str
        Name of the container to look for.
    facts : dict
        Facts from CVP collected by cv_facts module
    """
    is_empty = True
    not_empty = False
    # test if container has at least one device attached
    for device in facts['devices']:
        if device['parentContainerName'] == container_name:
            return not_empty
    return is_empty


def is_container_empty(module, container_name):
    MODULE_LOGGER.debug('get_devices_in_container %s', container_name)
    container_status = module.client.api.get_devices_in_container(container_name)
    MODULE_LOGGER.debug('* is_container_empty - get_devices_in_container %s', str(container_status))
    if container_status is not None:
        if isIterable(container_status) and len(container_status) > 0:
            MODULE_LOGGER.info(
                'Found devices in container %s', str(container_name))
            return False
        MODULE_LOGGER.info(
            'No devices found in container %s', str(container_name))
        return True
    MODULE_LOGGER.debug(
        'No devices found in container %s (default behavior)', str(container_name))
    return False


def get_container_facts(container_name='Tenant', facts=None):
    """
    Get FACTS information for a container.

    Parameters
    ----------
    container_name : str, optional
        Name of the container to look for, by default 'Tenant'
    facts : dict, optional
        CVP facts information, by default None
    """
    for container in facts['containers']:
        if container['name'] == container_name:
            return container
    return None


def delete_unused_containers(module, intended, facts):
    """
    Delete containers from CVP Topology when not defined in intended.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # default_containers = ['Tenant', 'Undefined', 'root']
    count_container_deletion = 0
    container_to_delete = list()

    # Get root container for the topology
    topology_root = get_root_container(containers_fact=facts['containers'])

    # Build a tree of containers configured on CVP
    container_cvp_tree = tree_build_from_list(containers=facts['containers'], root=topology_root)
    container_cvp_ordered_list = tree_to_list(json_data=container_cvp_tree, myList=list())

    # Build a tree of containers expected to be configured on CVP
    container_intended_tree = tree_build_from_dict(containers=intended, root=topology_root)
    container_intended_ordered_list = tree_to_list(json_data=container_intended_tree, myList=list())

    container_to_delete = list()
    # Build a list of container configured on CVP and not on intended.
    for cvp_container in container_cvp_ordered_list:
        # Only container with no devices can be deleted.
        # If container is not empty, no reason to go further.
        if is_container_empty(module=module, container_name=cvp_container):
            # Check if a container is not present in intended topology.
            if cvp_container not in container_intended_ordered_list:
                container_to_delete.append(cvp_container)

    MODULE_LOGGER.info('List of containers to delete: %s', str(container_to_delete))

    # Read cvp_container from end. If containers are part of container_to_delete, then delete container
    for cvp_container in reversed(container_to_delete):
        # Check if container is not in intended topology and not a default container.
        if cvp_container in container_to_delete and cvp_container not in builtin_containers:
            # Get container fact for parentName
            container_fact = get_container_facts(container_name=cvp_container, facts=facts)
            # Check we have a result. Even if we should always have a match here.
            if container_fact is not None:
                MODULE_LOGGER.info('container: %s', container_fact['name'])
                response = None
                try:
                    response = process_container(module=module,
                                                 container=container_fact['name'],
                                                 parent=container_fact['parentName'],
                                                 action='delete')
                except:  # noqa E722
                    MODULE_LOGGER.error(
                        "Unexpected error: %s", str(sys.exc_info()[0]))
                    continue
                if response[0]:
                    count_container_deletion += 1
    if count_container_deletion > 0:
        return [True, {'containers_deleted': "" + str(count_container_deletion) + ""}]
    return [False, {'containers_deleted': "0"}]


def container_info(container_name, module):
    """
    Get dictionary of container info from CVP.

    Parameters
    ----------
    container_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.
    Returns
    -------
    dict: Dict of container info from CVP or exit with failure if no info for
            container is found.
    """
    container_info = module.client.api.get_container_by_name(container_name)
    if container_info is None:
        container_info = {}
        container_info['error'] = "Container with name '%s' does not exist." % container_name
    else:
        container_info['configlets'] = module.client.api.get_configlets_by_container_id(container_info['key'])
    return container_info


def device_info(device_name, module):
    """
    Get dictionary of device info from CVP.

    Parameters
    ----------
    device_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.
    Returns
    -------
    dict: Dict of device info from CVP or exit with failure if no info for
            device is found.
    """
    device_info = module.client.api.get_device_by_name(device_name)
    if not device_info:
        devices = module.client.api.get_inventory()
        for device in devices:
            if device_name in device['fqdn']:
                device_info = device
    if not device_info:
        # Debug Line ##
        # module.fail_json(msg=str('Debug - device_info: %r' %device_info))
        # Debug Line ##
        device_info['error'] = "Device with name '%s' does not exist." % device_name
    else:
        device_info['configlets'] = module.client.api.get_configlets_by_netelement_id(device_info['systemMacAddress'])['configletList']
        device_info['parentContainer'] = module.client.api.get_container_by_id(device_info['parentContainerKey'])
    return device_info


def task_info(module, taskId):
    return module.client.api.get_task_by_id(taskId)


def move_devices_to_container(module, intended, facts):
    """
    Move devices to desired containers based on topology.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # Initialize response structure
    # Result return for Ansible
    result = dict()
    # List of devices moved by this function
    moved_devices = list()  # configlets with config changes
    # Structure to save list of devices moved and number of moved
    moved = dict()
    # Number of devices moved to containers.
    moved['devices_moved'] = 0
    # List of created taskIds to pass to cv_tasks
    task_ids = list()
    # Define wether we want to save topology or not
    # Force to True as per issue115
    save_topology = True
    # Read complete intended topology to locate devices
    for container_name, container in intended.items():
        # If we have at least one device defined, then we can start process
        if 'devices' in container:
            # Extract list of device hostname
            for device in container['devices']:
                # Get CVP information for target container.
                # move_device_to_container requires to use structure sends by CVP
                container_cvpinfo = container_info(container_name=container_name,
                                                   module=module)
                # Get CVP information for device.
                # move_device_to_container requires to use structure sends by CVP
                device_cvpinfo = device_info(device_name=device, module=module)
                # Initiate a move to desired container.
                # Task is created but not executed.
                device_action = module.client.api.move_device_to_container(app_name="ansible_cv_container",
                                                                           device=device_cvpinfo,
                                                                           container=container_cvpinfo,
                                                                           create_task=save_topology)
                if device_action['data']['status'] == 'success':
                    if 'taskIds' in device_action['data']:
                        for task in device_action['data']['taskIds']:
                            task_ids.append(task)
                    moved_devices.append(device)
                    moved['devices_moved'] = moved['devices_moved'] + 1
    # Build ansible output messages.
    moved['list'] = moved_devices
    moved['taskIds'] = task_ids
    result['changed'] = True
    result['moved_devices'] = moved
    return result


def container_factinfo(container_name, facts):
    """
    Get dictionary of configlet info from CVP.

    Parameters
    ----------
    configlet_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.

    Returns
    -------
    dict: Dict of configlet info from CVP or exit with failure if no info for
            container is found.
    """
    for container in facts['containers']:
        if container['name'] == container_name:
            return container
    return None


def configlet_factinfo(configlet_name, facts):
    """
    Get dictionary of configlet info from CVP.

    Parameters
    ----------
    configlet_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.

    Returns
    -------
    dict: Dict of configlet info from CVP or exit with failure if no info for
            container is found.
    """
    for configlet in facts['configlets']:
        if configlet['name'] == configlet_name:
            return configlet
    return None


def configure_configlet_to_container(module, intended, facts):
    """
    Manage mechanism to attach and detach configlets from container.

    Addition process:
    -----------------
    - if configlet from intended match filter: configlet is attached
    - if configlet from intended does not match filter: configlet is
    ignored
    - configlet_filter = ['none'] filtering is ignored and configlet is
    attached

    Deletion process:
    -----------------
    - if configlet is not part of intended and filter is not matched: we do
    not remove it
    - if configlet is not part of intended and filter is matched: we
    detach configlet.
    - configlet_filter = ['none'], configet is ignored and not detached

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # Initialize response structure
    #  Result return for Ansible
    result = dict()
    #  List of configlets attached by this function
    attached_configlet = list()
    #  Structure to save list of configlets attached and number of moved
    attached = dict()
    #  Number of configlets attached to containers.
    attached['configlet_attached'] = 0
    #  List of configlets detached by this function
    detached_configlet = list()
    #  Structure to save list of configlets detached and number of moved
    detached = dict()
    #  Number of configlets detached from containers.
    detached['configlet_detached'] = 0
    #  List of created taskIds to pass to cv_tasks
    task_ids = list()
    # List of configlets to attach to containers
    configlet_list_attach = list()
    # List of configlets to detach from containers.
    configlet_list_detach = list()
    # Define wether we want to save topology or not
    # Force to True as per issue115
    save_topology = True
    # Structure to save CVP result for configlet changes
    configlet_action = dict()
    # Configlet filter
    configlet_filter = module.params['configlet_filter']
    # Read complete intended topology to locate devices
    for container_name, container in intended.items():
        MODULE_LOGGER.info('work with container %s', str(container_name))
        # If we have at least one configlet defined, then we can start process
        # Get CVP information for target container.
        container_info_cvp = container_info(container_name=container_name, module=module)
        if 'configlets' in container:
            MODULE_LOGGER.debug('container has a list of containers to configure: %s', str(container['configlets']))
            # Extract list of configlet names
            for configlet in container['configlets']:
                MODULE_LOGGER.debug('running configlet %s', str(configlet))
                # We apply filter to know if we have to attach configlet.
                # If filter is set to ['none'], we consider add in any situation.
                if cv_tools.match_filter(input=configlet, filter=configlet_filter) or('none' in configlet_filter):
                    MODULE_LOGGER.debug('collecting information for configlet %s', str(configlet))
                    # Get CVP information for device.
                    configlet_cvpinfo = configlet_factinfo(configlet_name=configlet, facts=facts)
                    # Configlet information is saved for later deployment
                    configlet_list_attach.append(configlet_cvpinfo)
                    MODULE_LOGGER.debug('configlet_list_attach is now: %s', str(configlet_list_attach))
        # Create call to attach list of containers
        # Initiate a move to desired container.
        # Task is created but not executed.
        # Create debug output structure
        configlets_name = list()
        for configlet in configlet_list_attach:
            configlets_name.append(configlet['name'])
        # Configure new configlet to container
        if len(configlet_list_attach) > 0:
            MODULE_LOGGER.info('Apply %s to %s', str(configlets_name), str(container_info_cvp['name']))
            configlet_action = module.client.api.apply_configlets_to_container(app_name="ansible_cv_container",
                                                                               new_configlets=configlet_list_attach,
                                                                               container=container_info_cvp,
                                                                               create_task=save_topology)
            MODULE_LOGGER.debug('Get following response from cvprac for addition: %s', str(configlet_action))
            # Release list of configlet to configure (#165)
            configlet_list_attach = list()
            if 'data' in configlet_action and configlet_action['data']['status'] == 'success':
                if 'taskIds' in configlet_action['data']:
                    for task in configlet_action['data']['taskIds']:
                        task_ids.append(task)
                if len(configlet_list_attach) > 0:
                    attached_configlet.append(configlet_list_attach)
                    attached['configlet_attached'] = attached['configlet_attached'] + 1

        # Remove configlets from containers
        # def remove_configlets_from_container(self, app_name, container,del_configlets, create_task=True):
        container_info_cvp = container_factinfo(
            container_name=container_name, facts=facts)
        MODULE_LOGGER.info('get container info: %s for container %s', str(
            container_info_cvp), str(container_name))
        if container_info_cvp is not None and 'configlets' in container_info_cvp:
            for configlet in container_info_cvp['configlets']:
                # If configlet matchs filter, we just remove attachment.
                match_filter = cv_tools.match_filter(
                    input=configlet, filter=configlet_filter, default_always='none')
                MODULE_LOGGER.info('Filter test has returned: %s - Filter is %s - input is %s', str(match_filter), str(configlet_filter), str(configlet))
                # If configlet is not in intended and does not match filter, ignore it
                # If filter is set to ['none'], we consider to NOT touch attachment in any situation.
                if (match_filter is False
                        and container_factinfo(container_name=container, facts=facts) is not None
                        and configlet not in container_factinfo(container_name=container, facts=facts)['configlets']):
                    MODULE_LOGGER.warning('configlet does not match filter (%s) and is not in intended topology (%s), skipped', str(
                        configlet_filter), str(container_info_cvp['configlets']))
                    continue
                # If configlet is not part of intended list and match filter: we remove
                container_factsinfo = container_factinfo(
                    container_name=container_name, facts=facts)
                # If there is no configlet found in facts, just skipping this section.
                if 'configlets' not in container_factsinfo:
                    MODULE_LOGGER.info('container %s has no configlets attached - skipped', str(container))
                    continue
                if match_filter and configlet not in ['configlets']:
                    MODULE_LOGGER.debug(
                        'collecting information for configlet %s', str(configlet))
                    # Get CVP information for device.
                    configlet_cvpinfo = configlet_factinfo(configlet_name=configlet, facts=facts)
                    # Configlet information is saved for later deployment
                    MODULE_LOGGER.warning(
                        'addind configlet %s to list of detach...', str(configlet))
                    configlet_list_detach.append(configlet_cvpinfo)

            # Create debug output structure
            configlets_name = list()
            for configlet in configlet_list_detach:
                configlets_name.append(configlet['name'])
            # Configure new configlet to container
            if len(configlet_list_detach) > 0:
                MODULE_LOGGER.info('Removing %s from %s', str(
                    configlets_name), str(container_info_cvp['name']))
                configlet_action = module.client.api.remove_configlets_from_container(app_name="ansible_cv_container",
                                                                                      del_configlets=configlet_list_detach,
                                                                                      container=container_info_cvp,
                                                                                      create_task=save_topology)
                MODULE_LOGGER.debug('Get following response from cvprac for deletion: %s', str(configlet_action))
                # Release list of configlet to configure (#165)
                configlet_list_detach = list()
                if 'data' in configlet_action and configlet_action['data']['status'] == 'success':
                    if 'taskIds' in configlet_action['data']:
                        for task in configlet_action['data']['taskIds']:
                            task_ids.append(task)
                    if len(configlet_list_detach) > 0:
                        detached_configlet.append(configlet_list_detach)
                        detached['configlet_attached'] = detached['configlet_list_detach'] + 1

    # Build ansible output messages.
    attached['list'] = attached_configlet
    attached['taskIds'] = task_ids
    result['changed'] = True
    result['attached_configlet'] = attached
    result['detached_configlet'] = detached
    MODULE_LOGGER.debug('configure_configlet_to_container returns %s', str(result))
    return result


def locate_relative_root_container(containers_topology):
    """
    Function to locate root container of partial topology

    In case user provides a partial topology, it is required to locate root of
    this topology and not CVP root container. it is useful in case of a partial
    deletion and not complete tree.

    Parameters
    ----------
    containers_topology : dict
        User's defined intended topology

    Returns
    -------
    string
        Name of the relative root container. None if not found.
    """
    MODULE_LOGGER.debug('relative intended topology is: %s', str(containers_topology))
    for container_name, container in containers_topology.items():
        if container['parent_container'] not in containers_topology.keys():
            return container_name
    return None


def delete_topology(module, intended, facts):
    """
    Delete CVP Topology when state is set to absent.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # default_containers = ['Tenant', 'Undefined', 'root']
    count_container_deletion = 0
    container_to_delete = list()

    # Get root container for current topology
    topology_root = get_root_container(containers_fact=facts['containers'])
    # First try to get relative topology root container.
    topology_root_relative = locate_relative_root_container(containers_topology=intended)
    # If not found for any reason, fallback to CVP root container.
    if topology_root_relative is None:
        topology_root_relative = get_root_container(
            containers_fact=facts['containers'])
    MODULE_LOGGER.info('relative topology root is: %s', str(topology_root))
    # Build a tree of containers configured on CVP
    MODULE_LOGGER.info('build tree topology from facts topology')
    container_cvp_tree = tree_build_from_list(
        containers=facts['containers'], root=topology_root)
    container_cvp_ordered_list = tree_to_list(json_data=container_cvp_tree, myList=list())  # noqa # pylint: disable=unused-variable

    # Build a tree of containers expected to be deleted from CVP
    MODULE_LOGGER.info('build tree topology from intended topology')
    container_intended_tree = tree_build_from_dict(
        containers=intended, root=topology_root_relative)
    container_intended_ordered_list = tree_to_list(json_data=container_intended_tree, myList=list())

    MODULE_LOGGER.info('container_intended_ordered_list %s', container_intended_ordered_list)

    container_to_delete = list()
    # Check if containers can be deleted (i.e. no attached devices)
    for cvp_container in container_intended_ordered_list:
        # Do not run test on built-in containers
        if cvp_container not in builtin_containers:
            # Only container with no devices can be deleted.
            # If container is not empty, no reason to go further.
            if is_empty(module=module, container_name=cvp_container, facts=facts) or is_container_empty(module=module, container_name=cvp_container):
                # Check if a container is not present in intended topology.
                if cvp_container in container_intended_ordered_list:
                    container_to_delete.append(cvp_container)

    MODULE_LOGGER.debug('containers_to_delete %s', str(container_to_delete))

    for cvp_container in reversed(container_to_delete):
        MODULE_LOGGER.debug('deletion of cvp_container %s', str(cvp_container))
        # Check if container is not in intended topology and not a default container.
        if cvp_container in container_to_delete and cvp_container not in builtin_containers:
            # Get container fact for parentName
            MODULE_LOGGER.debug('get_container_facts %s', cvp_container)
            container_fact = get_container_facts(container_name=cvp_container, facts=facts)
            # Check we have a result. Even if we should always have a match here.
            if container_fact is not None:
                MODULE_LOGGER.debug('container name: %s', container_fact['name'])
                response = process_container(module=module,
                                             container=container_fact['name'],
                                             parent=container_fact['parentName'],
                                             action='delete')
                if response[0]:
                    count_container_deletion += 1
    if count_container_deletion > 0:
        return [True, {'containers_deleted': "" + str(count_container_deletion) + ""}]
    return [False, {'containers_deleted': "0"}]


def get_tasks(taskIds, module):
    """
    Collect TASK INFO from CVP.

    Parameters
    ----------
    taskIds : list
        list of tasks ID to get.
    module : AnsibleModule
        Ansible Module with connection information.

    Returns
    -------
    list
        List of Task information.
    """

    tasksList = list()
    # remove duplicate entries
    taskIds = list(set(taskIds))
    # Get task content from CVP
    for taskId in taskIds:
        tasksList.append(task_info(module=module, taskId=taskId))
    return tasksList


def main():
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        topology=dict(type='dict', required=True),          # Topology to configure on CV side.
        cvp_facts=dict(type='dict', required=True),         # Facts from cv_facts module.
        configlet_filter=dict(type='list', default='none'),  # Filter to protect configlets to be detached
        mode=dict(type='str',
                  required=False,
                  default='merge',
                  choices=['merge', 'override', 'delete'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    if not HAS_CVPRAC:
        module.fail_json(msg='cvprac required for this module')

    result = dict(changed=False, data={})
    result['data']['taskIds'] = list()
    result['data']['tasks'] = list()
    module.client = connect(module)
    deletion_process = None
    creation_process = None
    # Create list of builtin containers
    create_builtin_containers(facts=module.params['cvp_facts'])
    try:
        if module.params['mode'] in ['merge', 'override']:
            # -> Start process to create new containers
            if (isIterable(module.params['topology']) and module.params['topology'] is not None):
                creation_process = create_new_containers(module=module,
                                                         intended=module.params['topology'],
                                                         facts=module.params['cvp_facts'])
                if creation_process[0]:
                    result['data']['changed'] = True
                    result['data']['creation_result'] = creation_process[1]
                # -> Start process to move devices to targetted containers
                move_process = move_devices_to_container(module=module,
                                                         intended=module.params['topology'],
                                                         facts=module.params['cvp_facts'])
                if move_process is not None:
                    result['data']['changed'] = True
                    # If a list of task exists, we expose it
                    if 'taskIds' in move_process['moved_devices']:
                        for taskId in move_process['moved_devices']['taskIds']:
                            result['data']['taskIds'].append(taskId)
                    # move_process['moved_devices'].pop('taskIds',None)
                    result['data']['moved_result'] = move_process['moved_devices']

                # -> Start process to move devices to targetted containers
                attached_process = configure_configlet_to_container(module=module,
                                                                    intended=module.params['topology'],
                                                                    facts=module.params['cvp_facts'])
                if attached_process is not None:
                    result['data']['changed'] = True
                    # If a list of task exists, we expose it
                    if 'taskIds' in attached_process['attached_configlet']:
                        for taskId in attached_process['attached_configlet']['taskIds']:
                            result['data']['taskIds'].append(taskId)
                    # move_process['moved_devices'].pop('taskIds',None)
                    result['data']['attached_configlet'] = attached_process['attached_configlet']

        # If MODE is override we also delete containers with no device and not listed in our topology
        if module.params['mode'] == 'override':
            # -> Start process to delete unused container.
            if (isIterable(module.params['topology']) and module.params['topology'] is not None):
                deletion_process = delete_unused_containers(module=module,
                                                            intended=module.params['topology'],
                                                            facts=module.params['cvp_facts'])
            else:
                deletion_process = delete_unused_containers(module=module,
                                                            intended=dict(),
                                                            facts=module.params['cvp_facts'])
            if deletion_process[0]:
                result['data']['changed'] = True
                result['data']['deletion_result'] = deletion_process[1]

        # If MODE is DELETE then we start process to delete topology
        elif module.params['mode'] == 'delete':
            # -> Start process to delete container described in topology.
            if (isIterable(module.params['topology']) and module.params['topology'] is not None):
                deletion_topology_process = delete_topology(module=module,
                                                            intended=module.params['topology'],
                                                            facts=module.params['cvp_facts'])
                if deletion_topology_process[0]:
                    result['data']['changed'] = True
                    result['data']['deletion_result'] = deletion_topology_process[1]

        if len(result['data']['taskIds']) > 0:
            result['data']['tasks'] = get_tasks(module=module, taskIds=result['data']['taskIds'])

        # DEPRECATION: Make a copy to support old namespace.
        result['cv_container'] = result['data']

    except CvpApiError as e:
        module.fail_json(msg=str(e))
    module.exit_json(**result)


if __name__ == '__main__':
    main()
