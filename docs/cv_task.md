# Manage pending tasks on CVP

## Descrpition

__Module name:__ `arista.cvp.cv_task`

This module manage provisioning topology at container's level. it takes an intended topology, compare against facts from [`cv_facts`](cv_facts.md) and then __create__, __delete__ containers before assigning existing configlets and moving devices to containers.

## Options

Module comes with a set of options:

- `tasks`: CVP taskIDs to act on
- `wait`: Time to wait for tasks to transition to 'Completed'. (Default value is `0`)
- `state`: Action to carry out on the task. Must be either `executed` or `cancelled`. Default is `executed`

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
tasks:
    - name: "Gather CVP facts from {{inventory_hostname}}"
      arista.cvp.cv_facts:
      register: cvp_facts
      tags:
        - always

    - name: 'Execute all pending tasks and wait for completion for 60 seconds'
      arista.cvp.cv_task:
        tasks: "{{ tasks }}"
        wait: 60
```

__Result__

Below is an example of expected output

```json
{
    "msg": {
        "changed": false, 
        "data": {}, 
        "failed": false, 
        "warnings": [
            "No actionable tasks found on CVP"
        ]
    }
}
```


