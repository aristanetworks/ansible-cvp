# cv_container_v3

Manage Provisioning topology.

Module added in version 3.0.0
## Synopsis

CloudVision Portal Configlet configuration requires a dictionary of containers with their parent, to create and delete containers on CVP side.
Module also supports to configure configlets at container level.
Returns number of created and/or deleted containers

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| topology  |   dict | True  |  | | YAML dictionary to describe intended containers. |
| state  |   str | False  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> | Set if Ansible should build or remove devices on CloudVision. |
| apply_mode  |   str | False  |  loose  | <ul> <li>loose</li>  <li>strict</li> </ul> | Set how configlets are attached/detached to containers. If set to strict all configlets not listed in your vars will be detached. |


## Examples

```yaml

# task in loose mode (default)
- name: Create container topology on CVP
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    verbose: False
    containers:
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
    containers:
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

## Author

Ansible Arista Team (@aristanetworks)

## Full schema

Please see the [schema documentation](../schema/cv_container_v3.md).
