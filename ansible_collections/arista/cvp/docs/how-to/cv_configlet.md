# Configure configlets on Cloudvision

`cv_configlet` manage configlets on CloudVision:

- Configlets creation
- Configlets update
- Configlets deletion

The `cv_configlet` actions are based on cv_facts results:

- Use intend approach
- No declarative action

To import content from text file, leverage template rendering and then load from file: use `lookup()` command

## Inputs

Full documentation available in [module section](../modules/cv_configlet.rst.md) and a lab is available in the following [repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)

## Input variables

```yaml
CVP_CONFIGLETS:
  TEAM01-alias: "alias a1 show version"
  TEAM01-another-configlet: "alias a2 show version"
```

## Module inputs

#### Required Inputs

- `cvp_facts`: Facts from cv_facts
- `configlets`: List of configlets to create
- `configlet_filter`: A filter to target only specific configlets on CV

#### Optional inputs

- `state`: Keyword to define if we want to create(present) or delete(absent) configlets


```yaml
---
- name: lab03 - cv_configlet lab
  hosts: CloudVision
  connection: local
  gather_facts: no
  vars:
    CVP_CONFIGLETS:
      TEAM01-alias: "alias a1 show version"
      TEAM01-another-configlet: "alias a2 show version"
  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      arista.cvp.cv_facts:
      register: CVP_FACTS
    - name: "Configure configlet on {{inventory_hostname}}"
      arista.cvp.cv_configlet:
        cvp_facts: "{{CVP_FACTS.ansible_facts}}"
        configlets: "{{CVP_CONFIGLETS}}"
        configlet_filter: ["TEAM01"]
        state: present
```

## Module outputs

`cv_configlet` outputs:

- List of created configlets
- List of updated configlets
- List of deleted configlets
- List of generated tasks.

```json
ok: [CloudVision] => {
    "msg": {
        "changed": true,
        "data": {
            "deleted": [],
            "new": [
                {
                    "TEAM01-alias": "success"
                }
            ],
            "tasks": [],
            "updated": []
        },
        "failed": false
    }
}
```
