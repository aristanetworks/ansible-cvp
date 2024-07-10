<!--
  ~ Copyright (c) 2023-2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Ansible Modules for Arista CloudVision Platform

![Arista CVP](https://img.shields.io/badge/Arista-CVP%20Automation-blue) ![[collection version](https://github.com/aristanetworks/ansible-cvp/tags)](https://img.shields.io/github/v/release/aristanetworks/ansible-cvp) ![License](https://img.shields.io/github/license/aristanetworks/ansible-cvp) [![Collection code testing](https://github.com/aristanetworks/ansible-cvp/actions/workflows/pull-request-management.yml/badge.svg)](https://github.com/aristanetworks/ansible-cvp/actions/workflows/pull-request-management.yml)

## About

[Arista Networks](https://www.arista.com/) supports Ansible for managing devices running the EOS operating system through [CloudVision platform (CVP)](https://www.arista.com/en/products/eos/eos-cloudvision). This roles includes a set of ansible modules that perform specific configuration tasks on CVP server. These tasks include: collecting facts, managing configlets, containers, build provisionning topology and running tasks. For installation, you can refer to [specific section](#installation) of this readme.

<p align="center">
  <img src='ansible_collections/arista/cvp/medias/ansible-cloudvision.png' alt='Arista CloudVision and Ansible'/>
</p>

More documentation is available in [project's website](https://cvp.avd.sh/)

## List of CVP versions supported

**arista.cvp** collection supports list of CloudVision version as listed below:

- **CVP 2018.x.x**: starting version [`ansible-cvp 1.0.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v1.0.0)
- **CVP 2019.x.x**: starting version [`ansible-cvp 1.0.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v1.0.0)
- **CVP 2020.1.x**: starting version [`ansible-cvp 1.1.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v1.1.0)
- **CVP >= 2020.2.x**: starting version [`ansible-cvp 2.0.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v2.0.0)

Starting version 2.0.0, collection uses [cvprac](https://github.com/aristanetworks/cvprac) as CloudVision connection manager. So support for any new CLoudvision server is tied to it support in this python library.

## Collection overview

This repository provides content for Ansible's collection **arista.cvp** with following content:

### List of available modules

**Version 3:**

- [**arista.cvp.cv_configlet_v3**](https://cvp.avd.sh/en/latest/docs/modules/cv_configlet_v3.md) -  Manage configlet configured on CVP.
- [**arista.cvp.cv_container_v3**](https://cvp.avd.sh/en/latest/docs/modules/cv_container_v3.md) -  Manage container topology and attach configlet and devices to containers.
- [**arista.cvp.cv_device_v3**](https://cvp.avd.sh/en/latest/docs/modules/cv_device_v3.md) - Manage devices configured on CVP
- [**arista.cvp.cv_task_v3**](https://cvp.avd.sh/en/latest/docs/modules/cv_task_v3.md) - Run tasks created on CVP.
- [**arista.cvp.cv_facts_v3**](https://cvp.avd.sh/en/latest/docs/modules/cv_facts_v3.md) - Collect information from CloudVision.
- [**arista.cvp.cv_image_v3**](https://cvp.avd.sh/en/latest/docs/modules/cv_image_v3.md) - Create EOS images and bundles on CloudVision.

### List of available roles

- [**arista.cvp.dhcp_configuration**](https://cvp.avd.sh/en/latest/roles/dhcp_configuration/) - Configure DHCPD service on a CloudVision server or any dhcpd service.
- [**arista.cvp.configlet_sync**](https://cvp.avd.sh/en/latest/roles/configlets_sync/) - Synchronize configlets between multiple CloudVision servers.

## Deprecated modules

- [**arista.cvp.cv_facts**](https://cvp.avd.sh/en/latest/docs/modules/cv_facts.md) - Collect CVP facts from server like list of containers, devices, configlet and tasks.
- [**arista.cvp.cv_configlet**](https://cvp.avd.sh/en/latest/docs/modules/cv_configlet.md) -  Manage configlet configured on CVP.
- [**arista.cvp.cv_container**](https://cvp.avd.sh/en/latest/docs/modules/cv_container.md) -  Manage container topology and attach configlet and devices to containers.
- [**arista.cvp.cv_device**](https://cvp.avd.sh/en/latest/docs/modules/cv_device.md) - Manage devices configured on CVP
- [**arista.cvp.cv_task**](https://cvp.avd.sh/en/latest/docs/modules/cv_task.md) - Run tasks created on CVP.

## Example

This example outlines how to use `arista.cvp` to create a containers topology on Arista CloudVision.

A dedicated repository is available for step by step examples on [ansible-cvp-toi](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi).

A [complete end to end demo](https://github.com/arista-netdevops-community/ansible-avd-cloudvision-demo) using [Arista Validated Design collection](https://github.com/aristanetworks/ansible-avd) and CloudVision modules is available as an example.

Another [demonstration repository](https://github.com/arista-netdevops-community/atd-avd) is available to play with Arista Test Drive. Please reach out to your favorite SE for getting access to such instance.

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

As modules of this collection are based on [`HTTPAPI` connection plugin](https://docs.ansible.com/ansible/latest/plugins/connection/httpapi.html), authentication elements shall be declared using this plugin mechanism and are automatically shared with `arista.cvp.cv_*` modules.

## Installation

Complete installation process is available on [repository website](https://cvp.avd.sh/)

### Requirements

To install requirements please follow [this](https://cvp.avd.sh/en/stable/docs/installation/requirements/) guide.

### Installation from ansible-galaxy

Ansible galaxy hosts all stable version of this collection. Installation from ansible-galaxy is the most convenient approach for consuming `arista.cvp` content

```shell
$ ansible-galaxy collection install arista.cvp
Process install dependency map
Starting collection install process
Installing 'arista.cvp:1.0.1' to '~/.ansible/collections/ansible_collections/arista/cvp'
```

### Git installation as source of collection

You can git clone this repository and use examples folder for testing. This folder contains a set of pre-configured playbook and ansible configuration:

```shell
git clone https://github.com/aristanetworks/ansible-cvp.git
```

Update your ansible.cfg to update collections_paths to point to local repository

```ini
collections_paths = /path/to/local/repository:~/.ansible/collections:/usr/share/ansible/collections
```

> It is highly recommended to use a python virtual-environment to not alter your production environment.

### Docker for testing

In an effort to support both [arista.avd](https://github.com/aristanetworks/ansible-avd) and arista.cvp collections, you can find a generic docker image in [this repository](https://github.com/arista-netdevops-community/docker-avd-base).

Besides this image, a repository with some basic labs to use as part of a TOI are available in [this repository](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)

## Resources

- Ansible for [Arista Validated Design](https://github.com/aristanetworks/ansible-avd)
- Ansible [EOS modules](https://docs.ansible.com/ansible/latest/modules/list_of_network_modules.html#eos) on ansible documentation.
- [CloudVision Platform](https://www.arista.com/en/products/eos/eos-cloudvision) overvierw
- [Training Lab content](https://github.com/arista-netdevops-community/ansible-cvp-avd-toi)
- Content for [demo using Arista Validated Design and `arista.cvp` collection.](https://github.com/arista-netdevops-community/ansible-avd-cloudvision-demo)

## Ask a question

Support for this `arista.cvp` collection is provided by the community directly in this repository. Easiest way to get support is to open [an issue](https://github.com/aristanetworks/ansible-cvp/issues).

## Branching Model

- The **`devel`** branch corresponds to the release actively under development.
- The **`releases/x.x.x`** branches correspond to stable releases.
- Fork repository and create a branch based on **`devel`** to set up a dev environment if you want to open a PR.
- See the ansible-cvp release for information about active branches.

## License

Project is published under [Apache 2.0 License](LICENSE)
