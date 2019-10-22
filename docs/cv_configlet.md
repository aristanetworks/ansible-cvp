# Manage Configlet content

## Descrpition

__Module name:__ `cv_configlet`

This module manage configlet content and definition. it takes an intended list of configlet with their content, compare against facts from [`cv_facts`](cv_facts.md) and then __create__, __delete__, __update__ configlets.

## Options

Module comes with a set of options:

- `configlets`: List of configlets to manage.
- `cvp_facts`: Current facts collecting on CVP by a previous task
- `configlet_filter`: Filter to apply configlet management. If configured, module will add/update/delete configlets matching entries. If not matching, module will ignore configlet configured on CVP. If option is not set, module will only work in `add` mode

## Usage

__Inputs__

Below is a basic playbook to collect facts:

```yaml
  vars:
    configlet_list:
      Test_Configlet: "alias v99 show version"
      Test_DYNAMIC_Configlet: "{{ lookup('file', 'templates/configlet_'+inventory_hostname+'.txt') }}"
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      cv_facts:
      register: cvp_facts

    - name: 'Create configlets on CVP {{inventory_hostname}}.'
      cv_configlet:
        cvp_facts: "{{cvp_facts.ansible_facts}}"
        configlets: "{{configlet_list}}"
        configlet_filter: ["New", "Test","base-chk","base-firewall"]
      register: cvp_configlet
```

__Result__

Below is an example of expected output

```json
{
    "cvp_configlet": {
        "changed": true, 
        "data": {
            "deleted": [], 
            "new": [
                {
                    "Test_Configlet": "success"
                }
            ], 
            "tasks": [], 
            "updated": []
        }, 
        "failed": false
    }
}
```


