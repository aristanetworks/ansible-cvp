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
module: cv_container_v3
version_added: "3.0.0"
author: EMEA AS Team (@aristanetworks)
short_description: Manage Provisioning topology.
description:
  - CloudVision Portal Configlet configuration requires a dictionary of containers with their parent,
    to create and delete containers on CVP side.
  - Module also supports to configure configlets at container level.
  - Returns number of created and/or deleted containers
options:
  topology:
    description: Yaml dictionary to describe intended containers
    required: true
    type: dict
  state:
    description: Set if ansible should build or remove devices on CLoudvision
    required: false
    default: 'present'
    choices: ['present', 'absent']
    type: str
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
            parentContainerName: Tenant
        Spines:
            parentContainerName: Fabric
            configlets:
                - container_configlet
  tasks:
    - name: 'running cv_container'
      arista.cvp.cv_container_v3:
        topology: "{{CVP_CONTAINERS}}"
'''


import logging
import traceback
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.schema as schema
from ansible_collections.arista.cvp.plugins.module_utils.container_tools import CvContainerTools, ContainerInput
from ansible_collections.arista.cvp.plugins.module_utils.response import CvAnsibleResponse
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Ansible module preparation
ansible_module: AnsibleModule

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_container_v3')
MODULE_LOGGER.info('Start cv_container_v3 module execution')


def check_import():
    """
    check_import Check all imports are resolved
    """
    if HAS_CVPRAC is False:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not schema.HAS_JSONSCHEMA:
        ansible_module.fail_json(msg="JSONSCHEMA is required. Please install using pip install jsonschema")


# ------------------------------------------------------------ #
#               MAIN section -- starting point                 #
# ------------------------------------------------------------ #

def main():
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        # Topology to configure on CV side.
        topology=dict(type='dict', required=True),
        state=dict(type='str',
                   required=False,
                   default='present',
                   choices=['present', 'absent'])
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(argument_spec=argument_spec,
                                   supports_check_mode=True)
    # Instantiate ansible results
    result = dict(changed=False, data={}, failed=False)
    result['data']['taskIds'] = list()
    result['data']['tasks'] = list()
    # Test all libs are correctly installed
    check_import()

    # boolean for state flag
    if ansible_module.params['state'] == 'absent':
        state_present = False
    else:
        state_present = True

    # Test user input against schema definition
    user_topology = ContainerInput(
        user_topology=ansible_module.params['topology'])

    if user_topology.is_valid is False:
        ansible_module.fail_json(
            msg='Error, your input is not valid against current schema:\n {}'.format(*ansible_module.params['topology']))

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    # Instantiate data
    cv_topology = CvContainerTools(
        cv_connection=cv_client, ansible_module=ansible_module)

    cv_response: CvAnsibleResponse = cv_topology.build_topology(
        user_topology=user_topology, present=state_present)
    MODULE_LOGGER.debug(
        'Received response from Topology builder: %s', str(cv_response))
    result = cv_response.content

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
