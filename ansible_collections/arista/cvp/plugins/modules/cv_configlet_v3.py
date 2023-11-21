#!/usr/bin/python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=bare-except
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
#


from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: cv_configlet_v3
version_added: "3.0.0"
author: Ansible Arista Team (@aristanetworks)
short_description: Create, Delete, or Update CloudVision Portal Configlets.
description:
  - CloudVison Portal Configlet compares the list of configlets and config in
  - configlets against cvp-facts then adds, deletes, or updates
  - them as appropriate.
  - If a configlet is in cvp_facts but not in configlets it will be deleted.
  - If a configlet is in configlets but not in cvp_facts it will be created.
  - If a configlet is in both configlets and cvp_facts it configuration will
  - be compared and updated with the version in configlets
  - if the two are different.
options:
  configlets:
    description: List of configlets to managed on CVP server.
    required: true
    type: dict
  configlets_notes:
    description: Add a note to the configlets.
    required: false
    default: 'Managed by Ansible'
    type: str
  state:
    description:
        - If absent, configlets will be removed from CVP if not
          bound to a container or a device.
        - If present, configlets will be created or updated.
    required: false
    default: 'present'
    choices: ['present', 'absent']
    type: str
'''

EXAMPLES = r'''
---
- name: Test cv_configlet_v3
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    configlet_list:
      Test_Configlet: "! This is a Very First Testing Configlet\n!"
      Test_DYNAMIC_Configlet: "{{ lookup('file', 'templates/configlet_'+inventory_hostname+'.txt') }}"
  tasks:
    - name: "Push config"
      arista.cvp.cv_configlet_v3:
        configlets: "{{configlet_list}}"
        state: present
      register: cvp_configlet
'''

# Required by Ansible and CVP
import logging
import traceback
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv
from ansible_collections.arista.cvp.plugins.module_utils import tools_schema
from ansible_collections.arista.cvp.plugins.module_utils.configlet_tools import ConfigletInput, CvConfigletTools, HAS_HASHLIB, HAS_DIFFLIB
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Logger startup
MODULE_LOGGER = logging.getLogger('arista.cvp.cv_configlet')
MODULE_LOGGER.info('Start cv_configlet module execution')

# TODO - use f-strings
# pylint: disable=consider-using-f-string


def check_import(ansible_module: AnsibleModule):
    """
    check_import Check all imports are resolved
    """
    if HAS_CVPRAC is False:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not HAS_HASHLIB:
        ansible_module.fail_json(
            msg='hashlib required for this module. Please install using pip install hashlib')

    if not HAS_DIFFLIB:
        ansible_module.fail_json(
            msg='difflib required for this module. Please install using pip install difflib')

    if not tools_schema.HAS_JSONSCHEMA:
        ansible_module.fail_json(
            msg="JSONSCHEMA is required. Please install using pip install jsonschema")

# ------------------------------------------------------------ #
#               MAIN section -- starting point                 #
# ------------------------------------------------------------ #


def main():
    """
    Main entry point for module execution.
    """
    # TODO - ansible module prefers constructor over literal
    #        for dict
    # pylint: disable=use-dict-literal
    argument_spec = dict(
        # Topology to configure on CV side.
        configlets=dict(type='dict', required=True),
        state=dict(type='str',
                   required=False,
                   default='present',
                   choices=['present', 'absent']),
        configlets_notes=dict(type='str',
                              default='Managed by Ansible',
                              required=False)
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(argument_spec=argument_spec,
                                   supports_check_mode=True)
    # Instantiate ansible results
    result = dict(changed=False, data={}, failed=False)
    result['data']['taskIds'] = []
    result['data']['tasks'] = []

    # State management
    is_present = True
    if ansible_module.params['state'] == 'absent':
        is_present = False

    # Test all libs are correctly installed
    check_import(ansible_module=ansible_module)

    user_configlets = ConfigletInput(
        user_topology=ansible_module.params['configlets'])

    # Test user input against schema definition
    if user_configlets.is_valid is False:
        ansible_module.fail_json(
            msg='Error, your input is not valid against current schema:\n {}'.format(*ansible_module.params['configlets']))

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    # Instantiate data
    cv_configlet_manager = CvConfigletTools(
        cv_connection=cv_client, ansible_module=ansible_module)

    # if ansible_module.check_mode is True:
    #     ansible_module.fail_json(msg="Not yet implemented !")

    cv_response: CvAnsibleResponse = cv_configlet_manager.apply(
        configlet_list=user_configlets.configlets, present=is_present, note=ansible_module.params['configlets_notes'])
    result = cv_response.content

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
