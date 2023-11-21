#!/usr/bin/python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: cv_change_control_v3
version_added: 3.4.0
author: Ansible Arista Team (@aristanetworks)
short_description: Change Control management with CloudVision
description:
  - CloudVision Portal change control module.
options:
  name:
    description: The name of the change control. If not provided, one will be generated automatically.
    required: false
    type: str
  change:
    description: A dictionary containing the change control to be created/modified.
    required: false
    type: dict
  state:
    description: Set if we should get, set/update, or remove the change control.
    required: false
    default: 'show'
    choices: ['show', 'set', 'remove', 'approve', 'unapprove', 'execute',
              'schedule', 'approve_and_execute', 'schedule_and_approve']
    type: str
  change_id:
    description: List of change IDs to get/remove.
    required: false
    type: list
    elements: str
  schedule_time:
    description: RFC3339 time format, e.g., `2021-12-23T02:07:00.0`.
    required: false
    type: str
'''

EXAMPLES = r'''
---
- name: CVP Change Control Tests
  hosts: cv_server
  gather_facts: no
  vars:
    ansible_command_timeout: 1200
    ansible_connect_timeout: 600
    change:
      name: Ansible playbook test change
      notes: Created via playbook
      activities:
        - action: "Switch Healthcheck"
          name: Switch1_healthcheck
          arguments:
            - name: DeviceID
              value: <device serial number>
          stage: Pre-Checks
        - action: "Switch Healthcheck"
          name: Switch2_healthcheck
          arguments:
            - name: DeviceID
              value: <device serial number>
          stage: Pre-Checks
        - task_id: "20"
          stage: Leaf1a_upgrade
        - task_id: "22"
          stage: Leaf1b_upgrade
      stages:
        - name: Pre-Checks
          mode: parallel
        - name: Upgrades
          modes: series
        - name: Leaf1a_upgrade
          parent: Upgrades
        - name: Leaf1b_upgrade
          parent: Upgrades

  tasks:
    - name: "Gather CVP change controls {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: show
      register: cv_facts

    - name: "Print out all change controls from {{inventory_hostname}}"
      debug:
        msg: "{{cv_facts}}"


    - name: "Check CC structure"
      debug:
        msg: "{{change}}"


    - name: "Create a change control on {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: set
        change: "{{ change }}"
      register: cv_change_control

    - name: "Get the created change control {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: show
        name: change.name
      register: cv_facts

    - name: "Show the created CC from {{inventory_hostname}}"
      debug:
        msg: "{{cv_facts}}"


    - name: "Delete the CC from {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: remove
        name: "{{change.name}}"
      register: cv_deleted

    - name: "Show deleted CCs"
      debug:
        msg: "{{cv_deleted}}"

    - name: "Approve a change control on {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: approve
        change_id: ["{{ cv_change_control.data.id }}"]

    - name: "Execute a change control on {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: execute
        change_id: ["{{ cv_change_control.data.id }}"]

'''

# Required by Ansible and CVP
import logging
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils import tools_cv
from ansible_collections.arista.cvp.plugins.module_utils.change_tools import CvChangeControlTools, CvChangeControlInput

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_change_control_v3')
MODULE_LOGGER.info('Start cv_change_control_v3 module execution')


def main():
    """
    main entry point for module execution.
    """
    # TODO - ansible module prefers constructor over literal
    #        for dict
    # pylint: disable=use-dict-literal
    argument_spec = dict(
        name=dict(type='str'),
        change=dict(type='dict'),
        state=dict(default='show', type='str',
                   choices=['show', 'set', 'remove', 'approve', 'unapprove', 'execute',
                            'schedule', 'approve_and_execute', 'schedule_and_approve']),
        change_id=dict(type='list', elements='str'),
        schedule_time=dict(type='str')
    )

    ansible_module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    # Instantiate ansible results
    result = dict(changed=False, data={}, failed=False)
    warnings = []

    MODULE_LOGGER.info('starting module cv_change_control_v3')
    if ansible_module.check_mode:
        MODULE_LOGGER.warning('! check_mode is enable')
        # module.exit_json(changed=True)

    if ansible_module.params['change']:
        user_change = CvChangeControlInput(ansible_module.params['change'])
        if user_change.is_valid is False:
            ansible_module.fail_json(msg=f"Error, your input is not valid against current schema:\n {ansible_module.params['change']}")

    if not tools_cv.HAS_CVPRAC:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac'
        )

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    result = dict(changed=False)

    # Instantiate the image class
    cv_cc = CvChangeControlTools(
        cv_connection=cv_client,
        ansible_module=ansible_module,
        check_mode=ansible_module.check_mode
    )

    MODULE_LOGGER.debug("Calling module action")
    result['changed'], result['data'], warnings = cv_cc.module_action(**ansible_module.params)
    MODULE_LOGGER.warning(warnings)

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
