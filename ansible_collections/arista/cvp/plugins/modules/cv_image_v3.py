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
import os
__metaclass__ = type



EXAMPLES = r"""
---
---
- name: CVP Image Tests
  hosts: cv_server
  gather_facts: no
  vars:

  tasks:
    - name: "Gather CVP image information facts {{inventory_hostname}}"
      arista.cvp.cv_image_v3:
         mode: images
         action: get
      register: image_data

    - name: "Print out facts from {{inventory_hostname}}"
      debug:
        msg: "{{image_data}}"


    - name: "Get CVP image image bundles {{inventory_hostname}}"
      arista.cvp.cv_image_v3:
        mode: bundles
        action: get
      register: image_bundle_data

    - name: "Print out images from {{inventory_hostname}}"
      debug:
        msg: "{{image_bundle_data}}"


    - name: "Update an image bundle {{inventory_hostname}}"
      arista.cvp.cv_image_v3:
        mode: bundles
        action: add
        bundle_name: Test_bundle
        image_list:
           - TerminAttr-1.16.4-1.swix
           - EOS-4.25.4M.swi

"""



# Required by Ansible and CVP
import re
import logging
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.tools as tools
import ansible_collections.arista.cvp.plugins.module_utils.schema_v1 as schema
from ansible_collections.arista.cvp.plugins.module_utils.image_tools import *

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
        mode=dict(default='images', type='str', choices=['images','bundles']),
        action=dict(default='get', type='str', choices=['get','add','remove']),
        )

    ansible_module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    
    # Instantiate ansible results
    result = dict(changed=False, data={}, failed=False)
    warnings = list()


    MODULE_LOGGER.info('starting module cv_image_v3')
    if ansible_module.check_mode:
        MODULE_LOGGER.warning('! check_mode is enable')
        # module.exit_json(changed=True)


    if not tools_cv.HAS_CVPRAC:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

     # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    result = dict( changed=False )

    # Instantiate the image class    
    cv_images = CvImageTools( cv_connection=cv_client,
        ansible_module=ansible_module,
        check_mode=ansible_module.check_mode )
    
    result['changed'], result['data'], warnings = cv_images.module_action( **ansible_module.params )
    


    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
