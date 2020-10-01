# Configure container on Cloudvision

cv_container manage containers on CloudVision:

- Support creation/deletion of containers
- Support devices binding to containers
- Support configlets binding to containers

`cv_container` bases its actions on cv_facts results

The `cv_container` actions are based on cv_facts results:

- Use intend approach
- No declarative action

## Inputs

Full documentation available in [module section](../modules/cv_container.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)

### Input variables

- Container Name
- Parent container where to create container
- Optional list of devices to attach to container
    - Devices must be already registered
    - Should not be in undefined container
- Optional list of configlets to attach to container:
    - Configlets must be created previously

```yaml
---
CVP_CONTAINERS:
  TEAM01:
    parent_container: Tenant
  TEAM01_DC:
    parent_container: TEAM01
  TEAM01_LEAFS:
    parent_container: TEAM01_DC
    configlets:
      - GLOBAL-ALIASES
  TEAM01_SPINES:
    parent_container: TEAM01_DC
    devices:
      - sw01
      - sw02
```

### Module inputs

#### Required Inputs

- `cvp_facts`: Facts from cv_facts
- `topology`: Container topology

#### Optional inputs

- `mode`: Define how to manage container available on CV and not in customer topology
    - `merge` (default)
    - `delete`
    - `override`

```yaml
- name: lab04 - cv_container lab
  hosts: CloudVision
  connection: local
  gather_facts: no
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      arista.cvp.cv_facts:
      register: CVP_FACTS
    - name: "Configure containers on {{inventory_hostname}}"
      arista.cvp.cv_container:
        cvp_facts: "{{CVP_FACTS.ansible_facts}}"
        topology: "{{CVP_CONTAINERS}}"
```

## Module output

`cv_container` returns :

- List of created containers
- List of deleted containers
- List of moved devices
- List of attached configlets
- List of CV tasks generated

> Generated tasks can be consumed directly by cv_tasks.

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
                        "containers": [ ],
                        "devices": [ ],
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
        "tasks": []
    },
    "failed": false
}
```
