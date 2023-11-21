<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_task

Execute or Cancel CVP Tasks.

Module added in version 1.0.0
## Synopsis

CloudVision Portal Task module

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| tasks  |   list | True  |  | | CVP taskIDs to act on. |
| wait  |   int | False  |  0  | | Time to wait for tasks to transition to 'Completed.' |
| state  |   str | False  |  executed  | <ul> <li>executed</li>  <li>cancelled</li> </ul> | Action to carry out on the task. |
| options  |   dict | False  |  | | Implements the ability to create a sub-argument_spec, where the sub options of the top level argument are also validated using the attributes discussed in this section. |


## Examples

```yaml

---
- name: Execute all tasks registered in cvp_configlets variable
  arista.cvp.cv_task:
    tasks: "{{ cvp_configlets.data.tasks }}"

- name: Cancel a list of pending tasks
  arista.cvp.cv_task:
    tasks: "{{ cvp_configlets.data.tasks }}"
    state: cancelled

# Execute all pending tasks and wait for completion for 60 seconds
# In order to get a list of all pending tasks, execute cv_facts first
- name: Update cvp facts
  arista.cvp.cv_facts:

- name: Execute all pending tasks and wait for completion for 60 seconds
  arista.cvp.cv_task:
    port: '{{cvp_port}}'
    tasks: "{{ tasks }}"
    wait: 60

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).


## Author

Ansible Arista Team (@aristanetworks)
