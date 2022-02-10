# Ansible Modules for Arista CloudVision Platform

## About

[Arista Networks](https://www.arista.com/) supports Ansible for managing devices running the EOS operating system through [CloudVision platform (CVP)](https://www.arista.com/en/products/eos/eos-cloudvision). This collection includes a set of ansible modules that perform specific configuration tasks on CVP server. These tasks include: collecting facts, managing configlets, building topology with containers and devices, running tasks.

<p align="center">
  <img src='medias/ansible-cloudvision.png' alt='Arista CloudVision and Ansible'/>
</p>

Even if __`arista.cvp`__ collection is integrated with `arista.avd` collection to [automate configuration deployment](https://avd.sh/en/latest/roles/eos_config_deploy_cvp/index.html), this collection can also be used outside of AVD tasks to populate your Cloudvision server with your own workflows.

## Requirements

### Arista CloudVision

Current active branch:

- __CVP 2020.2.x and onward__: starting version [`ansible-cvp 2.0.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v2.0.0)

!!! info
    Starting version 2.0.0, collection uses [cvprac](https://github.com/aristanetworks/cvprac) as Cloudvision connection manager. So support for any new CLoudvision server is tied to it support in this python library.

| ansible-cvp | 1.0.0 | 1.1.0 | >= 2.0.0 |
| ----------- | ----- | ----- | -------- |
| 2018.2 | ✅ | ✅ | ✅ |
| 2019.x | ✅ | ✅ | ✅ |
| 2020.1 | | ✅ | ✅ |
| >= 2020.2 | | | ✅ |

### Python

- Python `>=3.8`

Please check the minimum version supported by your ansible installation on [ansible website](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-node-requirements)

### Additional Python Libraries required

__Ansible version:__

- ansible >= `2.9.0`

__3rd party Python libraries:__

- [cvprac](https://github.com/aristanetworks/cvprac)
- requests
- jsonschema
- treelib (for modules in version 1)

```shell
--8<-- "requirements.txt"
```

## Installation

```shell
pip install ansible_collections/arista/cvp/requirements.txt

# For modules in version 1
pip install treelib>=1.5.5
```

Ansible galaxy hosts all stable version of this collection. Installation from ansible-galaxy is the most convenient approach for consuming `arista.cvp` content

```shell
$ ansible-galaxy collection install arista.cvp
Process install dependency map
Starting collection install process
Installing 'arista.cvp:1.1.0' to '~/.ansible/collections/ansible_collections/arista/cvp'
```

Complete installation process is available on [repository website](docs/installation/requirements/)

## Collection overview

This repository provides content for Ansible's collection __arista.cvp__ with following content:

### List of available modules

__Version 3:__

- [__arista.cvp.cv_configlet_v3__](docs/modules/cv_configlet_v3.rst/) -  Manage configlet configured on CVP.
- [__arista.cvp.cv_container_v3__](docs/modules/cv_container_v3.rst/) -  Manage container topology and attach configlet and devices to containers.
- [__arista.cvp.cv_device_v3__](docs/modules/cv_device_v3.rst/) - Manage devices configured on CVP
- [__arista.cvp.cv_task_v3__](docs/modules/cv_task_v3.rst/) - Run tasks created on CVP.
- [__arista.cvp.cv_facts_v3__](docs/modules/cv_facts_v3.rst/) - Collect information from Cloudvision.
- [__arista.cvp.cv_image_v3__](https://cvp.avd.sh/en/latest/docs/modules/cv_image_v3.rst/) - Create EOS images and bundles on Cloudvision.

### List of available roles

- [__arista.cvp.dhcp_configuration__](roles/dhcp_configuration/) - Configure DHCPD service on a Cloudvision server or any dhcpd service.
- [__arista.cvp.configlet_sync__](roles/configlets_sync/) - Synchronize configlets between multiple Cloudvision servers.

### Deprecated modules

- [__arista.cvp.cv_facts__](docs/modules/cv_facts.rst/) - Collect CVP facts from server like list of containers, devices, configlet and tasks.
- [__arista.cvp.cv_configlet__](docs/modules/cv_configlet.rst/) -  Manage configlet configured on CVP.
- [__arista.cvp.cv_container__](docs/modules/cv_container.rst/) -  Manage container topology and attach configlet and devices to containers.
- [__arista.cvp.cv_device__](docs/modules/cv_device.rst/) - Manage devices configured on CVP
- [__arista.cvp.cv_task__](docs/modules/cv_task.rst/) - Run tasks created on CVP.

## Example

This example outlines how to use `arista.cvp` to create a containers topology on Arista CloudVision.

A dedicated repository is available for step by step examples on [ansible-cvp-toi](https://github.com/arista-netdevops-community/ansible-cvp-toi).

A [complete end to end demo](https://github.com/arista-netdevops-community/ansible-avd-cloudvision-demo) using [Arista Validated Design collection](https://github.com/aristanetworks/ansible-avd) and CloudVision modules is available as an example.

Below is a very basic example to build a container topology on a CloudVision platform assuming you have 3 veos named `veos0{1,3}` and a configlet named `alias`

```yaml
---
- name: Playbook to demonstrate cvp modules.
  hosts: cv_server
  connection: local
  gather_facts: no
  collections:
    - arista.cvp
  vars:
    # Configlet definition
    device_configuration:
      mlag-01a-config: "{{lookup('file', './config-router-mlag01a.conf')}}"
      mlag-01b-config: "{{lookup('file', './config-router-mlag01b.conf')}}"

    # Container definition
    containers_provision:
        Fabric:
          parentContainerName: Tenant
        Spines:
          parentContainerName: Fabric
        Leaves:
          parentContainerName: Fabric
          configlets:
              - alias
        MLAG01:
          parentContainerName: Leaves

    # Device definition
    devices_provision:
      - fqdn: mlag-01a
        parentContainerName: 'MLAG01'
        configlets:
            - 'mlag-01a-config'
        systemMacAddress: '50:8d:00:e3:78:aa'
      - fqdn: mlag-01b
        parentContainerName: 'MLAG01'
        configlets:
            - 'mlag-01b-config'
        systemMacAddress: '50:8d:00:e3:78:bb'

  tasks:
    - name: "Build Container topology on {{inventory_hostname}}"
      arista.cvp.cv_container_v3:
        topology: '{{containers_provision}}'

    - name: "Configure devices on {{inventory_hostname}}"
      arista.cvp.cv_device_v3:
        devices: '{{devices_provision}}'
```

As modules of this collection are based on [`HTTPAPI` connection plugin](https://docs.ansible.com/ansible/latest/plugins/httpapi.html), authentication elements shall be declared using this plugin mechanism and are automatically shared with `arista.cvp.cv_*` modules.

```ini
[development]
cv_server  ansible_host= 10.90.224.122 ansible_httpapi_host=10.90.224.122

[development:vars]
ansible_connection=httpapi
ansible_httpapi_use_ssl=True
ansible_httpapi_validate_certs=False
ansible_user=cvpadmin
ansible_password=ansible
ansible_network_os=eos
ansible_httpapi_port=443
```

As modules of this collection are based on [`HTTPAPI` connection plugin](https://docs.ansible.com/ansible/latest/plugins/httpapi.html), authentication elements shall be declared using this plugin mechanism and are automatically shared with `arista.cvp.cv_*` modules.

## License

Project is published under [Apache License](LICENSE).

## Ask a question

The best platform for general feedback, assistance, and other discussion is our [GitHub discussions](). To report a bug or request a specific feature, please open a [GitHub issue](https://github.com/aristanetworks/ansible-cvp/issues) using the appropriate template.

## Contributing

Contributing pull requests are gladly welcomed for this repository. If you are planning a big change, please start a discussion first to make sure we'll be able to merge it.

You can also open an [issue](https://github.com/aristanetworks/ansible-cvp/issues) to report any problem or to submit enhancement.

A more complete [guide for contribution](https://avd.sh/en/latest/docs/contribution/overview.html) is available in the repository
