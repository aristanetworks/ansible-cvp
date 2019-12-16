# Collecting Facts

## Descrpition

__Module name:__ `arista.cvp.cv_facts`

This module collects facts from CloudVision platform and return a dictionary for the following elements:

- list of devices
- list of containers
- list of configlets
- list of tasks

Module comes with 2 different options to allow user to select what information to retrieve from CVP:

__Facts limitation:__

- __`facts`__: A list of facts to retrieve from CVP. it can be one or more entries from the list:
    - `devices`
    - `containers`
    - `configlets`
    - `tasks`. 
> If not specified, module will extract all this elements from CloudVision

__Facts subset__

- __`gather_subset`__: Allow user to extract an optional element from CloudVision.
    - `config`: Add device configuration in device facts. If not set, configuration is skipped. (applicable if `devices` is part of __facts__)
    - `tasks_pending`: Collect only facts from pending tasks on CloudVision. (applicable if `tasks` is part of __facts__)
    - `tasks_failed`: Collect only failed tasks information. (applicable if `tasks` is part of __facts__)
    - `tasks_all`: Collect all tasks information from CVP. (applicable if `tasks` is part of __facts__)

Module supports inactive devices and 3rd part devices: When `gather_subset: config` is defined, only devices with flag `"streamingStatus": "active"` have their configuration collected into the facts.

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

Below is a basic playbook to collect all facts:

```yaml
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      arista.cvp.cv_facts:

    - name: "Print out facts from CVP"
      debug:
        msg: "{{ansible_facts}}"
```

To only get a subset of facts with configlets:

```yaml
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      arista.cvp.cv_facts:
        facts:
          configlets

    - name: "Print out facts from CVP"
      debug:
        msg: "{{ansible_facts}}"
```

Extracting device configuration in facts:

```yaml
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      arista.cvp.cv_facts:
        facts:
          devices
        gather_subset:
          condiguration

    - name: "Print out facts from CVP"
      debug:
        msg: "{{ansible_facts}}"
```

__Result__

Below is an example of output with default parameters

