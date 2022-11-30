# Schema for cv_device_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| apply_mode | str | No | loose | loose<br>strict | Set how configlets are attached/detached on device. If set to strict all configlets not listed in your vars are detached |
| validate_mode | str | No | skip | skip<br>stop_on_warning<br>stop_on_error| Set if config validation should be stopped on warning/error and fail the playbook or continue to the next task |
| search_key | str | No | hostname | fqdn<br>hostname<br>serialNumber | Key name to use to look for device in CloudVision |
| state | str| No | present | present<br>factory_reset<br>provisioning_reset<br>absent<br>validate | Set if Ansible should build, remove devices from provisioning, fully decommission, factory reset devices on CloudVision or validate configlets against devices|
| devices | List | Yes |  |  | List of devices with their container and configlets information |
| &nbsp;&nbsp;&nbsp;&nbsp;ipAddress | str | Yes |  |  | IP address of the device |
| &nbsp;&nbsp;&nbsp;&nbsp;fqdn | str | Yes |  |  | Fully Qualified Domain Name of the device.<br>This field is required along with `parentContainerName` |
| &nbsp;&nbsp;&nbsp;&nbsp;serialNumber | str | Yes |  |  | serial number of the device.<br>This field is required along with `parentContainerName` |
| &nbsp;&nbsp;&nbsp;&nbsp;systemMacAddress | str | No |  |  | MAC address of the device |
| &nbsp;&nbsp;&nbsp;&nbsp;parentContainerName | str | Yes |  |  | Name of the parent container.<br>This field is required along with either `serialNumber` or `fqdn` |
| &nbsp;&nbsp;&nbsp;&nbsp;configlets | List | No |  |  | List of configlets |
| &nbsp;&nbsp;&nbsp;&nbsp;imageBundle | str | No |  |  | Name of the image bundle applied to a container/device |
