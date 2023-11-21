<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_device

Provision, Reset, or Update CloudVision Portal Devices.

Module added in version 1.0.0
## Synopsis

CloudVision Portal Device compares the list of Devices
in devices against cvp-facts then adds, resets, or updates them as appropriate.
If a device is in cvp_facts but not in devices it will be reset to factory defaults in ZTP mode
If a device is in devices but not in cvp_facts it will be provisioned
If a device is in both devices and cvp_facts its configlets and imageBundles will be compared
and updated with the version in devices if the two are different.
Warning - reset means devices will be erased and will run full ZTP process. Use this function with caution !

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| devices  |   dict | True  |  | | Yaml dictionary to describe intended devices configuration from CVP stand point. |
| cvp_facts  |   dict | True  |  | | Facts from CVP collected by cv_facts module. |
| device_filter  |   list | False  |  ['all']  | | Filter to apply intended mode on a set of configlet. If not used, then module only uses ADD mode. device_filter list devices that can be modified or deleted based on configlets entries. |
| state  |   str | False  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  <ul> <li>If absent, devices will be removed from CVP and moved back to undefined.</li>  <li>If present, devices will be configured or updated.</li> </ul> |
| configlet_mode  |   str | False  |  override  | <ul> <li>override</li>  <li>merge</li>  <li>delete</li> </ul> |  <ul> <li>If override, Add listed configlets and remove all unlisted ones.</li>  <li>If merge, Add listed configlets to device and do not touch already configured configlets.</li> </ul> |
| options  |   dict | False  |  | | Implements the ability to create a sub-argument_spec, where the sub options of the top level argument are also validated using the attributes discussed in this section. |


## Examples

```yaml

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
        parentContainername: veos01
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

    - name: "Add configlet to device on {{inventory_hostname}}"
      tags:
        - provision
      cv_device:
        devices: "{{devices_inventory}}"
        cvp_facts: '{{cvp_facts.ansible_facts}}'
        configlet_mode: merge
        device_filter: ['veos']
      register: cvp_device

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_device.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
