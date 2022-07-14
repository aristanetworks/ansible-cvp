# Configure a Change Control on Cloudvision

__cv_change_control_v3__ manage change controls on CloudVision:

- Create a new change control
- Modify/Update an existing change control
- Delete a change control

## Module Options

 - `state`: Can be one of the following: `set`, `show` or `remove`
    - `state: set`: Set Change control
    - `state: show`: List Change control
    - `state: remove`: Delete Change control
 - `change`: A dict, with the structure of the change. The change dict is structured as follows:

 ```yaml
name: <name of change control>
notes: <Any notes that you want to add>
stages:
   - name: <name of stage>
     mode: <series | parallel>
     parent: <name of parent stage>
activities:
   - name: <only used internally, "task" for any tasks>
     task_id: <str - the WorkOrderId of the task to be executed>
     timeout: <int>
     stage: <str - the name of the Stage to assign the task to>
   - name: <only used internally>
     action: <The name of the action to be done e.g. "Switch Healthcheck">
     stage: <The name of the stage to assign the action to>
     arguments: <list of dicts, each consisting of a name, and value key>
        - name: <argument name>
          value: <argument value>
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
