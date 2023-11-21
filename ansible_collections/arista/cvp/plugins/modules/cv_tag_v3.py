#!/usr/bin/python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#

# Required by Ansible and CVP
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: cv_tag_v3
version_added: "3.4.0"
author: Ansible Arista Team (@aristanetworks)
short_description: Create/Assign/Delete/Unassign tags on CVP
description:
  - CloudVision Portal Tag module to Create/Assign/Delete/Unassign tags on CloudVision
options:
  tags:
    description: List of CVP tags.
    required: True
    type: list
    elements: dict
  mode:
    description: Action to carry out on the tags.
    required: false
    type: str
    choices:
      - create
      - delete
      - assign
      - unassign
  auto_create:
    description: Automatically create tags before assigning.
    required: false
    default: true
    type: bool
'''

EXAMPLES = r'''
# Create and assign device and interface tags to multiple devices and interfaces
- name: cv_tag_v3 example1
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device: leaf1
        device_tags:
          - name: tag1
            value: value1
          - name: tag2
            value: value2
          - name: tag3
            value: value3
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
              - name: tag2i
                value: value2i
          - interface: Ethernet2
            tags:
              - name: tag1i
                value: value1i
              - name: tag2i
                value: value2i
      - device: spine1
        device_tags:
          - name: DC
            value: Dublin
          - name: rack
            value: rackA
          - name: pod
            value: podA
        interface_tags:
          - interface: Ethernet3
            tags:
              - name: tag3i
                value: value3i
              - name: tag4i
                value: value4i
          - interface: Ethernet4
            tags:
              - name: tag5i
                value: value6i
              - name: tag6i
                value: value6i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: assign
        auto_create: true

# Delete device and interface tags using device_id
- name: cv_tag_v3 example2
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device_id: JPE123435
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: delete

# Create device and interface tags (without assigning to the devices) using device_id
- name: cv_tag_v3 example3
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device_id: JPE123435
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: create

# Assign device and interface tags
- name: cv_tag_v3 example4
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device: leaf1
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: assign

# Unassign device and interface tags
- name: cv_tag_v3 example5
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device: leaf1
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: assign
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
    # TODO - ansible module prefers constructor over literal
    #        for dict
    # pylint: disable=use-dict-literal
    MODULE_LOGGER.info('Start cv_tag_v3 module execution')
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
            if not ('device' in per_device.keys() or 'device_id' in per_device.keys()):
                error_msg = "Error, either 'device' or 'device_id' needed for each 'device tags/interface tags when mode is 'assign' or 'unassign'"
                ansible_module.fail_json(msg=error_msg)
            if 'interface_tags' in per_device.keys():
                MODULE_LOGGER.info('interface tags in keys')
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
