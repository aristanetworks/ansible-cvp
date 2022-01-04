# cv_configlet_v3

Create, Delete, or Update CloudVision Portal Configlets.

Module added in version 3.0.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVison Portal Configlet compares the list of configlets and config
in configlets against cvp-facts then adds, deletes, or updates them as
appropriate. If a configlet is in cvp_facts but not in configlets it
will be deleted. If a configlet is in configlets but not in cvp_facts it
will be created. If a configlet is in both configlets and cvp_facts it
configuration will be compared and updated with the version in
configlets if the two are different.

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
<td>configlets<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>List of configlets to managed on CVP server.</div>
</td>
</tr>

<tr>
<td>configlets_notes<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>Managed by Ansible</td>
<td></td>
<td>
    <div>Add a note to the configlets.</div>
</td>
</tr>

<tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>present</td>
<td><ul><li>present</li><li>absent</li></ul></td>
<td>
    <div>If absent, configlets will be removed from CVP if they are not bound</div>
    <div>to either a container or a device.</div>
    <div>If present, configlets will be created or updated.</div>
</td>
</tr>

</table>
</br>

## Examples:

    ---
    - name: Test cv_configlet_v3
      hosts: cvp
      connection: local
      gather_facts: no
      vars:
        configlet_list:
          Test_Configlet: "! This is a Very First Testing Configlet\n!"
          Test_DYNAMIC_Configlet: "{{ lookup('file', 'templates/configlet_'+inventory_hostname+'.txt') }}"
      tasks:
        - name: 'Create configlets on CVP {{inventory_hostname}}.'
          tags:
            - provision
          cv_configlet:
            configlets: "{{configlet_list}}"
            configlets_notes: "Configlet managed by Ansible"
          register: cvp_configlet

### Author

-   EMEA AS Team (@aristanetworks)
