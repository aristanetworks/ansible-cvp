# Configure container on Cloudvision (v3)

__cv_container_v3__ manages containers on CloudVision:

- Supports creation/deletion of containers
- Supports devices binding to containers
- Supports configlets binding to containers

## Inputs

Full documentation available in [module section](../../modules/cv_container_v3.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi).

### Input variables

- Container Name
- Parent container where to create container
- Optional list of configlets to attach to container:
  - Configlets must be created previously

```yaml
---
CVP_CONTAINERS:
  TEAM01:
    parentContainerName: Tenant
  TEAM01_DC:
    parentContainerName: TEAM01
  TEAM01_LEAFS:
    parentContainerName: TEAM01_DC
    configlets:
      - GLOBAL-ALIASES
```

### Module inputs

#### Required Inputs

- `topology`: Container topology

#### Optional inputs

- `state`: Keyword to define if we want to create(present) or delete(absent) configlets. Default is set to `present`

```yaml
- name: lab04 - cv_container lab
  hosts: CloudVision
  connection: local
  gather_facts: no
  tasks:
    - name: "Configure containers on {{inventory_hostname}}"
      arista.cvp.cv_container_v3:
        topology: "{{CVP_CONTAINERS}}"
```

## Module output

`cv_container_v3` returns :

- List of created containers
- List of deleted containers
- List of moved devices
- List of attached configlets
- List of CV tasks generated

!!! info
    Generated tasks can be consumed directly by cv_tasks_v3.

```yaml
msg:
  changed: true
  configlet_attachmenet:
    changed: true
    configlet_attachmenet_count: 0
    configlet_attachmenet_list:
    - Spines:01TRAINING-01
    diff: {}
    success: true
    taskIds: []
  container_added:
    changed: true
    container_added_count: 4
    container_added_list:
    - DC2
    - Leafs
    - Spines
    - POD01
    diff: {}
    success: true
    taskIds: []
  container_deleted:
    changed: false
    container_deleted_count: 0
    container_deleted_list: []
    diff: {}
    success: false
    taskIds: []
  failed: false
  success: true
  taskIds: []
```