```json
{
    "ansible_facts": {
        "cvp_info": {
            "appVersion": "Foster_Build_03", 
            "version": "2018.2.5"
        }, 
        "configlets": [
            {
                "name": "ANSIBLE_TESTING_CONTAINER",
                "isDefault": "no",
                "config": "alias a57 show version",
                "reconciled": false,
                "netElementCount": 3,
                "editable": true,
                "dateTimeInLongFormat": 1574944821353,
                "isDraft": false,
                "note": "## Managed by Ansible ##",
                "visible": true,
                "containerCount": 2,
                "user": "cvpadmin",
                "key": "configlet_3503_4572477104617871",
                "sslConfig": false,
                "devices": [
                    "veos01",
                    "veos02",
                    "veos03"
                ],
                "type": "Static",
                "containers": [
                    "Fabric",
                    "Leaves"
                ],
                "isAutoBuilder": ""
            }
        ],
        "containers": [
            {
                "childContainerId": null,
                "imageBundle": "",
                "name": "MLAG01",
                "factoryId": 1,
                "CreatedOn": 1574944849950,
                "parentName": "Leaves",
                "userId": null,
                "configlets": [],
                "key": "container_9007_5100829604178666",
                "CreatedBy": "cvpadmin",
                "devices": [
                    "veos01",
                    "veos02"
                ],
                "Key": "container_9007_5100829604178666",
                "parentId": "container_9005_5100826828532751",
                "Mode": "expand",
                "type": null,
                "id": 21,
                "Name": "MLAG01"
            }
        ],
        "devices": [
            {
                "memTotal": 0,
                "imageBundle": "",
                "serialNumber": "728870FA16465700865C770C620DF4DE",
                "internalVersion": "4.23.0F",
                "dcaKey": null,
                "deviceSpecificConfiglets": [
                    "SYS_TelemetryBuilderV2_172.23.0.2_1",
                    "veos01-basic-configuration",
                    "ANSIBLE_TESTING_VEOS"
                ],
                "systemMacAddress": "50:25:22:56:12:61",
                "tempAction": null,
                "deviceStatus": "Registered",
                "taskIdList": [],
                "internalBuildId": "bf140e5e-dc9b-4586-9c8e-9615c43ed837",
                "mlagEnabled": false,
                "modelName": "vEOS",
                "hostname": "veos01",
                "complianceCode": "0000",
                "version": "4.23.0F",
                "type": "netelement",
                "isDANZEnabled": false,
                "parentContainerId": "container_9007_5100829604178666",
                "status": "Registered",
                "danzEnabled": false,
                "unAuthorized": false,
                "parentContainerKey": "container_9007_5100829604178666",
                "deviceInfo": "Registered",
                "ztpMode": false,
                "bootupTimestamp": 1569848744.301779,
                "lastSyncUp": 0,
                "key": "50:25:22:56:12:61",
                "parentContainerName": "MLAG01",
                "containerName": "MLAG01",
                "domainName": "",
                "internalBuild": "bf140e5e-dc9b-4586-9c8e-9615c43ed837",
                "ipAddress": "172.23.0.2",
                "sslConfigAvailable": false,
                "fqdn": "veos01",
                "bootupTimeStamp": 1569848744.301779,
                "isMLAGEnabled": false,
                "streamingStatus": "active",
                "memFree": 0,
                "architecture": "",
                "complianceIndication": "",
                "sslEnabledByCVP": false,
                "hardwareRevision": ""
            }
        ],
        "tasks": [
            {
                "currentTaskType": "User Task",
                "newParentContainerName": "MLAG01",
                "executedOnInLongFormat": 0,
                "ccId": "",
                "dualSupervisor": false,
                "taskStatus": "ACTIVE",
                "note": "",
                "completedOnInLongFormat": 1574946580964,
                "description": "Configlet Assign: veos01",
                "createdOnInLongFormat": 1574946575919,
                "workOrderId": "445",
                "netElementId": "50:25:22:56:12:61",
                "createdBy": "cvpadmin",
                "executedBy": "",
                "workOrderUserDefinedStatus": "Pending",
                "data": {
                    "ERROR_IN_CAPTURING_RUNNING_CONFIG": "",
                    "NETELEMENT_ID": "50:25:22:56:12:61",
                    "imageBundleId": "",
                    "imageToBePushedToDevice": "",
                    "ZERO_TOUCH_REPLACEMENT": "",
                    "ERROR_IN_CAPTURING_DESIGN_CONFIG": "",
                    "designedConfigOutputIndex": "",
                    "image": "",
                    "runningConfig": "",
                    "configSnapshots": [],
                    "imageId": [],
                    "ignoreConfigletList": [],
                    "IS_AUTO_GENERATED_IN_CVP": false,
                    "commandUsedInMgmtIpVal": "",
                    "user": "",
                    "sessionUsedInMgmtIpVal": "",
                    "IS_ADD_OR_MOVE_FLOW": false,
                    "ccExecutingNode": "",
                    "preRollbackImage": "",
                    "WORKFLOW_ACTION": "Configlet Push",
                    "newparentContainerId": "container_9007_5100829604178666",
                    "APP_SESSION_ID": "",
                    "INCORRECT_CONFIG_IN_CAPTURING_DESIGN_CONFIG": "",
                    "noOfRe-Tries": 0,
                    "imageIdList": [],
                    "ccId": "",
                    "presentImageInDevice": "",
                    "configletList": [],
                    "INCORRECT_CONFIG_IN_CAPTURING_DESIGN_CONFIG_OUTPUT_INDEX": "",
                    "VIEW": "CONFIG",
                    "isRollbackFromSnapshotFlow": false,
                    "targetIpAddress": "",
                    "isRollbackTask": false,
                    "IS_CONFIG_PUSH_NEEDED": "yes",
                    "isDCAEnabled": false,
                    "currentparentContainerId": "container_9007_5100829604178666",
                    "configExistInCVP": false,
                    "config": [],
                    "designedConfig": "",
                    "extensionsRequireReboot": []
                },
                "workOrderDetails": {
                    "workOrderDetailsId": "",
                    "serialNumber": "728870FA16465700865C770C620DF4DE",
                    "workOrderId": "",
                    "netElementHostName": "veos01",
                    "netElementId": "50:25:22:56:12:61",
                    "ipAddress": "172.23.0.2"
                },
                "workOrderState": "ACTIVE",
                "taskStatusBeforeCancel": "",
                "currentTaskName": "Submit",
                "name": "",
                "templateId": "ztp",
                "workFlowDetailsId": "",
                "newParentContainerId": "container_9007_5100829604178666"
            }
        ]
    }
}
```


