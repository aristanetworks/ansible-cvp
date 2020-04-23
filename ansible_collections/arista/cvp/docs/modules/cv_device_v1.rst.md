# cv\_device\_v1

Provision, Reset, or Update CloudVision Portal Devices.

Module added in version 2.9

<div class="contents" data-local="" data-depth="2">

</div>

## Synopsis

CloudVison Portal Device compares the list of Devices in in devices
against cvp-facts then adds, resets, or updates them as appropriate. If
a device is in cvp\_facts but not in devices it will be reset to factory
defaults If a device is in devices but not in cvp\_facts it will be
provisioned If a device is in both devices and cvp\_facts its configlets
and imageBundles will be compared and updated with the version in
devices if the two are different.

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
<td>cvp_facts<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>Facts from CVP collected by cv_facts module</div>
</td>
</tr>

<tr>
<td>device_filter<br/><div style="font-size: small;"></div></td>
<td>list</td>
<td>no</td>
<td>[&#x27;none&#x27;]</td>
<td></td>
<td>
    <div>Filter to apply intended mode on a set of configlet. If not used, then module only uses ADD mode. device_filter list devices that can be modified or deleted based on configlets entries.</div>
</td>
</tr>

<tr>
<td>devices<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>Yaml dictionary to describe intended devices configuration from CVP stand point.</div>
</td>
</tr>

<tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>present</td>
<td><ul><li>present</li><li>absent</li></ul></td>
<td>
    <div>If absent, devices will be removed from CVP and moved back to undefined.</div>
    <div>If present, devices will be configured or updated.</div>
</td>
</tr>

</table>
</br>

## Examples:

    ---
    - name: Test cv_device
      hosts: cvp
      connection: local
      gather_facts: no
      collections:
        - arista.cvp
      vars:
        configlet_list:
          cv_device_test01: "alias a{{ 999 | random }} show version"
          cv_device_test02: "alias a{{ 999 | random }} show version"
        # Device inventory for provision activity: bind configlet
        devices_inventory:
          veos01:
            name: veos01
            configlets:
              - cv_device_test01
              - SYS_TelemetryBuilderV2_172.23.0.2_1
              - veos01-basic-configuration
              - SYS_TelemetryBuilderV2
      tasks:
          # Collect CVP Facts as init process
        - name: "Gather CVP facts from {{inventory_hostname}}"
          cv_facts:
          register: cvp_facts
          tags:
            - always
    
        - name: "Configure devices on {{inventory_hostname}}"
          tags:
            - provision
          cv_device:
            devices: "{{devices_inventory}}"
            cvp_facts: '{{cvp_facts.ansible_facts}}'
            device_filter: ['veos']
          register: cvp_device

### Author

  - EMEA AS Team (@aristanetworks)

### Status

This module is flagged as **preview** which means that it is not
guaranteed to have a backwards compatible interface.
