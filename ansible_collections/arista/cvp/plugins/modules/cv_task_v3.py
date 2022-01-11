#!/usr/bin/python
# coding: utf-8 -*-
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
module: cv_task_v3
version_added: "3.0.0"
author: EMEA AS Team (@aristanetworks)
short_description: Execute or Cancel CVP Tasks.
description:
  - CloudVison Portal Task module to action pending tasks on CLoudvision
options:
  tasks:
    description: CVP taskIDs to act on
    required: True
    type: list
    elements: str
  state:
    description: action to carry out on the task
                 executed - execute tasks
                 cancelled - cancel tasks
    required: false
    default: executed
    type: str
    choices:
      - executed
      - cancelled
'''

EXAMPLES = '''
---
- name: Execute all tasks registered in cvp_configlets variable
  arista.cvp.cv_task:
    tasks: "{{ cvp_configlets.taskIds }}"

- name: Cancel a list of pending tasks
  arista.cvp.cv_task:
    tasks: ['666', '667']
    state: cancelled
'''

import logging
import traceback
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv
from ansible_collections.arista.cvp.plugins.module_utils.response import CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils.task_tools import CvTaskTools
try:
    from cvprac.cvp_client_errors import CvpClientError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger('arista.cvp.cv_tasks')
MODULE_LOGGER.info('Start cv_tasks module execution')


def check_import(ansible_module: AnsibleModule):
    """
    check_import Check all imports are resolved
    """
    if HAS_CVPRAC is False:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    # if not schema.HAS_JSONSCHEMA:
    #     ansible_module.fail_json(
    #         msg="JSONSCHEMA is required. Please install using pip install jsonschema")


def main():
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        # Topology to configure on CV side.
        tasks=dict(type='list', required=True, elements='str'),
        state=dict(type='str',
                   required=False,
                   default='executed',
                   choices=['executed', 'cancelled'])
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

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    task_manager = CvTaskTools(cv_connection=cv_client, ansible_module=ansible_module)
    ansible_response: CvAnsibleResponse = task_manager.tasker(taskIds_list=ansible_module.params['tasks'],
                                                              state=ansible_module.params['state'])

    result = ansible_response.content

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
