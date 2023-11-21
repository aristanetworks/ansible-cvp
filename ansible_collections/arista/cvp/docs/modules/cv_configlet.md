<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_configlet

Create, Delete, or Update CloudVision Portal Configlets.

Module added in version 1.0.0
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
| cvp_facts  |   dict | True  |  | | Facts extracted from CVP servers using cv_facts module. |
| configlet_filter  |   list | False  |  ['none']  | | Filter to apply intended mode on a set of configlet. If not used, then module only uses ADD mode. configlet_filter list configlets that can be modified or deleted based on configlets entries. |
| filter_mode  |   str | False  |  loose  | <ul> <li>loose</li>  <li>strict</li> </ul> |  <ul> <li>If loose, a match is when a configlet matches a substring of a configlet defined in the filter.</li>  <li>If strict, a match is when a configlet exactly matches a configlet defined in the filter.</li> </ul> |
| state  |   str | False  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  <ul> <li>If absent, configlets will be removed from CVP if they are not bound to either a container or a device.</li>  <li>If present, configlets will be created or updated.</li> </ul> |
| options  |   dict | False  |  | | Implements the ability to create a sub-argument_spec, where the sub options of the top level argument are also validated using the attributes discussed in this section. |


## Examples

```yaml

---
- name: Test cv_configlet_v2
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    configlet_list:
      Test_Configlet: "! This is a Very First Testing Configlet\n!"
      Test_DYNAMIC_Configlet: "{{ lookup('file', 'templates/configlet_'+inventory_hostname+'.txt') }}"
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      tags:
        - always
      cv_facts:
      register: cvp_facts

    - name: 'Create configlets on CVP {{inventory_hostname}}.'
      tags:
        - provision
      cv_configlet:
        cvp_facts: "{{cvp_facts.ansible_facts}}"
        configlets: "{{configlet_list}}"
        configlets_notes: "Configlet managed by Ansible"
        configlet_filter: ["New", "Test","base-chk","base-firewall"]
      register: cvp_configlet

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_configlet.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
