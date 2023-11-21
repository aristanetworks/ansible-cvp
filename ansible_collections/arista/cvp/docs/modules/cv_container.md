<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_container

Manage Provisioning topology.

Module added in version 1.0.0
## Synopsis

CloudVision Portal Configlet configuration requires a dictionary of containers with their parent, to create and delete containers on CVP side.
Returns number of created and/or deleted containers

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| topology  |   dict | True  |  | | Yaml dictionary to describe intended containers. |
| cvp_facts  |   dict | True  |  | | Facts from CVP collected by cv_facts module. |
| mode  |   str | False  |  merge  | <ul> <li>merge</li>  <li>override</li>  <li>delete</li> </ul> | Allow to save topology or not. |
| configlet_filter  |   list | False  |  ['none']  | | Filter to apply intended set of configlet on containers. If not used, then module only uses ADD mode. configlet_filter list configlets that can be modified or deleted based on configlets entries. |
| options  |   dict | False  |  | | Implements the ability to create a sub-argument_spec, where the sub options of the top level argument are also validated using the attributes discussed in this section. |


## Examples

```yaml

- name: Create container topology on CVP
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    verbose: False
    containers:
        Fabric:
            parent_container: Tenant
        Spines:
            parent_container: Fabric
            configlets:
                - container_configlet
            images:
                - 4.22.0F
            devices:
                - veos01
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      cv_facts:
      register: cvp_facts
    - name: "Build Container topology on {{inventory_hostname}}"
      cv_container:
        cvp_facts: "{{cvp_facts.ansible_facts}}"
        topology: "{{containers}}"
        mode: merge
      register: CVP_CONTAINERS_RESULT

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_container.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
