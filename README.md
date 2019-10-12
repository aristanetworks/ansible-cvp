![](https://img.shields.io/badge/Arista-CVP%20Automation-blue) ![GitHub](https://img.shields.io/github/license/aristanetworks/ansible-cvp)  ![GitHub commit activity](https://img.shields.io/github/commit-activity/w/aristanetworks/ansible-cvp)  ![GitHub last commit](https://img.shields.io/github/last-commit/aristanetworks/ansible-cvp)

# Ansible Modules for CloudVision Platform (CVP)


![Development Status](https://img.shields.io/badge/development-In_Progress-red)  __WARNING: Pre Release Work in progress Anisble modules for CVP__ 



<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Ansible Modules for CloudVision Platform (CVP)](#ansible-modules-for-cloudvision-platform-cvp)
  - [Modules overview](#modules-overview)
    - [cv_facts](#cv_facts)
    - [cv_configlet](#cv_configlet)
    - [cv_container](#cv_container)
    - [cv_device](#cv_device)
  - [Installation](#installation)
  - [Example playbook](#example-playbook)
- [Resources](#resources)
- [License](#license)
- [Ask question or report issue](#ask-question-or-report-issue)
- [Contribute](#contribute)

<!-- /code_chunk_output -->


## Modules overview

This repository provides a list of modules related to [CloudVision platform](https://www.arista.com/en/products/eos/eos-cloudvision) from [Arista Networks](https://www.arista.com/).

### cv_facts

Module to collect relevant information from CVP instance. It is baseline module to use before using other modules to interact with CVP servers. This module collect the following list of elements:
- List of devices.
- List of containers.
- List of configlets.
- List of image bundles.
- List of tasks.

_Playbook Example_

```yaml
---
- name: Test cv_configlet_v2
  hosts: cvp
  connection: local
  gather_facts: no
  tasks:
  - name: "Gather CVP facts {{inventory_hostname}}"
      cv_facts:
      host: '{{ansible_host}}'
      username: '{{cvp_username}}'
      password: '{{cvp_password}}'
      protocol: https
      port: '{{cvp_port}}'
      register: cv_facts
```

_Tested CVP versions:_

- 2018.2.5
- 2019.1.0

### cv_configlet

Module to manage containers on CVP based on an intend method. After extracting facts from CVP with `cv_facts`, module create, delete and update containers based on the topology defined within ansible.

This module only manages configlets that match a list of filter. If this filter is not set, then module only run addition of configlet.

_Module example:_

```yaml
---
- name: Test cv_configlet_v2
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    configlet_list:
      Test_Configlet: "! This is a Very First Testing Configlet\n!"
      Test_DYNAMIC_Configlet: "{{ lookup('file', 'templates/configlet_'+inventory_hostname+'.txt') }}"
  tasks:
  - name: 'Create configlets on CVP {{inventory_hostname}}.'
      tags:
        - provision
      cv_configlet:
        host: "{{ansible_host}}"
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        cvp_facts: "{{cvp_facts.ansible_facts}}"
        configlets: "{{configlet_list}}"
        configlet_filter: ["New", "Test"]
      register: cvp_configlet
```

_Tested CVP versions:_

- 2018.2.5
- 2019.1.0

### cv_container

This module is in charge of topology management as well as attaching configlet to containers and move devices to containers.

> WORK IN PROGRESS


### cv_device

  Devices can be deployed from the undefined container to a provisioned container or moved from one container to another using the add functionality and specifying the target container. Configlets can be added to devices using add and specifying the current parent container.
  Devices can be Removed from CVP using the delete option and specifying `CVP` as the container, equivalent to the `REMOVE` GUI option.
  
  Devices can be reset and moved to the undefined container using the delete option and specifying `RESET` as the container.

  Configlets can be removed from a device using the delete option and specifying the configs to be removed and the current parent container as the container.
  show option provide device data and current config.

> WORK IN PROGRESS
  

## Installation

**CvpRac**

  To use these modules you will need cvprac.
  The official version can be found here: [Arista Networks cvprac](https://github.com/aristanetworks/cvprac)
  CVPRACV2 in this repository is a tweaked version with additional functionality that has been requested in the official version.

  Installation notes are available on [installation page](INSTALLATION.md)

> Note: Repository is a pre-release work. A custom installation is required to run non standard installation process for python and ansible.

## Example playbook

This example outlines how to use Ansible to create a device container on Arista CloudVision.

```yaml
---
- name: Test cv_container
  hosts: cvp
  connection: local
  gather_facts: no
  vars:

  tasks:
    # collect CVP facts
    - name: "Gather CVP facts {{inventory_hostname}}"
      cv_facts:
        host: '{{ansible_host}}'
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        protocol: https
      register: cv_facts
    # Print CVP facts.
    - name: "Print out facts from CVP"
      debug:
        msg: "{{cv_facts}}"

```

> TO BE UPDATED WHEN MODULES SHIPPED

# Resources

  Other CVP Ansible modules can be found here: [Arista EOS+ Ansible Modules](https://github.com/arista-eosplus/ansible-cloudvision)

# License

Project is published under [Apache License](LICENSE).

# Ask question or report issue

Please open an issue on Github this is the fastest way to get an answer.

# Contribute

Contributing pull requests are gladly welcomed for this repository. If you are planning a big change, please start a discussion first to make sure we’ll be able to merge it.
