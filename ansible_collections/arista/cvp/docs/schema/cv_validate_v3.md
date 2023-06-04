# Schema for cv_tag_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| validate_mode | str | Yes |  | stop_on_error<br>stop_on_warning<br>ignore | Error reporting mechanism. <br>stop_on_error - Stop when configlet validation throws an error or warning<br>stop_on_warning - Stop when configlet validation throws a warning<br>ignore - ignore errors and warning |
| device | list | Yes |  |  | CVP device information |
| &nbsp;&nbsp;&nbsp;&nbsp;device_name | str | Yes |  |  | Device name |
| &nbsp;&nbsp;&nbsp;&nbsp;search_type | str | Yes |  | fqdn<br>hostname<br>serialNumber | Search type for device_name |
| &nbsp;&nbsp;&nbsp;&nbsp;cvp_configlets | List | No |  |  | Name of CVP configlets |
| &nbsp;&nbsp;&nbsp;&nbsp;local_configlets | List | No |  |  | Name and config of configlets |
