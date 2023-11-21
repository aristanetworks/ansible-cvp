<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Schema for cv_tag_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| auto_create | bool | No | True | Yes<br> No | auto_create tags before assigning |
| mode | str | No |  | create<br>delete<br>assign<br>unassign | action to carry out on the tags. <br>create - create tags<br>delete - delete tags<br>assign - assign existing tags on device<br>unassign - unassign existing tags from device |
| tags | list | Yes |  |  | CVP tags |
| &nbsp;&nbsp;&nbsp;&nbsp;device | str | No |  |  | device to assign tags to |
| &nbsp;&nbsp;&nbsp;&nbsp;device_id | str | No |  |  | serial number of the device to assign tags to |
| &nbsp;&nbsp;&nbsp;&nbsp;device_tags | List | No |  |  | device tags |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- name | str | Yes |  |  | name of tag |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value |  str | Yes |  |  | value of tag |
| &nbsp;&nbsp;&nbsp;&nbsp;interface_tags | List | No |  |  | interface tags |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interface | str | No |  |  | Interface to apply tags on |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tags | List | No |  |  | interface tags |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- name | str | Yes |  |  | name of tag |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value |  str | Yes |  |  | value of tag |
