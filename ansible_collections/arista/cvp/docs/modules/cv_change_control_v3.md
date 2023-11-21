<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_change_control_v3

Change Control management with CloudVision

Module added in version 3.4.0
## Synopsis

CloudVision Portal change control module.

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| name  |   str | False  |  | | The name of the change control. If not provided, one will be generated automatically. |
| change  |   dict | False  |  | | A dictionary containing the change control to be created/modified. |
| state  |   str | False  |  show  | <ul> <li>show</li>  <li>set</li>  <li>remove</li>  <li>approve</li>  <li>unapprove</li>  <li>execute</li>  <li>schedule</li>  <li>approve_and_execute</li>  <li>schedule_and_approve</li> </ul> | Set if we should get, set/update, or remove the change control. |
| change_id  |   list | False  |  | | List of change IDs to get/remove. |
| schedule_time  |   str | False  |  | | RFC3339 time format, e.g., `2021-12-23T02:07:00.0`. |

## Inputs

For a full view of the module inputs, please see the [schema documentation](../schema/cv_change_control_v3.md).

## Examples

```yaml

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


```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_change_control_v3.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
