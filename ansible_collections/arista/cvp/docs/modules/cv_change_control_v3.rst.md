# cv_change_control_v3

Change Control with Arista Cloudvision Portal

Module added in version 3.X.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVision Portal Change Control Module.


## Module-specific Options

The following options may be specified for this module:

<table border=1 cellpadding=4>

<tr>
<th class="head">parameter</th>
<th class="head">type</th>
<th class="head">required</th>
<th class="head">default</th>
<th class="head">choices</th>
<th class="head">comments</th>
</tr>

<tr>
<td>name<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>blank</td>
<td></td>
<td>
    <div>Name of the change control. If none is provided for state == set, a name will be generated based on time timestamp.</div>
</td>
</tr>

<tr>
<td>change<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>no (unless state==set)</td>
<td></td>
<td></td>
<td>
    <div>A dict containing the details of the CC</div>
</td>
</tr>

<tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>yes</td>
<td>show</td>
<td><ul><li>show</li><li>set</li><li>remove</li></ul></td>
<td>
    <div>Set will create a new CC, unless the 'key' identifying the CC is included</div>
</td>
</tr>


</table>
</br>

## Examples:

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
          device: DC1-Leaf1a
          stage: Pre-Checks
        - action: "Switch Healthcheck"
          name: Switch1b_healthcheck
          device: DC1-Leaf1b
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
      register: cv_change

    - name: "The Change created has ID {{inventory_hostname}}"
      debug:
        msg: "{{ cv_change }}"

    - name: "Updating Change notes"
      ansible.utils.update_fact:
        updates:
          - path: change.key
            value: "{{ cv_change.data.id }}"
          - path: change.notes
            value: "Change updated"
      register: updated


    - name: "Update the change control on {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: set
        change: "{{ updated.change }}"
      register: cv_change


    - name: "Get the updated change control {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: show
        name: "{{change.name}}"
      register: cv_facts

    - name: "Show the created CC from {{inventory_hostname}}"
      debug:
        msg: "{{cv_facts}}"


    - name: "Delete the CC from {{inventory_hostname}}"
      arista.cvp.cv_change_control_v3:
        state: remove
        name: "{{change.name}}"
      register: cv_deleted

### Author

-   EMEA AS Team (@aristanetworks)
