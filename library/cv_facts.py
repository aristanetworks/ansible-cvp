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
DOCUMENTATION = """
---
module: cv_facts
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
short_description: Collect facts from CloudVision Portal.
description:
  - Returns the list of devices, configlets, containers and images
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
"""

from ansible.module_utils.basic import AnsibleModule
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError

def connect(module):
    ''' Connects to CVP device using user provided credentials from playbook.
    :param module: Ansible module with parameters and client connection.
    :return: CvpClient object with connection instantiated.
    '''
    client = CvpClient()
    try:
        client.connect([module.params['host']],
                       module.params['username'],
                       module.params['password'],
                       protocol=module.params['protocol'],
                       port=module.params['port'],
                       )
    except CvpLoginError as e:
        module.fail_json(msg=str(e))
    return client

def get_configlets(module):
    return module.client.api.get_configlets()['data']

def get_containers(module):
    return module.client.api.get_containers()['data']

def get_images(module):
    return module.client.api.get_images()['data']

def get_devices(module):
    return module.client.api.get_devices()

def get_tasks(module):
    return module.client.api.get_tasks()['data']

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        host=dict(required=True),
        port=dict(type='int', default=None),
        protocol=dict(default='https', choices=['http', 'https']),
        username=dict(required=True),
        password=dict(required=True, no_log=True),
    )
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)
    
    result = dict(changed=False, ansible_facts={})

    module.client = connect(module)
    
    facts = result["ansible_facts"]
    facts["configlets"] = get_configlets(module)
    facts["devices"] = get_devices(module)
    facts["images"] = get_images(module)
    facts["containers"] = get_containers(module)
    facts["tasks"] = get_tasks(module)
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()
