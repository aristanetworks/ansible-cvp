# Configure container on Cloudvision (v3)

__cv_container_v3__ manages containers on CloudVision. It supports:

- Creation and deletion of containers
- Configlets binding to containers

## Inputs

Full documentation available in [module section](../../modules/cv_container_v3.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi).

### Input variables

- Container name
- Parent container name
- Optional list of configlets to attach to container
  - The configlets must exist on the CVP server

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

- `state`: Keyword to define if we want to create (present) or delete (absent) the containers. Default is set to `present`.
- `apply_mode`: Define how configlets configured to the containers are managed by ansible:
  - `loose` (default): Configure new configlets to containers and __ignore__ configlet already configured but not listed.
  - `strict`: Configure new configlets to containers and __remove__ configlet already configured but not listed.


```yaml
- name: lab04 - cv_container lab
  hosts: CloudVision
  connection: local
  gather_facts: no
  tasks:
    - name: "Configure containers on {{inventory_hostname}}"
      arista.cvp.cv_container_v3:
        topology: "{{CVP_CONTAINERS}}"
        state: present
        apply_mode: loose
```

## Module output

`cv_container_v3` returns the list of:

- attached configlets
- detached configlets
- created containers
- deleted containers
- CV tasks generated

!!! info
    Generated tasks can be consumed directly by cv_tasks_v3.

```yaml
  msg:
    changed: true
    configlets_attached:
      changed: true
      configlets_attached_count: 0
      configlets_attached_list:
      - TEAM01_LEAFS:GLOBAL-ALIASES
      diff: {}
      success: true
      taskIds:
      - '565'
    configlets_detached:
      changed: false
      configlets_detached_count: 0
      configlets_detached_list: []
      diff: {}
      success: true
      taskIds: []
    container_added:
      changed: false
      container_added_count: 0
      container_added_list: []
      diff: {}
      success: false
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
    taskIds:
    - '565'
```
