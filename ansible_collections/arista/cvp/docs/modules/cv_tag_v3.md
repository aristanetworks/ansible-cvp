<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_tag_v3

Create/Assign/Delete/Unassign tags on CVP

Module added in version 3.4.0
## Synopsis

CloudVision Portal Tag module to Create/Assign/Delete/Unassign tags on CloudVision

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| tags  |   list | True  |  | | List of CVP tags. |
| mode  |   str | False  |  | <ul> <li>create</li>  <li>delete</li>  <li>assign</li>  <li>unassign</li> </ul> | Action to carry out on the tags. |
| auto_create  |   bool | False  |  True  | | Automatically create tags before assigning. |

## Inputs

For a full view of the module inputs, please see the [schema documentation](../schema/cv_tag_v3.md).

## Examples

```yaml

# Create and assign device and interface tags to multiple devices and interfaces
- name: cv_tag_v3 example1
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device: leaf1
        device_tags:
          - name: tag1
            value: value1
          - name: tag2
            value: value2
          - name: tag3
            value: value3
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
              - name: tag2i
                value: value2i
          - interface: Ethernet2
            tags:
              - name: tag1i
                value: value1i
              - name: tag2i
                value: value2i
      - device: spine1
        device_tags:
          - name: DC
            value: Dublin
          - name: rack
            value: rackA
          - name: pod
            value: podA
        interface_tags:
          - interface: Ethernet3
            tags:
              - name: tag3i
                value: value3i
              - name: tag4i
                value: value4i
          - interface: Ethernet4
            tags:
              - name: tag5i
                value: value6i
              - name: tag6i
                value: value6i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: assign
        auto_create: true

# Delete device and interface tags using device_id
- name: cv_tag_v3 example2
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device_id: JPE123435
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: delete

# Create device and interface tags (without assigning to the devices) using device_id
- name: cv_tag_v3 example3
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device_id: JPE123435
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: create

# Assign device and interface tags
- name: cv_tag_v3 example4
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device: leaf1
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: assign

# Unassign device and interface tags
- name: cv_tag_v3 example5
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device: leaf1
        device_tags:
          - name: tag1
            value: value1
        interface_tags:
          - interface: Ethernet1
            tags:
              - name: tag1i
                value: value1i
  tasks:
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: assign

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_tag_v3.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
