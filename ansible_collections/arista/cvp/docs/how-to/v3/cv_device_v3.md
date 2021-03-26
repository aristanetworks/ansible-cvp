# Configure devices on Cloudvision

__cv_device_v3__ manage devices on CloudVision:

- Support Configlets attachment
- Support Container move during provisioning
- Support device onboarding (from undefined to any container)

## Inputs

Full documentation available in [module section](../../modules/cv_container_v3.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)

### Input variables

- Device name.
- Parent container where to move device.
- List of configlets to apply to the device.

```yaml
CVP_DEVICES:
  - fqdn: CV-ANSIBLE-EOS01
    parentContainerName: 'ANSIBLE'
    # Optional fields
    configlets:
        - '01TRAINING-01'
    systemMacAddress: '50:8d:00:e3:78:aa'
```

### Module inputs

#### Required Inputs

- `devices`: List of devices

#### Optional inputs

- `state`: Define if module should `create`(default) or `delete` devices from CV

```yaml
- name: "Configure devices on {{inventory_hostname}}"
  arista.cvp.cv_device_v3:
    devices: "{{CVP_DEVICES}}"
  register: CVP_DEVICES_RESULTS
```

## Module output

`cv_device` returns :

!!! info
    Generated tasks can be consumed directly by cv_tasks_v3.

```yaml
msg:
  changed: true
  configlets_attached:
    changed: true
    configlets_attached_count: 2
    configlets_attached_list:
    - C_configlet_attached
    diff: {}
    success: true
    taskIds:
    - '460'
  devices_deployed:
    changed: false
    devices_deployed_count: 0
    devices_deployed_list: []
    diff: {}
    success: false
    taskIds: []
  devices_moved:
    changed: true
    devices_moved_count: 1
    devices_moved_list:
    - C_to_V
    diff: {}
    success: true
    taskIds: []
  failed: false
  success: true
  taskIds:
  - '460'
```
