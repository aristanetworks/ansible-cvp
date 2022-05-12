# Execute / Cancel tasks on CloudVision

__cv_tag_v3__ manage tasks on CloudVision:

- Create tag on CloudVision
- Assign tag on CloudVision
- Unassign tag on CloudVision
- Delete tag on CloudVision

## Inputs

The documentation is available in the [module section](../../modules/cv_tag_v3.rst.md).

### Input variables

- list of tags
- state (`assign` or `unassign`)
- mode (`create` or `delete`)
- auto_create (`True` or `False`). Default is `True`

### Example:

```yaml
  - hosts: CloudVision
    tasks:
      - name: create tags
        arista.cvp.cv_tag_v3:
          tags: "{{CVP_TAGS}}"
          state: assign
          mode: create
          auto_create: true
```

### Example of creating device and interface tags:

```yaml
- name: Test cv_tag_v3
  hosts: CloudVision
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
        interface_tags:
          - interface: Ethernet1/1
            tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
          - interface: Ethernet1/2
            tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
      - device: leaf2
        device_tags:
          - name: tag1
            value: value1
          - name: tag2
            value: value2
        interface_tags:
          - interface: Ethernet1/1
            tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
          - interface: Ethernet1/2
            tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
  tasks:
    - name: create tags
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        state: assign
        mode: create
        auto_create: true
```


## Module output

```yaml
actions_manager:
    actions_manager_count: 0
    actions_manager_list:
    - tag_AnsibleWorkspaceLZ7
    changed: true
    diff: {}
    success: true
    taskIds: []
  invocation:
    module_args:
      auto_create: true
      mode: create
      state: assign
      tags:
      - device: leaf1
        device_tags:
        - name: tag1
          value: value1
        - name: tag2
          value: value2
        interface_tags:
        - interface: Ethernet1/1
          tags:
          - name: tag1
            value: value1
          - name: tag2
            value: value2
        - interface: Ethernet1/2
          tags:
          - name: tag1
            value: value1
          - name: tag2
            value: value2
  success: true
  taskIds: []
```