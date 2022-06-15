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
# Required by Ansible and CVP
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: cv_tag_v3
version_added: "4.0.0"
author: PM Team (@aristanetworks)
short_description: Create/Assign/Delete/Unassign tags on CVP
description:
  - CloudVison Portal Tag module to Create/Assign/Delete/Unassign tags on CloudVision
options:
  tags:
    description: CVP tags
    required: True
    type: dict
    elements: str
  mode:
    description: action to carry out on the tags
                 create - create tags
                 delete - delete tags
                 assign - assign existing tags to device
                 unassign - unassign existing tags from device
    required: false
    type: str
    choices:
      - create
      - delete
      - assign
      - unassign
  auto_create:
    description: auto_create tags before assigning
    required: false
    default: true
    type: bool
'''

EXAMPLES = '''
---
- name: "create tags"
  arista.cvp.cv_tag_v3:
    tags: "{{CVP_TAGS}}"
    mode: create
    auto_create: true
'''

import logging
import traceback
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.response import CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv
from ansible_collections.arista.cvp.plugins.module_utils import tools_schema
from ansible_collections.arista.cvp.plugins.module_utils.tag_tools import CvTagTools, CvTagInput
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Logger startup
MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info('Start cv_tag_v3 module execution')


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

# ------------------------------------------------------------ #
#               MAIN section -- starting point                 #
# ------------------------------------------------------------ #


def main():
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        # Topology to configure on CV side.
        tags=dict(type='list', required=True, elements='dict'),
        mode=dict(type='str',
                  required=False,
                  choices=['assign', 'unassign', 'create', 'delete']),
        auto_create=dict(type='bool',
                         required=False,
                         default=True)
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(argument_spec=argument_spec,
                                   supports_check_mode=True)

    # Test all libs are correctly installed
    check_import(ansible_module=ansible_module)

    # import epdb; epdb.serve(port=8888)
    user_tags = CvTagInput(ansible_module.params['tags'])
    if user_tags.is_valid is False:
        ansible_module.fail_json(msg=f"Error, your input is not valid against current schema:\n {ansible_module.params['tags']}")

    # check for incompatible options
    if ansible_module.params['mode'] == 'assign' or ansible_module.params['mode'] == 'unassign':
        for per_device in ansible_module.params['tags']:
            if 'device_tags' in per_device.keys() and 'device' not in per_device.keys():
                ansible_module.fail_json(msg="Error, 'device' needed for each 'device_tags"
                                             " when mode is 'assign' or 'unassign'")
            if 'interface_tags' in per_device.keys():
                MODULE_LOGGER.info('interface tags in keys')
                if 'device' not in per_device.keys():
                    ansible_module.fail_json(msg="Error, 'device' needed for each 'interface_tags'"
                                                 " when mode is 'assign' or 'unassign'")
                for per_intf in per_device['interface_tags']:
                    MODULE_LOGGER.info('per_intf: %s', per_intf)
                    MODULE_LOGGER.info('keys: %s', per_intf.keys())
                    if 'interface' not in per_intf.keys():
                        ansible_module.fail_json(msg="Error, 'interface' needed for each 'interface_tags'"
                                                     " when mode is 'assign' or 'unassign'")

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)
    tag_manager = CvTagTools(cv_connection=cv_client, ansible_module=ansible_module)
    ansible_response: CvAnsibleResponse = tag_manager.tasker(tags=ansible_module.params['tags'],
                                                             mode=ansible_module.params['mode'],
                                                             auto_create=ansible_module.params['auto_create'])

    result = ansible_response.content
    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
