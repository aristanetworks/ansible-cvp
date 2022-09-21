# Tag management on CloudVision

**cv_tag_v3** manage tags on CloudVision:

- Create tag on CloudVision
- Assign tag on CloudVision
- Unassign tag on CloudVision
- Delete tag on CloudVision

## Inputs

The documentation is available in the [module section](../../modules/cv_tag_v3.rst.md).

### Input variables

- list of tags
- mode (`create`, `delete`, `assign`, `unassign`)
- auto_create (`True` or `False`). Default is `True`

### Example

```yaml
  - hosts: CloudVision
    tasks:
      - name: create tags
        arista.cvp.cv_tag_v3:
          tags: "{{CVP_TAGS}}"
          mode: create
          auto_create: true
```

### Example of creating device and interface tags

```yaml
- name: Test cv_tag_v3
  hosts: CloudVision
  connection: local
  gather_facts: no
  vars:
    CVP_TAGS:
      - device_tags:
          - name: tag1
            value: value1
          - name: tag2
            value: value2
        interface_tags:
          - tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
          - tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
  tasks:
    - name: create tags
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: create
        auto_create: true
```

### Example of assigning device and interface tags

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
          - interface: Ethernet1
            tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
          - interface: Ethernet2
            tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
  tasks:
    - name: create tags
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: assign
        auto_create: true
```

## Actions

| Mode              |   auto_create: true   |   auto_create: false   |
|-------------------|-----------------------|------------------------|
| assign            |Create tag and assign tag to <br>device. `device` field needed | Assign tag to device. <br>`device` field needed |
| unassign          | Unassign tag. <br>`device` field needed | Unassign tag. <br>`device` field needed |
| create            | Create tag | Create tag |
| delete | Delete tag | Delete tag |

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
