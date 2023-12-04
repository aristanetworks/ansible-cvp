#!/usr/bin/python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cv_validate_v3
version_added: "3.7.0"
author: Ansible Arista Team (@aristanetworks)
short_description: CVP/Local configlet Validation
description:
  - CloudVision Portal Validate module to Validate configlets against a device on CVP.
options:
  devices:
    description: CVP devices and configlet information.
    required: true
    type: list
    elements: dict
  validate_mode:
    description: Indicate how cv_validate_v3 should behave on finding errors or warnings.
    required: true
    type: str
    choices:
      - stop_on_error
      - stop_on_warning
      - ignore
"""

EXAMPLES = r"""
# offline validation
- name: offline configlet validation
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - device_name: leaf1
        search_type: hostname #[hostname | serialNumber | fqdn]
        local_configlets:
          valid: "interface Ethernet1\n  description test_validate"
          error: "ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111"

  tasks:
    - name: validate module
      arista.cvp.cv_validate_v3:
        devices: "{{CVP_DEVICES}}"
        validate_mode: stop_on_error # | stop_on_warning | valid

# online validation
- name: Online configlet validation
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - device_name: leaf1.aristanetworks.com
        search_type: fqdn #[hostname | serialNumber | fqdn]
        cvp_configlets:
          - valid
          - invalid

  tasks:
    - name: validate module
      arista.cvp.cv_validate_v3:
        devices: "{{CVP_DEVICES}}"
        validate_mode: stop_on_error # | stop_on_warning | valid
"""

import logging
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.response import CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv
from ansible_collections.arista.cvp.plugins.module_utils import tools_schema
from ansible_collections.arista.cvp.plugins.module_utils.validate_tools import CvValidateInput, CvValidationTools
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
            msg="cvprac required for this module. Please install using pip install cvprac"
        )

    if not tools_schema.HAS_JSONSCHEMA:
        ansible_module.fail_json(
            msg="JSONSCHEMA is required. Please install using pip install jsonschema"
        )

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
    MODULE_LOGGER.info("Start cv_validate_v3 module execution")
    argument_spec = dict(
        # Topology to configure on CV side.
        devices=dict(type="list", required=True, elements="dict"),
        validate_mode=dict(
            type="str",
            required=True,
            choices=["stop_on_warning", "stop_on_error", "ignore"],
        ),
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True
    )

    # Test all libs are correctly installed
    check_import(ansible_module=ansible_module)

    user_input = CvValidateInput(ansible_module.params["devices"])

    # Schema validation
    if user_input.is_valid is False:
        ansible_module.fail_json(
            msg=f"Error, your input is not valid against current schema:\n {ansible_module.params['devices']}"
        )

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)
    cv_validation = CvValidationTools(
        cv_connection=cv_client, ansible_module=ansible_module
    )
    ansible_response: CvAnsibleResponse = cv_validation.manager(
        devices=ansible_module.params["devices"],
        validate_mode=ansible_module.params["validate_mode"],
    )

    result = ansible_response.content
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
