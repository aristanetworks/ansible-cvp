# cv_task_v3

Execute or Cancel CVP Tasks.

Module added in version 3.0.0
## Synopsis

CloudVision Portal Task module to action pending tasks on CloudVision

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| tasks  |   list | True  |  | | CVP taskIDs to act on |
| state  |   str | False  |  executed  | <ul> <li>executed</li>  <li>cancelled</li> </ul> | Action to carry out on the task. |


## Examples

```yaml

---
- name: Execute all tasks registered in cvp_configlets variable
  arista.cvp.cv_task_v3:
    tasks: "{{ cvp_configlets.taskIds }}"

- name: Cancel a list of pending tasks
  arista.cvp.cv_task_v3:
    tasks: ['666', '667']
    state: cancelled

```

## Author

Ansible Arista Team (@aristanetworks)

