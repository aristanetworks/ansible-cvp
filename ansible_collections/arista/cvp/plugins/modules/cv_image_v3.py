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
module: cv_image_v3
version_added: 3.3.0
author: EMEA AS Team (@aristanetworks)
short_description: EOS Image management with Cloudvision
description:
  - CloudVision Portal Image management module.
  - ''
  - Due to a current limitation in Cloudvision API,
  - authentication with token is not supported for this module only.
options:
  image:
    description: Name of the image file, including path if needed
    required: false
    type: str
  image_list:
    description: List of name of the image file, including path if needed
    required: false
    type: list
    elements: str
  bundle_name:
    description: Name of the bundle to manage
    required: false
    type: str
  mode:
    description: What to manage with module
    required: false
    type: str
    choices:
      - bundle
      - image
    default: image
  action:
    description: Action to do with module
    required: false
    default: get
    type: str
    choices:
      - get
      - add
      - remove
'''

EXAMPLES = r'''
---
- name: CVP Image Tests
  hosts: cv_server
  gather_facts: no
  vars:
  tasks:
    - name: "Gather CVP image information facts {{inventory_hostname}}"
      arista.cvp.cv_image_v3:
         mode: image
         action: get
      register: image_data

    - name: "Print out facts from {{inventory_hostname}}"
      debug:
        msg: "{{image_data}}"


    - name: "Get CVP image image bundles {{inventory_hostname}}"
      arista.cvp.cv_image_v3:
        mode: bundle
        action: get
      register: image_bundle_data

    - name: "Print out images from {{inventory_hostname}}"
      debug:
        msg: "{{image_bundle_data}}"


    - name: "Update an image bundle {{inventory_hostname}}"
      vars:
        ansible_command_timeout: 1200
        ansible_connect_timeout: 600
      arista.cvp.cv_image_v3:
        mode: bundle
        action: add
        bundle_name: Test_bundle
        image_list:
           - TerminAttr-1.16.4-1.swix
           - EOS-4.25.4M.swi
'''

# Required by Ansible and CVP
import logging
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv
from ansible_collections.arista.cvp.plugins.module_utils.image_tools import CvImageTools

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_image')
MODULE_LOGGER.info('Start cv_image module execution')


def main():
    """
    main entry point for module execution.
    """
    argument_spec = dict(
        image=dict(type='str'),
        image_list=dict(type="list", elements='str'),
        bundle_name=dict(type='str'),
        mode=dict(default='image', type='str', choices=['image', 'bundle']),
        action=dict(default='get', type='str', choices=['get', 'add', 'remove']),
    )

    ansible_module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    # Instantiate ansible results
    result = dict(changed=False, data={}, failed=False)
    warnings = []

    MODULE_LOGGER.info('starting module cv_image_v3')
    if ansible_module.check_mode:
        MODULE_LOGGER.warning('! check_mode is enable')
        # module.exit_json(changed=True)

    if not tools_cv.HAS_CVPRAC:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac'
        )

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    result = dict(changed=False)

    # Instantiate the image class
    cv_images = CvImageTools(
        cv_connection=cv_client,
        ansible_module=ansible_module,
        check_mode=ansible_module.check_mode
    )

    result['changed'], result['data'], warnings = cv_images.module_action(**ansible_module.params)
    MODULE_LOGGER.warning(warnings)

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
