![](https://img.shields.io/badge/Arista-CVP%20Automation-blue) ![GitHub](https://img.shields.io/github/license/aristanetworks/ansible-cvp)  ![GitHub commit activity](https://img.shields.io/github/commit-activity/w/aristanetworks/ansible-cvp)  ![GitHub last commit](https://img.shields.io/github/last-commit/aristanetworks/ansible-cvp)

# Ansible Modules for CloudVision Platform (CVP)


![Development Status](https://img.shields.io/badge/development-In_Progress-red)  __WARNING: Pre Release Work in progress Anisble modules for CVP__ 



<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Ansible Modules for CloudVision Platform (CVP)](#ansible-modules-for-cloudvision-platform-cvp)
  - [Modules overview](#modules-overview)
  - [Installation](#installation)
  - [Example playbook](#example-playbook)
- [Resources](#resources)
- [License](#license)
- [Ask question or report issue](#ask-question-or-report-issue)
- [Contribute](#contribute)

<!-- /code_chunk_output -->


## Modules overview

**cv_configlet**

  Module to manage containers on CVP based on an intend method. After extracting facts from CVP with `cv_facts`, module create and delete containers based on the topology defined within ansible.

> A complete playbook to create / show / delete configlet is available under [tests folder](tests/playbook.configlet.demo.yaml) 

**cv_container**
 - `add`, `delete`, and `show` containers

Containers can be created or deleted. 

> A complete playbook to create / show / delete container is available under [tests folder](tests/playbook.container.demo.yaml) 

**cv_device**
 - `add`, `delete`, and `show` devices

  Devices can be deployed from the undefined container to a provisioned container or moved from one container to another using the add functionality and specifying the target container. Configlets can be added to devices using add and specifying the current parent container.
  Devices can be Removed from CVP using the delete option and specifying "CVP" as the container, equivalent to the REMOVE GUI option.
  Devices can be reset and moved to the undefined container using the delete option and specifying "RESET" as the container.
  Configlets can be removed from a device using the delete option and specifying the configs to be removed and the current parent container as the container.
  show option provide device data and current config.

> A complete playbook to move / show / delete devices is available under [tests folder](tests/playbook.device.demo.yaml) 

**cv_image [testing]**
 - `add`, `delete`, and `show` image bundles

  Image bundles must exist in CVP already, this module will allow the manipulation of them in CVP.
  Add and Delete will allow bundles to be applied or removed from Containers and devices
  Show will provide information on the contents of the image bundle.

**cv_tasks [testing]**
 - `add`, `delete`, and `show` tasks

  Tasks must exist in CVP already, this module will allow the manipulation of them in CVP.
  Add and Delete will allow Tasks to be executed or Canceled
  Show will provide information on the current Status or a Task.
  

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
    containers:
      - name: Fabric
        parent_container: Tenant
      - name: Spines
        parent_container: Fabric
      - name: Leaves
        parent_container: Fabric
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
    
    # Create containers topology

    - name: Create a container on CVP.
      cv_container:
        host: '{{ansible_host}}'
        username: '{{cvp_username}}'
        password: '{{cvp_password}}'
        topology: '{{containers}}'
        cvp_facts: '{{cvp_facts.ansible_facts}}'
```


# Resources

  Other CVP Ansible modules can be found here: [Arista EOS+ Ansible Modules](https://github.com/arista-eosplus/ansible-cloudvision)

# License

Project is published under [Apache License](LICENSE).

# Ask question or report issue

Please open an issue on Github this is the fastest way to get an answer.

# Contribute

Contributing pull requests are gladly welcomed for this repository. If you are planning a big change, please start a discussion first to make sure we’ll be able to merge it.
