#!/usr/bin/env python
#
# Copyright (c) 2019, Arista Networks AS-EMEA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

ANSIBLE_METADATA = {'metadata_version': '0.0.2.dev0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: cv_container
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
short_description: Manage Provisioning topology.
description:
  - CloudVison Portal Configlet configuration requires a dictionary of containers with their parent,
    to create and delete containers on CVP side.
  - Returns number of created and/or deleted containers
options:
  host:
    description: IP Address or hostname of the CloudVisin Server
    required: true
    default: null
  username:
    description: The username to log into Cloudvision.
    required: true
    default: null
  password:
    description: The password to log into Cloudvision.
    required: true
    default: null
  protocol:
    description: The HTTP protocol to use. Choices http or https.
    required: false
    default: https
  port:
    description: The HTTP port to use. The cvprac defaults will be used
                  if none is specified.
    required: false
    default: null
  topology:
    description: Yaml dictionary to describe intended containers
    required: true
    default: None
  cvp_facts:
    description: Facts from CVP collected by cv_facts module
    required: true
    default: None
  save_topology:
    description: Allow to save topology or not
    required: false
    default: False
"""

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
        host: '{{ansible_host}}'
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        protocol: https
      register: cvp_facts
    - name: "Build Container topology on {{inventory_hostname}}"
      cv_container:
        host: '{{ansible_host}}'
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        topology: '{{containers}}'
        cvp_facts: '{{cvp_facts.ansible_facts}}'
'''

RETURN = r'''
creation_result:
    description: Information about number of containers created on CVP.
    returned: On Success.
    type: complex
    contains:
        containers_created:
            description: Number of created containers on CVP.
            sample: "creation_result": {"containers_created": "4"}
deletion_result:
    description: Information about number of containers deleted on CVP.
    returned: On Success.
    type: complex
    contains:
        containers_deleted:
            description: Number of deleted containers on CVP.
            sample: "deletion_result": {"containers_deleted": "4"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.legacy_cvp.cvp_client import CvpClient
from ansible.module_utils.legacy_cvp.cvp_client_errors import CvpLoginError, CvpApiError
from treelib import Node, Tree
import json

def tree_to_list(json_data, myList):
    """
    Transform a tree structure into a list of object to create CVP.

    Because some object have to be created in a specific order on CVP side, 
    this function parse a tree to provide an ordered list of elements to create
    
    Example:
    --------
        >>> containers = {"Tenant": {"children": [{"Fabric": {"children": [{"Leaves": {"children": ["MLAG01", "MLAG02"]}}, "Spines"]}}]}}
        >>> print tree_to_list(containers=containers, myList=lsit())
        [u'Tenant', u'Fabric', u'Leaves', u'MLAG01', u'MLAG02', u'Spines']

    Parameters
    ----------
    json_data : [type]
        [description]
    myList : list
        Ordered list of element to create on CVP / recusrive function
    
    Returns
    -------
    list
        Ordered list of element to create on CVP
    """
    # Cast input to be encoded as JSON structure.
    if isinstance(json_data,str):
        json_data = json.loads(json_data)
    # If it is a dictionary object, 
    # it means we have to go through it to extract content
    if isinstance(json_data,dict):
        # Get key as it is a container name we want to save.
        for k1,v1 in json_data.items():
            # Ensure we are getting children element.
            if isinstance(v1,dict):
                for k2,v2 in v1.items():
                    if 'children' == k2:
                        # Save entry as we are dealing with an object to create
                        myList.append(k1)
                        for e in v2:
                            # Move to next element with a recursion
                            tree_to_list(json_data=e, myList=myList)
    # We are facing a end of a branch with a list of leaves.
    elif isinstance(json_data, list):
        for entry in json_data:
            myList.append(entry)
    # We are facing a end of a branch with a single leaf.
    elif isinstance(json_data, basestring):
        myList.append(json_data)
    return myList

def tree_build_from_dict(containers=None):
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
    
    Returns
    -------
    json
        tree topology
    """
    # Create tree object
    tree = Tree() # Create the base node
    previously_created=list()
    # Create root node to mimic CVP behavior
    tree.create_node("Tenant", "Tenant") 
    # Iterate for first level of containers directly attached under root.
    for container_name, container_info in containers.items():
        if container_info['parent_container'] in ['Tenant']:
            previously_created.append(container_name)
            tree.create_node(container_name, container_name, parent=container_info['parent_container'])
    # Loop since expected tree is not equal to number of entries in container topology
    while len(tree.all_nodes()) < len(containers)+1:
        for container_name, container_info in containers.items():
            if  tree.contains(container_info['parent_container']) and container_info['parent_container'] not in ['Tenant']:
                try: 
                    tree.create_node(container_name, container_name, parent=container_info['parent_container'])
                except:
                    continue
    return tree.to_json()

def tree_build_from_list(containers):
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
    
    Returns
    -------
    json
        tree topology
    """
    # Create tree object
    tree = Tree() # Create the base node
    previously_created=list()
    # Create root node to mimic CVP behavior
    tree.create_node("Tenant", "Tenant") 
    # Iterate for first level of containers directly attached under root.
    for cvp_container in containers:
        if cvp_container['parentName'] == None:
            continue
        elif cvp_container['parentName'] in ['Tenant']:
            previously_created.append(cvp_container['name'])
            tree.create_node(cvp_container['name'], cvp_container['name'], parent=cvp_container['parentName'])
    # Loop since expected tree is not equal to number of entries in container topology
    while len(tree.all_nodes()) < len(containers):
        for cvp_container in containers:
            if  tree.contains(cvp_container['parentName']) : #and cvp_container['parentName'] not in ['Tenant']
                try:
                    tree.create_node(cvp_container['name'], cvp_container['name'], parent=cvp_container['parentName'])
                except:
                    continue
    return tree.to_json()

def tree_build(containers=None):
    """
    Triage function to build a tree.

    Call appropriate function wether we are using list() or dict() as input.
    
    Parameters
    ----------
    containers : dict or list, optional
        Containers' structure to use to build tree, by default None
    """
    if isinstance(containers, dict):
        return tree_build_from_dict(containers=containers)
    elif isinstance(containers, list):
        return tree_build_from_list(containers=containers)
    return None

def isIterable( testing_object= None):
    """
    Test if an object is iterable or not.

    Test if an object is iterable or not. If yes return True, else return False.

    Parameters
    ----------
    testing_object : any, optional
        Object to test if it is iterable or not, by default None
    """
    try:
        some_object_iterator = iter(testing_object)
        return True
    except TypeError as te:
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
    try:
        client.connect([module.params['host']],
                       module.params['username'],
                       module.params['password'],
                       protocol=module.params['protocol'],
                       port=module.params['port'],
                       )
    except CvpLoginError, e:
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
            return [False,{'container':cont}]
        elif action == "add":
            return [False,{'container':cont}]
        elif action == "delete":
            resp = module.client.api.delete_container(cont['name'],
                                                      cont['key'],
                                                      parent['name'],
                                                      parent['key'])
            if resp['data']['status'] == "success":
                return [True,{'taskIDs':resp['data']['taskIds']},
                        {'container':cont}]
    else:                 
        if action == "show":
            return [False,{'container':"Not Found"}]
        elif action == "add":
            resp = module.client.api.add_container(container, parent['name'],
                                            parent['key'])
            if resp['data']['status'] == "success":
                return [True,{'taskIDs':resp['data']['taskIds']},
                        {'container':cont}]
        if action == "delete":
            return [False,{'container':"Not Found"}]


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
    # Build ordered list of containers to create: from Tenant to leaves.
    container_intended_tree = tree_build_from_dict(containers=intended)
    container_intended_ordered_list = tree_to_list(json_data=container_intended_tree, myList=list())
    # Parse ordered list of container and chek if they are configured on CVP.
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
    # Build module message to retur for creation.
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
    is_empty = True
    not_empty = False
    container_status = module.client.api.get_devices_in_container(container_name)
    if container_status is not None:
        if isIterable(container_status) and len(container_status) > 0:
            return False
        return True
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
    default_containers = ['Tenant', 'Undefined', 'root']
    count_container_deletion = 0
    container_to_delete = list()
    
    # Build a tree of containers configured on CVP
    container_cvp_tree = tree_build_from_list(containers=facts['containers'])
    container_cvp_ordered_list = tree_to_list(json_data=container_cvp_tree, myList=list())

    # Build a tree of containers expected to be configured on CVP
    container_intended_tree = tree_build_from_dict(containers=intended)
    container_intended_ordered_list = tree_to_list(json_data=container_intended_tree, myList=list())

    container_to_delete = list()
    # Build a list of container configured on CVP and not on intended.
    for cvp_container in container_cvp_ordered_list:
        # Only container with no devices can be deleted.
        # If container is not empty, no reason to go further.
        if is_empty(module=module, container_name=cvp_container, facts=facts) or is_container_empty(module=module, container_name=cvp_container):
            # Check if a container is not present in intended topology.
            if cvp_container not in container_intended_ordered_list:
                container_to_delete.append(cvp_container)
    
    # Read cvp_container from end. If containers are part of container_to_delete, then delete container
    for cvp_container in reversed(container_cvp_ordered_list):
        # Check if container is not in intended topology and not a default container.
        if cvp_container in container_to_delete and cvp_container not in default_containers:
            # Get container fact for parentName
            container_fact = get_container_facts(container_name=cvp_container, facts=facts)
            # Check we have a result. Even if we should always have a match here.
            if container_fact is not None:
                response = process_container(module=module,
                                             container=container_fact['name'],
                                             parent=container_fact['parentName'],
                                             action='delete')
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
        Ansible module to get access to cvp cient.

    Returns
    -------
    dict: Dict of container info from CVP or exit with failure if no info for
            container is found.
    """
    container_info = module.client.api.get_container_by_name(container_name)
    if container_info == None:
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
        Ansible module to get access to cvp cient.

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
        ## Debug Line ##
        module.fail_json(msg=str('Debug - device_info: %r' %device_info))
        ## Debug Line ##
        device_info['error']="Device with name '%s' does not exist." % device_name
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
    #  Result return for Ansible
    result = dict()
    #  List of devices moved by this function
    moved_devices = list() # configlets with config changes
    #  Structure to save list of devices moved and number of moved
    moved = dict()
    #  Number of devices moved to containers.
    moved['devices_moved'] = 0
    #  List of created taskIds to pass to cv_tasks
    task_ids=list()
    # Define wether we want to save topology or not
    save_topology = False if module.params['save_topology']==False else True
    # Read complete intended topology to locate devices
    for container_name, container in intended.items():
        # If we have at least one device defined, then we can start process
        if 'devices' in container:
            # Extract list of device hostname
            for device in container['devices']:
                # Get CVP information for target container.
                # move_device_to_container requires to use structure sends by CVP
                container_cvpinfo = container_info(container_name=container_name, module=module)
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
                    moved['devices_moved']= moved['devices_moved']+1
    # Build ansible output messages.
    moved['list'] = moved_devices
    moved['taskIds'] = task_ids
    result['changed'] = True
    result['moved_devices'] = moved
    return result

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        host=dict(required=True),
        port=dict(type='int', default=None),
        protocol=dict(default='https', choices=['http', 'https']),
        username=dict(required=True),
        password=dict(required=True, no_log=True),
        topology=dict(type='dict', required=True),
        cvp_facts=dict(type='dict', required=True),
        save_topology=dict(type='bool', default=True)    # Enable or disable task creation
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)
    result = dict(changed=False, cv_container={})
    result['cv_container']['tasks'] = list()
    module.client = connect(module)
    deletion_process = None
    creation_process = None
    try:
        # Start process to create new containers
        # Should be done only if topology is iterable.
        if (isIterable(module.params['topology']) and module.params['topology'] is not None):
            creation_process = create_new_containers(module=module,
                                                    intended=module.params['topology'],
                                                    facts=module.params['cvp_facts'])
            if creation_process[0]:
                result['cv_container']['changed'] = True
                result['cv_container']['creation_result'] = creation_process[1]
            
            # Start process to move devices to targetted containers
            move_process = move_devices_to_container(module=module,
                                                     intended=module.params['topology'],
                                                     facts=module.params['cvp_facts'])

            if move_process is not None:
                result['cv_container']['changed'] = True
                # If a list of task exists, we expose it
                if 'taskIds' in move_process['moved_devices']:
                    for taskId in move_process['moved_devices']['taskIds']:
                        result['cv_container']['tasks'].append(task_info(module=module, taskId = taskId))
                # move_process['moved_devices'].pop('taskIds',None)
                result['cv_container']['moved_result'] = move_process['moved_devices']
                
        # Start process to delete unused container.
        if (isIterable(module.params['topology']) and module.params['topology'] is not None):
            deletion_process = delete_unused_containers(module=module,
                                                        intended=module.params['topology'],
                                                        facts=module.params['cvp_facts'])
        else: 
            deletion_process = delete_unused_containers(module=module,
                                                        intended=dict(),
                                                        facts=module.params['cvp_facts'])
        if deletion_process[0]:
            result['cv_container']['changed'] = True
            result['cv_container']['deletion_result'] = deletion_process[1]
    except CvpApiError, e:
        module.fail_json(msg=str(e))
    module.exit_json(**result)

if __name__ == '__main__':
    main()
