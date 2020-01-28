# Manage Configlet content

## Descrpition

__Module name:__ `arista.cvp.cv_configlet`

This module manage configlet content and definition. it takes an intended list of configlet with their content, compare against facts from [`cv_facts`](cv_facts.md) and then __create__, __delete__, __update__ configlets.

## Options

Module comes with a set of options:

- `configlets`: List of configlets to manage.
- `cvp_facts`: Current facts collecting on CVP by a previous task
- `configlet_filter`: Filter to apply configlet management. If configured, module will add/update/delete configlets matching entries. If not matching, module will ignore configlet configured on CVP. If option is not set, module will only work in `add` mode
- `state`: Provide an option to delete configlets from CloudVision. Default value is present and it is an optional field.
    - `present`: Create / update configlets from CV.
    - `absent`: remove configlets from CV.

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
    configlet_list:
      Test_Configlet: "alias v99 show version"
      Test_DYNAMIC_Configlet: "{{ lookup('file', 'templates/configlet_'+inventory_hostname+'.txt') }}"
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      arista.cvp.cv_facts:
      register: cvp_facts

    - name: 'Create configlets on CVP {{inventory_hostname}}.'
      arista.cvp.cv_configlet:
        cvp_facts: "{{cvp_facts.ansible_facts}}"
        configlets: "{{configlet_list}}"
        configlet_filter: ["New", "Test","base-chk","base-firewall"]
      register: cvp_configlet
```

__Result__

Below is an example of expected output

```yaml
msg:
  changed: true
  data:
    deleted: []
    new: []
    tasks: []
    updated:
    - another_configlet: success
    - common_configlet: success
  diff:
    prepared: |-
      another_configlet:
      --- CVP
      +++ Ansible
      @@ -1 +1 @@
      -alias a971 show version+alias b61 show version

      common_configlet:
      --- CVP
      +++ Ansible
      @@ -1 +1 @@
      -alias a971 show version+alias b61 show version
  failed: false
```


