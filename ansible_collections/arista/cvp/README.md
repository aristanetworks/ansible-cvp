# Ansible Modules for Arista CloudVision Platform

## About

[Arista Networks](https://www.arista.com/) supports Ansible for managing devices running the EOS operating system through [CloudVision platform (CVP)](https://www.arista.com/en/products/eos/eos-cloudvision). This roles includes a set of ansible modules that perform specific configuration tasks on CVP server. These tasks include: collecting facts, managing configlets, containers, build provisionning topology and running tasks.

## Requirements

__Arista CloudVision:__

- CloudVision 2018.2.5 or later

__Python:__

- Python 3.6.8 or later

__Additional Python Libraries required:__

- requests >= `2.22.0`
- treelib version `1.5.5` or later

__Supported Ansible Versions:__

    ansible 2.9 or later

## Installation

```shell
pip install requests>=2.22.0
pip install treelib>=1.5.5
```

Ansible galaxy hosts all stable version of this collection. Installation from ansible-galaxy is the most convenient approach for consuming `arista.cvp` content

```shell
$ ansible-galaxy collection install arista.cvp
Process install dependency map
Starting collection install process
Installing 'arista.cvp:1.0.3' to '~/.ansible/collections/ansible_collections/arista/cvp'
```

## Modules overview

This repository provides content for Ansible's collection __arista.cvp__ with following content:

- __arista.cvp.cv_facts__ - Collect CVP facts from server like list of containers, devices, configlet and tasks.
- __arista.cvp.cv_configlet__ -  Manage configlet configured on CVP.
- __arista.cvp.cv_container__ -  Manage container topology and attach configlet and devices to containers.
- __arista.cvp.cv_device__ - Manage devices configured on CVP
- __arista.cvp.cv_task__ - Run tasks created on CVP.

This collection supports CVP version >= `2018.2.5`

## Example

### Create containers on CloudVision

```yaml
---
- name: Build Switch configuration
  hosts: DC1_FABRIC
  connection: local
  gather_facts: no
  vars:
    CVP_CONTAINERS:
      DC1_LEAF1:
        parent_container: DC1_L3LEAFS
      DC1_FABRIC:
        parent_container: Tenant
      DC1_L3LEAFS:
        parent_container: DC1_FABRIC
      DC1_LEAF2:
        parent_container: DC1_L3LEAFS
      DC1_SPINES:
        parent_container: DC1_FABRIC
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      arista.cvp.cv_facts:
      register: CVP_FACTS
    - name: "Building Container topology on {{inventory_hostname}}"
      tags: [provision]
      arista.cvp.cv_container:
          topology: '{{CVP_CONTAINERS}}'
          cvp_facts: '{{CVP_FACTS.ansible_facts}}'
          save_topology: true
```

### Create Configlets on CloudVision

```yaml
---
- name: Build Switch configuration
  hosts: DC1_FABRIC
  connection: local
  gather_facts: no
  vars:
    CVP_CONFIGLETS:
      ANSIBLE_TESTING_CONTAINER: "alias a{{ 999 | random }} show version"
      ANSIBLE_TESTING_VEOS: "alias a{{ 999 | random }} show version"
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      arista.cvp.cv_facts:
      register: CVP_FACTS
    - name: 'Create configlets on CVP {{inventory_hostname}}.'
      arista.cvp.cv_configlet:
        cvp_facts: "{{CVP_FACTS.ansible_facts}}"
        configlets: "{{CVP_CONFIGLETS}}"
        configlet_filter: ["_TESTING_"]
```

### Configure devices on CloudVision

```yaml
---
- name: Build Switch configuration
  hosts: DC1_FABRIC
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      DC1-SPINE1:
        name: DC1-SPINE1
        parent_container: DC1_SPINES
        configlets:
            - AVD_DC1-SPINE1
        imageBundle: []
      DC1-SPINE2:
        name: DC1-SPINE2
        parent_container: DC1_SPINES
        configlets:
            - AVD_DC1-SPINE2
        imageBundle: []
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      arista.cvp.cv_facts:
      register: CVP_FACTS
    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device:
        devices: "{{CVP_DEVICES}}"
        cvp_facts: '{{CVP_FACTS.ansible_facts}}'
        device_filter: ['DC1']
        state: present
```

More documentation on [github repository](https://github.com/aristanetworks/ansible-cvp)

## License

Project is published under [Apache License](LICENSE).

## Ask a question

Support for this `arista.cvp` collection is provided by the community directly in this repository. Easiest way to get support is to open [an issue](https://github.com/aristanetworks/ansible-cvp/issues).

## Contributing

Contributing pull requests are gladly welcomed for this repository. If you are planning a big change, please start a discussion first to make sure we'll be able to merge it.

You can also open an [issue](https://github.com/aristanetworks/ansible-cvp/issues) to report any problem or to submit enhancement.

A more complete [guide for contribution](https://github.com/aristanetworks/ansible-cvp/contributing.md) is available in the repository
