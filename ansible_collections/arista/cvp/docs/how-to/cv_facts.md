# Get facts from Cloudvision

`cv_facts` collect Facts from CloudVision:

- CV version
- List of devices part of CV.
    - Active EOS devices
    - Inactive EOS devices
    - 3rd part devices
- List of configlets
- List of containers
- List of tasks

Full documentation available in [module section](../modules/cv_facts.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)

## Playbook example

### Standard playbook

```yaml
---
- name: lab02 - cv_facts lab
  hosts: CloudVision
  connection: local
  gather_facts: no
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      arista.cvp.cv_facts:
      register: cv_facts
```

### Only collect a set of facts

```yaml
tasks:
  - name: "Gather CVP facts {{inventory_hostname}}"
    arista.cvp.cv_facts:
      facts:
        configlets
```

### Collect running-configuration of devices

```yaml
tasks:
  - name: "Gather CVP facts {{inventory_hostname}}"
    arista.cvp.cv_facts:
      facts:
        devices
      gather_subset:
        config
```

## Module output

Output is JSON and can be saved or considered as input by other modules

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
                    "veos03"
                ],
[...]
```
