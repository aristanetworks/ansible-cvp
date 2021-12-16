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
    serialNumber: 64793E1D3DE2240F547E5964354214A4
```

### Module inputs

#### Required Inputs

- `devices`: List of devices

#### Optional inputs

- `state`: Define if module should `create / update`(default) or `reset` devices (`factory_reset`) from CV. By default it is set to `present`.
- `apply_mode`: Define how configlets configured to the devices are managed by ansible:
  - `loose` (default): Configure new configlets to device and __ignore__ configlet already configured but not listed.
  - `strict`: Configure new configlets to device and __remove__ configlet already configured but not listed.
- `search_key`: Define key to use to search for devices.
  - `hostname`: Use Hostname to get devices.
  - `fqdn`: Use Hostname + DNS to get devices.
  - `serialNumber`: Use device serial number to get devices.

!!! danger "state option"
    When set to `state: factory_reset`, ansible will generate a task to reset switches to default configuration with ZTP mode enabled.

```yaml
# Use default loose apply_mode
- name: "Configure devices on {{inventory_hostname}}"
  arista.cvp.cv_device_v3:
    devices: "{{CVP_DEVICES}}"
  register: CVP_DEVICES_RESULTS

# Use strict apply_mode
- name: "Configure devices on {{inventory_hostname}}"
  arista.cvp.cv_device_v3:
    devices: "{{CVP_DEVICES}}"
    apply_mode: strict
  register: CVP_DEVICES_RESULTS

# Use serial-number to search for devices.
- name: "Configure devices on {{inventory_hostname}}"
  arista.cvp.cv_device_v3:
    devices: "{{CVP_DEVICES}}"
    state: present
    apply_mode: loose
    search_key: serialNumber
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
    - CV-ANSIBLE-EOS01_configlet_attached - CV-EOS-ANSIBLE01
    diff: {}
    success: true
    taskIds:
    - '469'
  configlets_detached:
    changed: true
    configlets_detached_count: 1
    configlets_detached_list:
    - CV-ANSIBLE-EOS01_configlet_removed - 01DEMO-alias - 01TRAINING-alias
    diff: {}
    success: true
    taskIds:
    - '469'
  devices_deployed:
    changed: false
    devices_deployed_count: 0
    devices_deployed_list: []
    diff: {}
    success: false
    taskIds: []
  devices_moved:
    changed: false
    devices_moved_count: 0
    devices_moved_list: []
    diff: {}
    success: false
    taskIds: []
  failed: false
  success: true
  taskIds:
  - '469'
```
