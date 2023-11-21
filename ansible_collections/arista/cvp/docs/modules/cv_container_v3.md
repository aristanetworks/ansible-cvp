<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_container_v3

Manage Provisioning topology.

Module added in version 3.0.0
## Synopsis

CloudVision Portal Configlet configuration requires a dictionary of containers with their parent, to create and delete containers on CVP side.
The Module also supports assigning configlets at the container level.
Returns number of created and/or deleted containers.
With the argument `apply_mode` set to `loose` the module will only add new containers.
When `apply_mode` is set to `strict` the module will try to remove unspecified containers from CloudVision.
This will fail if the container has configlets attached to it or devices are placed in the container.

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| topology  |   dict | True  |  | | YAML dictionary to describe intended containers. |
| state  |   str | False  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> | Set if Ansible should build or remove devices on CloudVision. |
| apply_mode  |   str | False  |  loose  | <ul> <li>loose</li>  <li>strict</li> </ul> | Set how configlets are attached/detached to containers. If set to strict all configlets not listed in your vars will be detached. |

## Inputs

For a full view of the module inputs, please see the [schema documentation](../schema/cv_container_v3.md).

## Examples

```yaml

# task in loose mode (default)
- name: Create container topology on CVP
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    verbose: False
    CVP_CONTAINERS:
        Fabric:
            parentContainerName: Tenant
        Spines:
            parentContainerName: Fabric
            configlets:
                - container_configlet
  tasks:
    - name: 'running cv_container'
      arista.cvp.cv_container_v3:
        topology: "{{CVP_CONTAINERS}}"

# task in strict mode
- name: Create container topology on CVP
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    verbose: False
    CVP_CONTAINERS:
        Fabric:
            parentContainerName: Tenant
        Spines:
            parentContainerName: Fabric
            configlets:
                - container_configlet
  tasks:
    - name: 'running cv_container'
      arista.cvp.cv_container_v3:
        topology: "{{CVP_CONTAINERS}}"
        apply_mode: strict

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_container_v3.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
