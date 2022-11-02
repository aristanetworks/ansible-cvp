# Configure a Change Control on CloudVision

**cv_change_control_v3** manage change controls on CloudVision:

- Create a new change control
- Modify/Update an existing change control
- Delete a change control
- Approve or Unapprove a change control
- Execute a change control
- Schedule a change control

## Module Options

- `state`: Can be one of the following: `set`, `show` or `remove`
  - `state: set`: Set Change control
  - `state: show`: List Change control
  - `state: remove`: Delete Change control
  - `state: approve`: Approve Change control
  - `state: unapprove`: Unpprove Change control
  - `state: execute`: Execute Change control
  - `state: schedule`: Schedule Change control (available only on CVP 2022.1.0 and newer or CVaaS)
  - `state: approve_and_execute`: Approve and Execute Change control
  - `state: schedule_and_approve`: Schedule and Approve Change control (available only on CVP 2022.1.0 and newer or CVaaS)
- `change`: A dict, with the structure of the change. The change dict is structured as follows:

```yaml
name: <str - Name of change control>
notes: <str - Any notes that you want to add>
stages:
 - name: <str - Name of stage>
   mode: <series | parallel>
   parent: <str - Name of parent stage>
activities:
 - name: <str - Only used internally, "task" for any tasks>
   stage: <str - The name of the Stage to assign the task to>
   task_id: <str - The WorkOrderId of the task to be executed, if this is to be a task activity>
   timeout: <int - The timeout, if this is to be a task activity - default is 900 seconds>
   action: <str - The name of the action performed (mutually exclusive to task_id and timeout)>
   arguments:
     - name: <str - Device ID>
       value: <str - Device serial number>
```

## Example

Create a change control

```yaml
- name: CVP Change Control
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

    - name: "Approve a change control on {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: approve
        change_id: ["{{ cv_change_control.data.id }}"]

    - name: "Execute a change control on {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: execute
        change_id: ["{{ cv_change_control.data.id }}"]
```
