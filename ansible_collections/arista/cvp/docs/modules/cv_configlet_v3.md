<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_configlet_v3

Create, Delete, or Update CloudVision Portal Configlets.

Module added in version 3.0.0
## Synopsis

CloudVison Portal Configlet compares the list of configlets and config in
configlets against cvp-facts then adds, deletes, or updates
them as appropriate.
If a configlet is in cvp_facts but not in configlets it will be deleted.
If a configlet is in configlets but not in cvp_facts it will be created.
If a configlet is in both configlets and cvp_facts it configuration will
be compared and updated with the version in configlets
if the two are different.

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| configlets  |   dict | True  |  | | List of configlets to managed on CVP server. |
| configlets_notes  |   str | False  |  Managed by Ansible  | | Add a note to the configlets. |
| state  |   str | False  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  <ul> <li>If absent, configlets will be removed from CVP if not bound to a container or a device.</li>  <li>If present, configlets will be created or updated.</li> </ul> |


## Examples

```yaml

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
    - name: "Push config"
      arista.cvp.cv_configlet_v3:
        configlets: "{{configlet_list}}"
        state: present
      register: cvp_configlet

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_configlet_v3.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
