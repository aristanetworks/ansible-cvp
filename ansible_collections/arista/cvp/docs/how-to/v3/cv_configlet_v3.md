# Configure configlets on Cloudvision (v3)

`cv_configlet_v3` manage configlets on CloudVision:

- Configlets creation
- Configlets update
- Configlets deletion

To import content from text file, leverage template rendering and then load from file: use `lookup()` command

## Inputs

Full documentation available in [module section](../../modules/cv_configlet_v3.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)

## Input variables

```yaml
CVP_CONFIGLETS:
  TEAM01-alias: "alias a1 show version"
  TEAM01-another-configlet: "alias a2 show version"
```

## Module inputs

### Mandatory Inputs

- `configlets`: List of configlets to create

### Optional inputs

- `state`: Keyword to define if we want to create(present) or delete(absent) configlets. Default is set to `present`

```yaml
---
- name: lab03 - cv_configlet lab
  hosts: CloudVision
  connection: local
  gather_facts: no
  vars:
    CVP_CONFIGLETS:
      TEAM01-alias: "alias a1 show version"
      TEAM01-another-configlet: "alias a2 show version"
  tasks:
      arista.cvp.cv_configlet_v3:
        configlets: "{{CVP_CONFIGLETS}}"
        state: present
```

## Module outputs

`cv_configlet_v3` outputs:

- List of created configlets
- List of updated configlets
- List of deleted configlets
- List of generated tasks.

!!! info
    Generated tasks can be consumed directly by cv_tasks_v3.

```yaml
msg:
  changed: true
  configlets_created:
    changed: false
    configlets_created_count: 0
    configlets_created_list: []
    diff: {}
    success: false
    taskIds: []
  configlets_deleted:
    changed: false
    configlets_deleted_count: 0
    configlets_deleted_list: []
    diff: {}
    success: false
    taskIds: []
  configlets_updated:
    changed: true
    configlets_updated_count: 2
    configlets_updated_list:
    - 01TRAINING-alias
    - 01TRAINING-01
    diff:
      01TRAINING-alias:
      - 0.9565217391304348
      - - |-
          --- CVP
        - |-
          +++ Ansible
        - |-
          @@ -1 +1 @@
        - -alias a101 show version
        - +alias a103 show version
    success: true
    taskIds:
    - '460'
  failed: false
  success: true
  taskIds:
  - '460'
```
