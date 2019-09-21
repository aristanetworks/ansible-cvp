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

ANSIBLE_METADATA = {'metadata_version': '0.0.1.dev0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: cv_container
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
short_description: Create or Update CloudVision Portal Container.
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
"""

EXAMPLES = r'''
- name: Create container topology on CVP
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    verbose: False
    containers:
      - name: Fabric
        parent_container: Tenant
      - name: Spines
        parent_container: Fabric
      - name: Leaves
        parent_container: Fabric
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
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError


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
    for container in intended:
        found = False
        for existing_container in facts['containers']:
            if container['name'] == existing_container['Name']:
                found = True
                break
        if not found:
            response = process_container(module=module,
                                         container=container['name'],
                                         parent=container['parent_container'],
                                         action='add')
            if response[0]:
                count_container_creation += 1
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
    # test if container_name is a parent container for another container
    for container_fact in facts['containers']:
        # If at least one container has container_name as parent container
        # we return information container_name is not empty
        if container_fact['parentName'] == container_name:
            return not_empty
    # test if container has at least one device attached
    for device in facts['devices']:
        if device['containerName'] == container_name:
            return not_empty
    return is_empty


def get_parentName_list(container_list, facts):
    """
    Collect list of parentName for all containers provided.

    Parameters
    ----------
    container_list : list
        List of containers' name to collect their parentName
    facts : dict
        Facts from CVP collected by cv_facts module
    """
    parentName = list()
    for container in facts['containers']:
        if container['Name'] in container_list:
            parentName.append(container['parentName'])
    return parentName


def recursive_tree_lookup(module, facts, children_to_delete, sorted_list):
    """
    Extract a sorted list of container to delete.

    Read facts[containers] and locate containers we can delete from bottom to top.
    Tree naviguation use recursive approach.
    This function assumes leaves are identified first and injected to function with sorted_list.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    facts : dict
        Facts from CVP collected by cv_facts module
    children_to_delete : list
        List of container to delete and used to lookup for sorted list.
    sorted_list : list
        Sorted list from bottom to top of containers we have to delete.
    """
    list_parentName = get_parentName_list(container_list=children_to_delete, facts=facts)
    list_resultLevelUp = list()
    # Build list of potential next containers to delete
    for container in facts['containers']:
        if container['Name'] in list_parentName and container['parentName'] != 'Tenant':
            list_resultLevelUp.append(container['Name'])

    # Recursive section
    # If a potential list exist, then go to next level
    if len(list_resultLevelUp) > 0:
        sorted_list = sorted_list + list_resultLevelUp
        recursive_tree_lookup(module=module,
                              facts=facts,
                              children_to_delete=list_resultLevelUp,
                              sorted_list=sorted_list)

    # If no more potential, then try to catch level under Tenant
    else:
        for container in facts['containers']:
            if container['Name'] in list_parentName and container['parentName'] == 'Tenant':
                sorted_list.append(container['Name'])

    # Return current sorted list
    return sorted_list


def sort_container_to_delete(module, containers_list, facts):
    """
    Build complete end to end list of container to delete.

    Identify leaves and then collect complete tree by reading recursive_tree_lookup

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    facts : dict
        Facts from CVP collected by cv_facts module
    containers_list : list
        Unsorted list of container to delete from CVP.
    """
    sorted_container_list = list()

    # Get first container we can remove
    # These container shall not have container nor device attached to them
    for container in containers_list:
        if is_empty(module=module, container_name=container, facts=facts):
            sorted_container_list.append(container)

    # Get parent container of leaf container identified previously
    sorted_container_list = recursive_tree_lookup(module=module,
                                 facts=facts,
                                 children_to_delete=sorted_container_list,
                                 sorted_list=sorted_container_list)
    return sorted_container_list


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
    default_containers = ['Tenant', 'Undefined']
    count_container_deletion = 0
    container_to_delete = list()
    for container in facts['containers']:
        found = False
        for new_container in intended:
            if new_container['name'] == container['Name']:
                found = True
        if not found and container['Name'] not in default_containers:
            container_to_delete.append(container['Name'])

    sorted_container_list = sort_container_to_delete(module=module,
                                                     containers_list=container_to_delete,
                                                     facts=facts)
    for container_name in sorted_container_list:
        for container in facts['containers']:
            if container_name == container['Name']:
                response = process_container(module=module,
                                             container=container['Name'],
                                             parent=container['parentName'],
                                             action='delete')
                if response[0]:
                    count_container_deletion += 1
    if count_container_deletion > 0:
        return [True, {'containers_deleted': "" + str(count_container_deletion) + ""}]
    return [False, {'containers_deleted': "0"}]


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        host=dict(required=True),
        port=dict(type='int', default=None),
        protocol=dict(default='https', choices=['http', 'https']),
        username=dict(required=True),
        password=dict(required=True, no_log=True),
        topology=dict(type='list', required=True),
        cvp_facts=dict(type='dict', required=True)
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)
    result = dict(changed=False)
    module.client = connect(module)

    try:
        creation_process = create_new_containers(module=module,
                                                 intended=module.params['topology'],
                                                 facts=module.params['cvp_facts'])
        if creation_process[0]:
            result['changed'] = True
            result['creation_result'] = creation_process[1]

        deletion_process = delete_unused_containers(module=module,
                                                    intended=module.params['topology'],
                                                    facts=module.params['cvp_facts'])
        if deletion_process[0]:
            result['changed'] = True
            result['deletion_result'] = deletion_process[1]
    except CvpApiError, e:
        module.fail_json(msg=str(e))
    module.exit_json(**result)


if __name__ == '__main__':
    main()
