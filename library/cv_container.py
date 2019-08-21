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

DOCUMENTATION = """
---
module: cv_container
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
short_description: Create or Update CloudVision Portal Container.
description:
  - CloudVison Portal Configlet configuration requires the container name,
    and parent container name to create the new container under
  - Returns the container data and any Task IDs created during the operation
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
  container:
    description: CVP container to apply the configlet to if no device
                  is specified
    required: false
    default: None
  parent:
    description: Name of the Parent container for the container specified
                  Used to configure target container and double check
                  container configuration
    required: false
    default: 'Tenant'
  action:
    description: action to carry out on the container
                  add -  create the container under the parent container
                  delete - remove from parent container
                  show - return the current container data if available
    required: true
    choices: 
      - 'show'
      - 'add'
      - 'delete'
    default: add
"""

EXAMPLES = r'''
# Example to create a container just under root container
- name: Create a container on CVP.
  cv_container:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    container: ansible_container
    parent: Tenant
    action: add

# Example to delete container attached to root container
- name: Delete a container on CVP.
  cv_container:
      host: '{{ansible_host}}'
      username: '{{cvp_username}}'
      password: '{{cvp_password}}'
      protocol: https
      container: ansible_container
      parent: Tenant
      action: delete

# Example to get information on a container
- name: Show a container on CVP.
  cv_container:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    container: ansible_container
    parent: Tenant
    action: show
  register: cvp_result

- name: Display cv_container show result
  debug:
    msg: "{{cvp_result}}"
'''

from ansible.module_utils.basic import AnsibleModule
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError


def connect(module):
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
    containers = module.client.api.get_containers()

    # Ensure the parent exists
    parent = next((item for item in containers['data'] if
                   item['name'] == parent), None)
    if not parent:
        module.fail_json(msg=str('Parent container does not exist.'))

    cont = next((item for item in containers['data'] if
                 item['name'] == container), None)
    if cont:
        if action == "show":
            return [False,{'container':cont}]
        elif action == "add":
            return [False,{'container':cont}]
        elif action == "delete":
            resp = module.client.api.delete_container(cont['name'],cont['key'], parent['name'],
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



def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        host=dict(required=True),
        port=dict(type='int', default=None),
        protocol=dict(default='https', choices=['http', 'https']),
        username=dict(required=True),
        password=dict(required=True, no_log=True),
        container=dict(required=True),
        parent=dict(default='Tenant'),
        action=dict(default='add', choices=['add','delete','show'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    result = dict(changed=False)

    module.client = connect(module)
    container = module.params['container']
    parent = module.params['parent']
    action = module.params['action']

    try:
        changed = process_container(module, container, parent, action)
        if changed[0]:
            result['changed'] = True
            result['taskIDs'] = changed[1]
        else:
            result['data'] = changed[1]
    except CvpApiError, e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)


if __name__ == '__main__':
    main()
