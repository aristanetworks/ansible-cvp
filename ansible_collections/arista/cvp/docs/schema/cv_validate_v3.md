<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Schema for cv_validate_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| validate_mode | str | Yes |  | stop_on_error<br>stop_on_warning<br>ignore | Error reporting mechanism. <br>stop_on_error - Stop when configlet validation throws an error or warning<br>stop_on_warning - Stop when configlet validation throws a warning<br>ignore - ignore errors and warning |
| devices | list | Yes |  |  | CVP device and configlet information |
| &nbsp;&nbsp;&nbsp;&nbsp;device_name | str | Yes |  |  | Device hostname, FQDN or Serial Number. Use `search_type` to identify which information has been provided |
| &nbsp;&nbsp;&nbsp;&nbsp;search_type | str | No | hostname | fqdn<br>hostname<br>serialNumber | Search type for device_name |
| &nbsp;&nbsp;&nbsp;&nbsp;cvp_configlets | List | No |  |  | Name of configlets already present on CloudVision |
| &nbsp;&nbsp;&nbsp;&nbsp;local_configlets | Dict | No |  |  | Name and config of configlets |
