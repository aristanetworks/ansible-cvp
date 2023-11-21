<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_device_v3

Manage Provisioning topology.

Module added in version 3.0.0
## Synopsis

CloudVision Portal Configlet configuration requires a dictionary of containers with their parent, to create and delete containers on CVP side.
Returns number of created and/or deleted containers

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| devices  |   list | True  |  | | List of devices with their container, configlet, and image bundle information. |
| state  |   str | False  |  present  | <ul> <li>present</li>  <li>factory_reset</li>  <li>provisioning_reset</li>  <li>absent</li> </ul> | Set if Ansible should build, remove devices from provisioning, fully decommission or factory reset devices on CloudVision. |
| apply_mode  |   str | False  |  loose  | <ul> <li>loose</li>  <li>strict</li> </ul> | Set how configlets are attached/detached on device. If set to strict, all configlets and image bundles not listed in your vars are detached. |
| inventory_mode  |   str | False  |  strict  | <ul> <li>loose</li>  <li>strict</li> </ul> | Define how missing devices are handled. "loose" will ignore missing devices. "strict" will fail on any missing device. |
| search_key  |   str | False  |  hostname  | <ul> <li>fqdn</li>  <li>hostname</li>  <li>serialNumber</li> </ul> | Key name to use to look for device in CloudVision. |

## Inputs

For a full view of the module inputs, please see the [schema documentation](../schema/cv_device_v3.md).

## Examples

```yaml

# task in loose apply_mode using fqdn (default)
- name: Device Management in CloudVision
  hosts: cv_server
  connection: local
  gather_facts: false
  collections:
    - arista.cvp
  vars:
    CVP_DEVICES:
      - fqdn: CV-ANSIBLE-EOS01
        parentContainerName: ANSIBLE
        configlets:
            - 'CV-EOS-ANSIBLE01'
        imageBundle: leaf_image_bundle
  tasks:
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: present
        search_key: fqdn

# task in loose apply_mode and loose inventory_mode using fqdn (default)
- name: Device Management in CloudVision
  hosts: cv_server
  connection: local
  gather_facts: false
  collections:
    - arista.cvp
  vars:
    CVP_DEVICES:
      - fqdn: NON-EXISTING-DEVICE
        parentContainerName: ANSIBLE
        configlets:
            - 'CV-EOS-ANSIBLE01'
        imageBundle: leaf_image_bundle
  tasks:
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: present
        search_key: fqdn
        inventory_mode: loose


# task in loose apply_mode using serial
- name: Device Management in CloudVision
  hosts: cv_server
  connection: local
  gather_facts: false
  collections:
    - arista.cvp
  vars:
    CVP_DEVICES:
      - serialNumber: xxxxxxxxxxxx
        parentContainerName: ANSIBLE
        configlets:
            - 'CV-EOS-ANSIBLE01'
  tasks:
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: present
        search_key: serialNumber

# task in strict apply_mode
- name: Device Management in CloudVision
  hosts: cv_server
  connection: local
  gather_facts: false
  collections:
    - arista.cvp
  vars:
    CVP_DEVICES:
      - fqdn: CV-ANSIBLE-EOS01
        parentContainerName: ANSIBLE
        configlets:
            - 'CV-EOS-ANSIBLE01'
  tasks:
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: present
        apply_mode: strict

# Decommission devices (remove from both provisioning and telemetry)
- name: Decommission device
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - fqdn: leaf1
        parentContainerName: ""
  tasks:
  - name: decommission device
    arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: absent

# Remove a device from provisioning
# Post 2021.3.0 the device will be automatically re-registered and moved to the Undefined container
- name: Remove device
  hosts: CVP
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - fqdn: leaf2
        parentContainerName: ""
  tasks:
  - name: remove device
    arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: provisioning_reset

# Factory reset a device (moves the device to ZTP mode)
- name: Factory reset device
  hosts: CVP
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - fqdn: leaf2
        parentContainerName: ""
  tasks:
  - name: remove device
    arista.cvp.cv_device_v3:
        devices: '{{CVP_DEVICES}}'
        state: factory_reset

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_device_v3.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
