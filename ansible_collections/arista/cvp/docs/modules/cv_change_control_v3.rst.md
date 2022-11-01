# cv_change_control_v3

Change Control management with CloudVision

Module added in version 3.4.0

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
<td>change<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>A dict containing the change control to be created/modified</div>
</td>
</tr>

<tr>
<td>change_id<br/><div style="font-size: small;"></div></td>
<td>list</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>List of change IDs to get/remove</div>
</td>
</tr>

<tr>
<td>name<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>The name of the change control, If not provided, one will be generated automatically.</div>
</td>
</tr>

<tr>
<td>schedule_time<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>RFC3339 time format, e.g., 2021-12-23T02:07:00.0</div>
</td>
</tr>

<tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>show</td>
<td><ul><li>show</li><li>set</li><li>remove</li><li>approve</li><li>unapprove</li><li>execute</li><li>schedule</li><li>approve_and_execute</li><li>schedule_and_approve</li></ul></td>
<td>
    <div>Set if we should get, set/update, or remove the change control</div>
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

### Author

-   Ansible Arista Team (@aristanetworks)

### Full Schema

Get full schema docs [here](../../schema/cv_change_control_v3/).
