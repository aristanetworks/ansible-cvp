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

DOCUMENTATION = r'''
---
module: cv_device_v3
version_added: "3.0.0"
author: EMEA AS Team (@aristanetworks)
short_description: Manage Provisioning topology.
description:
  - CloudVision Portal Configlet configuration requires a dictionary of containers with their parent,
    to create and delete containers on CVP side.
  - Returns number of created and/or deleted containers
options:
  devices:
    description: List of devices with their container and configlets information
    required: true
    type: list
    elements: dict
  state:
    description: Set if ansible should build or remove devices on CLoudvision
    required: false
    default: 'present'
    choices: ['present', 'factory_reset']
    type: str
  apply_mode:
    description: Set how configlets are attached/detached on device. If set to strict all configlets not listed in your vars are detached.
    required: false
    default: 'loose'
    choices: ['loose', 'strict']
    type: str
  search_key:
    description: Key name to use to look for device in Cloudvision.
    required: false
    default: 'hostname'
    choices: ['fqdn', 'hostname', 'serialNumber']
    type: str
'''

EXAMPLES = r'''
# task in loose mode using fqdn (default)
- name: Device Management in Cloudvision
  hosts: cv_server
  connection: local
  gather_facts: false
  collections:
    - arista.cvp
  vars:
    CVP_DEVICES:
      - fqdn: CV-ANSIBLE-EOS01
        parentContainerName: ANSIBLE
        configlets:
            - 'CV-EOS-ANSIBLE01'
  tasks:
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: present
        search_key: fqdn

# task in loose mode using serial
- name: Device Management in Cloudvision
  hosts: cv_server
  connection: local
  gather_facts: false
  collections:
    - arista.cvp
  vars:
    CVP_DEVICES:
      - serialNumber: xxxxxxxxxxxx
        parentContainerName: ANSIBLE
        configlets:
            - 'CV-EOS-ANSIBLE01'
  tasks:
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: present
        search_key: serialNumber

# task in strict mode
- name: Device Management in Cloudvision
  hosts: cv_server
  connection: local
  gather_facts: false
  collections:
    - arista.cvp
  vars:
    CVP_DEVICES:
      - fqdn: CV-ANSIBLE-EOS01
        parentContainerName: ANSIBLE
        configlets:
            - 'CV-EOS-ANSIBLE01'
  tasks:
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: present
        apply_mode: strict
'''

import logging
import traceback
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv
from ansible_collections.arista.cvp.plugins.module_utils import tools_schema
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import CvDeviceTools, DeviceInventory
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Logger creation
MODULE_LOGGER = logging.getLogger('arista.cvp.cv_device_v3')
MODULE_LOGGER.info('Start cv_device_v3 module execution')


def check_import(ansible_module: AnsibleModule):
    """
    check_import Check all imports are resolved
    """
    if HAS_CVPRAC is False:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not tools_schema.HAS_JSONSCHEMA:
        ansible_module.fail_json(
            msg="JSONSCHEMA is required. Please install using pip install jsonschema")


def main():
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        # Topology to configure on CV side.
        devices=dict(type='list', required=True, elements='dict'),
        state=dict(type='str',
                   required=False,
                   default='present',
                   choices=['present', 'factory_reset']),
        apply_mode=dict(type='str',
                        required=False,
                        default='loose',
                        choices=['loose', 'strict']),
        search_key=dict(type='str',
                        required=False,
                        default='hostname',
                        choices=['fqdn', 'hostname', 'serialNumber'])
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(argument_spec=argument_spec,
                                   supports_check_mode=True)
    # Instantiate ansible results
    result = dict(changed=False, data={}, failed=False)
    result['data']['taskIds'] = list()
    result['data']['tasks'] = list()

    # Test all libs are correctly installed
    check_import(ansible_module=ansible_module)

    # Test user input against schema definition
    user_topology = DeviceInventory(data=ansible_module.params['devices'])

    if user_topology.is_valid is False:
        ansible_module.fail_json(
            msg='Error, your input is not valid against current schema:\n {}'.format(*ansible_module.params['devices']))

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    # Instantiate data
    cv_topology = CvDeviceTools(
        cv_connection=cv_client,
        ansible_module=ansible_module,
        check_mode=ansible_module.check_mode)

    MODULE_LOGGER.debug('Ansible user inventory is: %s', str(user_topology.devices))
    result = cv_topology.manager(
        user_inventory=user_topology,
        apply_mode=ansible_module.params['apply_mode'],
        search_mode=ansible_module.params['search_key'],
        state=ansible_module.params['state'])

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
