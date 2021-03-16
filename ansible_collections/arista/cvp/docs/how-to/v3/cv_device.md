# Configure devices on Cloudvision

cv_device manage devices on CloudVision:

- Support Configlets attachment
- Support Container move during provisioning
- Support device reset if required

`cv_device` bases its actions on cv_facts results

The `cv_device` actions are based on cv_facts results:

- Use intend approach
- No declarative action

## Inputs

Full documentation available in [module section](../modules/cv_container.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)

### Input variables

- Device name.
- Parent container where to move device.
- List of configlets to apply to the device.

```yaml
CVP_DEVICES:
   TEAM01-SPINE1:
      name: TEAM01-SPINE1
      parent_container : STAGING
      configlets:
         - TEAM01-SPINE1
      imageBundle: [] # Not yet supported
  TEAM02-SPINE1:
    name: TEAM02-SPINE1
    parent_container: STAGING
    configlets:
      - TEAM02-SPINE1
    imageBundle: [] # Not yet supporte
```

### Module inputs

#### Required Inputs

- `cvp_facts`: Facts from cv_facts
- `devices`: List of devices
- `device_filter`: Filter to only target devices as defined in list.

#### Optional inputs

- `state`: Define if module should `create`(default) or `delete` devices from CV

```yaml
- name: "Configure devices on {{inventory_hostname}}"
  arista.cvp.cv_device:
    devices: "{{CVP_DEVICES}}"
    cvp_facts: '{{CVP_FACTS.ansible_facts}}'
    device_filter: ['TEAM']
    state: present
  register: CVP_DEVICES_RESULTS
```

## Module output

`cv_device` returns :

> Generated tasks can be consumed directly by cv_tasks.

```json
{
    "msg": {
        "changed": true,
        "data": {
            "new": [],
            "reset": [],
            "tasks": [
                {
                    "currentTaskName": "Submit",
                    "description": "Ansible Configlet Update: on Device TEAM01-SPINE1",
                    "note": "",
                    "taskStatus": "ACTIVE",
                    "workOrderDetails": {
                        "ipAddress": "10.255.0.11",
                        "netElementHostName": "TEAM01-SPINE1",
                        "netElementId": "0c:1a:c1:ed:98:18",
                        "serialNumber": "6B25F852A3A3036E1ADBB4423F1E62EF",
                        "workOrderDetailsId": "",
                        "workOrderId": ""
                    },
                    "workOrderId": "8",
                    "workOrderState": "ACTIVE",
                    "workOrderUserDefinedStatus": "Pending"
                }
            ],
            "updated": [
                {
                    "TEAM01-SPINE1": "Configlets-[u'8']"
                },
                {
                    "TEAM01-SPINE1": "Device TEAM01-SPINE1 \
imageBundle cannot be updated - Exception: imageBundle_key \
check: No imageBundle specified"
                }
            ]
        },
        "failed": false
    }
}
```
