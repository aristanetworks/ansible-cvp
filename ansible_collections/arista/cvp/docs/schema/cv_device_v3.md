<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Schema for cv_device_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| apply_mode | str | No | loose | loose<br>strict | Set how configlets are attached/detached on device. If set to strict all configlets not listed in your vars are detached |
| inventory_mode | str | No | strict | loose<br>strict | Define how missing devices are handled. "loose" will ignore missing devices. "strict" will fail on any missing device |
| search_key | str | No | hostname | fqdn<br>hostname<br>serialNumber | Key name to use to look for device in CloudVision |
| state | str| No | present | present<br>factory_reset<br>provisioning_reset<br>absent | Set if Ansible should build, remove devices from provisioning, fully decommission or factory reset devices on CloudVision |
| devices | List | Yes |  |  | List of devices with their container and configlets information |
| &nbsp;&nbsp;&nbsp;&nbsp;ipAddress | str | Yes |  |  | IP address of the device |
| &nbsp;&nbsp;&nbsp;&nbsp;fqdn | str | Yes |  |  | Fully Qualified Domain Name of the device.<br>This field is required along with `parentContainerName` |
| &nbsp;&nbsp;&nbsp;&nbsp;serialNumber | str | Yes |  |  | serial number of the device.<br>This field is required along with `parentContainerName` |
| &nbsp;&nbsp;&nbsp;&nbsp;systemMacAddress | str | No |  |  | MAC address of the device |
| &nbsp;&nbsp;&nbsp;&nbsp;parentContainerName | str | Yes |  |  | Name of the parent container.<br>This field is required along with either `serialNumber` or `fqdn` |
| &nbsp;&nbsp;&nbsp;&nbsp;configlets | List | No |  |  | List of configlets |
| &nbsp;&nbsp;&nbsp;&nbsp;imageBundle | str | No |  |  | Name of the image bundle applied to a container/device |
