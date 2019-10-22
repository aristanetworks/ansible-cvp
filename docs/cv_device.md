# Manage device content

## Descrpition

__Module name:__ `cv_device`

This module manage devices from a Cloudvision stand point. It takes an intended list of devices with their configlets name and image bundle, compare against facts from [`cv_facts`](cv_facts.md) and then __attach__, __remove__ both configlets and image bundles.

## Options

Module comes with a set of options:

- `host`: IP address of CVP server
- `protocol`: Which protocol to use to connect to CVP. Can be either `http` or `https` (default: `https`)
- `port`: Port where CVP is listening. (default: based on `protocol`)
- `username`: user to use to connect to CVP.
- `password`: password to use to connect to CVP.
- `devices`: List of devices to manage.
- `cvp_facts`: Current facts collecting on CVP by a previous task
- `devices_filter`: Filter to apply intended mode on a set of configlet. If not used, then module only uses ADD mode. device_filter list devices that can be modified or deleted based on configlets entries.

## Usage

__Inputs__

Below is a basic playbook to collect facts:

```yaml
  vars:
    devices_inventory:
      veos01:
        name: veos01
        configlets:
          - cv_device_test01
          - SYS_TelemetryBuilderV2_172.23.0.2_1
          - veos01-basic-configuration
          - SYS_TelemetryBuilderV2
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      cv_facts:
        host: '{{ansible_host}}'
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        protocol: https
        port: '{{cvp_port}}'
      register: cvp_facts

    - name: "Configure devices on {{inventory_hostname}}"
      tags: 
        - provision
      cv_device:
        host: '{{ansible_host}}'
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        protocol: https
        port: '{{cvp_port}}'
        devices: "{{devices_inventory}}"
        cvp_facts: '{{cvp_facts.ansible_facts}}'
        device_filter: ['veos']
      register: cvp_device
```

__Result__

Below is an example of expected output

```json
{
    "changed": true, 
    "data": {
        "new": [], 
        "reset": [], 
        "tasks": [
            {
                "actionStatus": "ACTIVE", 
                "currentAction": "Submit", 
                "description": "Ansible Configlet Update: on Device veos01", 
                "displayedStutus": "Pending", 
                "name": "", 
                "note": "", 
                "status": "ACTIVE", 
                "taskNo": "128"
            }
        ]
        "updated": [
            {
                "veos01": "Configlets-[u'128']"
            }
        ]
    }, 
    "failed": false
}
```


