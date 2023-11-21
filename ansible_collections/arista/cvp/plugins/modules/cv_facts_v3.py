#!/usr/bin/python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=bare-except
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
#
# Copyright 2022 Arista Networks
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
module: cv_facts_v3
version_added: "3.3.0"
author: Ansible Arista Team (@aristanetworks)
short_description: Collect facts from CloudVision
description:
- Returns list of devices, configlets, containers, images and tasks from CloudVision
options:
  facts:
    description:
      - List of facts to retrieve from CVP.
      - By default, cv_facts returns facts for devices, configlets, containers, images, and tasks.
      - Using this parameter allows user to limit scope to a subset of information.
    required: false
    default: ['configlets', 'containers', 'devices', 'images', 'tasks']
    type: list
    elements: str
    choices: ['configlets', 'containers', 'devices', 'images', 'tasks']
  regexp_filter:
    description: Regular Expression to filter containers, configlets, devices and tasks in facts.
    required: false
    default: '.*'
    type: str
  verbose:
    description: Get all data from CVP or get only cv_modules data.
    required: false
    choices: ['long', 'short']
    default: 'short'
    type: str
'''

EXAMPLES = r'''
  tasks:
  - name: '#01 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:

  - name: '#02 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - configlets
    register: FACTS_DEVICES

  - name: '#03 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - devices
        - containers
    register: FACTS_DEVICES

  - name: '#04 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - devices
      regexp_filter: "spine1"
      verbose: long
    register: FACTS_DEVICES

  - name: '#05 - Collect images facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - images
    register: FACTS_DEVICES

  - name: '#06 - Collect task facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - tasks
      regexp_filter: 'Pending' # get facts filtered by task status - 'Failed', 'Pending', 'Completed', 'Cancelled'
      verbose: 'long'
    register: FACTS_DEVICES

  - name: '#07 - Collect task facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - tasks
      regexp_filter: 95 # get facts filtered by task_Id (int)
      verbose: 'long'
    register: FACTS_DEVICES
'''

import logging
import traceback
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv  # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils import tools_schema as schema
from ansible_collections.arista.cvp.plugins.module_utils.facts_tools import CvFactsTools
# from ansible_collections.arista.cvp.plugins.module_utils.facts_tools import *
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Logger creation
MODULE_LOGGER = logging.getLogger('arista.cvp.cv_facts_v3')
MODULE_LOGGER.info('Start cv_facts_v3 module execution')


def check_import(ansible_module: AnsibleModule):
    """
    check_import Check all imports are resolved
    """
    if HAS_CVPRAC is False:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not schema.HAS_JSONSCHEMA:
        ansible_module.fail_json(
            msg="JSONSCHEMA is required. Please install using pip install jsonschema")


def main():
    """
    Main entry point for module execution.
    """
    # TODO - ansible module prefers constructor over literal
    #        for dict
    # pylint: disable=use-dict-literal
    argument_spec = dict(
        # Ansible Argument Spec
        facts=dict(
            type='list',
            elements='str',
            required=False,
            choices=[
                'configlets',
                'containers',
                'devices',
                'images',
                'tasks',
            ],
            default=['configlets', 'containers', 'devices', 'images', 'tasks']),
        regexp_filter=dict(
            type='str',
            required=False,
            default='.*'
        ),
        verbose=dict(
            type='str',
            required=False,
            choices=['long', 'short'],
            default='short'
        )
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    # Test all libs are correctly installed
    check_import(ansible_module=ansible_module)

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    # Instantiate ansible results
    facts_collector = CvFactsTools(cv_connection=cv_client)
    try:
        facts = facts_collector.facts(scope=ansible_module.params['facts'], regex_filter=ansible_module.params['regexp_filter'],
                                      verbose=ansible_module.params['verbose'])
    except CvpClientError as e:
        ansible_module.fail_json(msg=str(e))
    result = dict(changed=False, data=facts, failed=False)

    # Implement logic

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
