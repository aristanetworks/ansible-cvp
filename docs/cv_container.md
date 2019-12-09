# Manage Provisionning topology

## Descrpition

__Module name:__ `arista.cvp.cv_container`

This module manage provisioning topology at container's level. it takes an intended topology, compare against facts from [`cv_facts`](cv_facts.md) and then __create__, __delete__ containers before assigning existing configlets and moving devices to containers.

## Options

Module comes with a set of options:

- `topology`: Topology to build on Cloudvision.
- `cvp_facts`: Current facts collecting on CVP by a previous task
- `save_topology`: Boolean to save and create tasks on CVP.
- `mode`: Define how module should work with container topology. Value can be:
    - `merge`: Combine the new container topology with the existing topology.
    - `override`: Discard the entire existing container topology and replace it with the new topology.
    - `delete`: Discard the entire container topology provided in `topology` and keep other existing containers untouched.

If __`mode`__ is set to __`delete`__, container topology shall be described starting from `Tenant`. A partial tree is currenly not supported.

## Usage

__Authentication__

This module uses `HTTPAPI` connection plugin for authentication. These elements shall be declared using this plugin mechanism and are automatically shared with `arista.cvp.cv_*` modules.

```ini
[development]
cvp_foster  ansible_host= 10.90.224.122 ansible_httpapi_host=10.90.224.122

[development:vars]
ansible_connection=httpapi
ansible_httpapi_use_ssl=True
ansible_httpapi_validate_certs=False
ansible_user=cvpadmin
ansible_password=ansible
ansible_network_os=eos
ansible_httpapi_port=443
```

__Inputs__

Below is a basic playbook to collect facts:

```yaml
vars:
    containers_provision:
        Fabric:
            parent_container: Tenant
        Spines:
            parent_container: Fabric
        Leaves:
            parent_container: Fabric
            configlets:
                - alias
            devices:
            - veos03
        MLAG01:
            parent_container: Leaves
            devices:
            - veos01
            - veos02
tasks:
    - name: "Gather CVP facts from {{inventory_hostname}}"
      arista.cvp.cv_facts:
      register: cvp_facts
      tags:
        - always

    - name: "Build Container topology on {{inventory_hostname}}"
      arista.cvp.cv_container:
        topology: '{{containers_provision}}'
        cvp_facts: '{{cvp_facts.ansible_facts}}'
        save_topology: true
        mode: merge
```

__Result__

Below is an example of expected output

```json
{
    "changed": false,
    "data": {
        "attached_configlet": {
            "configlet_attached": 4,
            "list": [
                [
                    {
                        "config": "alias v10 show version",
                        "containers": [],
                        "devices": [],
                        "key": "configlet_885_1325820320363417",
                        "name": "alias",
                        "type": "Static"
                    }
                ]
            ],
            "taskIds": [
                "127"
            ]
        },
        "changed": true,
        "creation_result": {
            "containers_created": "4"
        },
        "deletion_result": {
            "containers_deleted": "1"
        },
        "moved_result": {
            "devices_moved": 3,
            "list": [
                "veos01",
                "veos02",
                "veos03"
            ],
            "taskIds": [
                "125",
                "126",
                "127"
            ]
        },
        "tasks": [
            {
                "ccId": "",
                "completedOnInLongFormat": 1571674207598,
                "createdBy": "cvpadmin",
                "createdOnInLongFormat": 1571674202552,
                "currentTaskName": "Submit",
                "currentTaskType": "User Task",
                "data": {
                    "APP_SESSION_ID": "",
                    "ERROR_IN_CAPTURING_DESIGN_CONFIG": "",
                    "ERROR_IN_CAPTURING_RUNNING_CONFIG": "",
                    "INCORRECT_CONFIG_IN_CAPTURING_DESIGN_CONFIG": "",
                    "INCORRECT_CONFIG_IN_CAPTURING_DESIGN_CONFIG_OUTPUT_INDEX": "",
                    "IS_ADD_OR_MOVE_FLOW": true,
                    "IS_AUTO_GENERATED_IN_CVP": false,
                    "IS_CONFIG_PUSH_NEEDED": "yes",
                    "NETELEMENT_ID": "50:25:22:56:12:61",
                    "VIEW": "CONFIG",
                    "WORKFLOW_ACTION": "Configlet Push",
                    "ZERO_TOUCH_REPLACEMENT": "",
                    "ccExecutingNode": "",
                    "ccId": "",
                    "commandUsedInMgmtIpVal": "",
                    "config": [],
                    "configExistInCVP": false,
                    "configSnapshots": [],
                    "configletList": [],
                    "currentparentContainerId": "container_1401_1830045226427188",
                    "designedConfig": "",
                    "designedConfigOutputIndex": "",
                    "extensionsRequireReboot": [],
                    "ignoreConfigletList": [],
                    "image": "",
                    "imageBundleId": "",
                    "imageId": [],
                    "imageIdList": [],
                    "imageToBePushedToDevice": "",
                    "isDCAEnabled": false,
                    "isRollbackFromSnapshotFlow": false,
                    "isRollbackTask": false,
                    "newparentContainerId": "container_1436_1830170147175295",
                    "noOfRe-Tries": 0,
                    "preRollbackImage": "",
                    "presentImageInDevice": "",
                    "runningConfig": "",
                    "sessionUsedInMgmtIpVal": "",
                    "targetIpAddress": "",
                    "user": ""
                },
                "description": "Configlet Assign from Container Move: veos01",
                "dualSupervisor": false,
                "executedBy": "",
                "executedOnInLongFormat": 0,
                "name": "",
                "netElementId": "50:25:22:56:12:61",
                "newParentContainerId": "container_1436_1830170147175295",
                "newParentContainerName": "MLAG01",
                "note": "",
                "taskStatus": "ACTIVE",
                "taskStatusBeforeCancel": "",
                "templateId": "ztp",
                "workFlowDetailsId": "",
                "workOrderDetails": {
                    "ipAddress": "172.23.0.2",
                    "netElementHostName": "veos01",
                    "netElementId": "50:25:22:56:12:61",
                    "serialNumber": "728870FA16465700865C770C620DF4DE",
                    "workOrderDetailsId": "",
                    "workOrderId": ""
                },
                "workOrderId": "125",
                "workOrderState": "ACTIVE",
                "workOrderUserDefinedStatus": "Pending"
            }
        ]
    },
    "failed": false
}
```


