# Configure a Change Control on Cloudvision

__cv_change_control_v3__ manage change controls on CloudVision:

- Create a new change control
- Modify/Update an existing change control
- Delete a change control

## Module Options

 - `state`: Can be one of the following: `set`, `show` or `remove`
    - `state: set` : Set Change control
    - `state: show` : List Change control
    - `state: remove` : Delete Change control
 - `change`: A dict, with the structure of the change. The change dict is structured as follows:
    - `name`: (str) The name of the change control
    - `stages` : A list of dicts
      - `name` : (str) The name of the stage
      - `mode: <series | parallel>` : (str) This particular stage should have its actions executed in parallel or series
      - `parent` : (str) The name of the parent stage
    - `activities` : A list of dicts, containing details of the tasks or actions to be executed, and the stage they should be executed in.
      - `name` : (str) Only used internally, "task" for any tasks
      - `stage`: (str) The name of the stage that this task or action should be assigned to
      - `task_id`: (str) The WorkOrderId of the task to be executed, if this is to be a task activity
      - `timeout`: (int) The timeout, if this is to be a task activity - default is 900 seconds
      - `action`: (str) The name of the action performed (mutually exclusive to `task_id` and `timeout`)
      - `arguments`: (list) A list of dicts each consisting of `name` and `value` keys to provide the action arguments. `name: DeviceID` and `value: <device serial number` are commonly used.


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
```
