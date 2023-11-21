<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Schema for cv_change_control_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| change_id | list | No |  |  | List of change IDs to get/remove |
| name | str | No |  |  | The name of the change control, if not provided, one will be generated automatically |
| state | str | No | show | show<br>set<br>remove | Set if we should get, set/update, or remove the change control |
| change | Dict | No |  |  | A dict containing the change control to be created/modified |
| &nbsp;&nbsp;&nbsp;&nbsp;name | str | No |  |  | Name of change control |
| &nbsp;&nbsp;&nbsp;&nbsp;notes | str | No |  |  | Any notes that you want to add |
| &nbsp;&nbsp;&nbsp;&nbsp;stages | Dict | Yes |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- name | str | Yes |  |  | Name of stage |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mode | str | Yes |  | series<br>parallel | Serial or parallel execution |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parent | str | Yes |  |  | Name of parent stage |
| &nbsp;&nbsp;&nbsp;&nbsp;activities | Dict | Yes |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- name | str | Yes |  |  | Only used internally, "task" for any tasks |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stage | str | Yes |  |  | The name of the Stage to assign the task to |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;task_id | str | Yes |  |  | The WorkOrderId of the task to be executed, if this is to be a task activity |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timeout | int | No | 900 |  | The timeout, if this is to be a task activity |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action | str | Yes |  |  | The name of the action performed (mutually exclusive to task_id and timeout) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;arguments | Dict | Yes |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- name | str | Yes |  |  | Device ID |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value | str | Yes |  |  | Device serial number |
