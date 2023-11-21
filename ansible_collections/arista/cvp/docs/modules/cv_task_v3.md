<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

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

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_task_v3.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
