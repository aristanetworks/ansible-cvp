# Collecting Facts

## Descrpition

__Module name:__ `cv_facts`

This module collects facts from CloudVision platform and return a dictionary for the following elements:

- list of devices
- list of containers
- list of configlets
- list of tasks

## Options

Module comes with a set of options:

- `host`: IP address of CVP server
- `protocol`: Which protocol to use to connect to CVP. Can be either `http` or `https` (default: `https`)
- `port`: Port where CVP is listening. (default: based on `protocol`)
- `username`: user to use to connect to CVP
- `password`: password to use to connect to CVP

## Usage

__Inputs__

Below is a basic playbook to collect facts:

```yaml
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      cv_facts:
        host: '{{ansible_host}}'
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        protocol: https
        port: '{{cvp_port}}'
    - name: "Print out facts from CVP"
      debug:
        msg: "{{ansible_facts}}"
```

__Result__

Below is an example of expected output

```json
{
    "ansible_facts": {
        "cvp_info": {
            "appVersion": "Foster_Build_03", 
            "version": "2018.2.5"
        }, 
        "configlets": [
            {
                "config": "alias v10 show version\n", 
                "containers": [], 
                "devices": [
                    "veos01"
                ], 
                "key": "configlet_1065_1398913896328423", 
                "name": "RECONCILE_172.23.0.2", 
                "type": "Static"
            } 
        ],
        "containers": [
            {
                "childContainerKey": null, 
                "configlets": [], 
                "devices": [], 
                "imageBundle": "", 
                "key": "root", 
                "name": "Tenant", 
                "parentName": null
            }, 
            {
                "childContainerKey": null, 
                "configlets": [], 
                "devices": [], 
                "imageBundle": "", 
                "key": "container_1306_1487093442541759", 
                "name": "Fabric", 
                "parentName": "Tenant"
            },
        ],
        "devices": [
            {
                "complianceCode": "0000", 
                "complianceIndication": "", 
                "config": "! Command: show running-config\n", 
                "deviceSpecificConfiglets": [
                    "SYS_TelemetryBuilderV2_172.23.0.3_1", 
                    "veos02-basic-configuration", 
                    "SYS_TelemetryBuilderV2", 
                    "RECONCILE_172.23.0.3"
                ], 
                "fqdn": "veos02", 
                "imageBundle": "", 
                "ipAddress": "172.23.0.3", 
                "key": "50:5d:9e:7a:dc:0a", 
                "name": "veos02", 
                "parentContainerKey": "container_1310_1487099262859288", 
                "parentContainerName": "MLAG01", 
                "version": "4.23.0F"
            }
        ],
        "imageBundles": [
            {
                "certifified": "true", 
                "imageNames": [
                    "EOS-4.20.11M.swi", 
                    "TerminAttr-1.5.4-1.swix"
                ], 
                "key": "imagebundle_1571150950845802635", 
                "name": "EOS-4.20.11M"
            }
        ], 
        "tasks": [
            {
                "actionStatus": "COMPLETED", 
                "currentAction": "Task Status Update", 
                "description": "Configlet Assign from Container Move: veos03", 
                "displayedStutus": "Completed", 
                "name": "", 
                "note": "Executed by Ansible", 
                "status": "COMPLETED", 
                "taskNo": "121"
            }
        ]
    }
}
```


