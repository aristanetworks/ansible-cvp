# Ansible & CloudVision examples

## About

This folder contains a list of pre-configured playbook to run with all available modules provided by `arista.cvp` collection. It comes with a preconfigured `ansible.cfg` and a `Makefile` to automate environment building and playbook execution.

> These playbooks support only Ansible version __2.9.0rc4__ and onwards.

## Build and install ansible collection.

This section highlights how to build and install collection locally to use with playbooks

### Automated Make approach

Use Make to install python [`requirements`](../requirements.txt), build collection file and install it to `${PWD}/collections`

```shell
# Install requirements
$ make setup

# Build & install collection
$ make install
```

### Step by step approach

Below are list of all activities to do to configure collections

```shell
# Install python requirements.
$ pip install ../requirements.txt

# Build collection
$ ansible-galaxy collection build --force ../arista/cvp

# Install collection
$ ls | grep arista-cvp
$ ansible-galaxy collection install arista-cvp.xxx.tar.gz -p collections/
```

## Run playbooks

### Update inventory

An [inventory](inventory.ini) is provided for information purpose and must be updated with your environment. All playbooks call group called `[cvp]`, so it is higly recommended to use same for demo.

Following information must be provided per CVP instance:

- `ansible_host`: IP Address of you CVP instance.
- `cvp_port`: Port to use to connect to CVP.
- `cvp_username`: Username to use for CVP connection.
- `cvp_password`: Password to use for connection with `cvp_username`.

If you are using a virtual-environment, it is necessary to discover your python path with this variable:

```ini
[cvp:vars]
ansible_python_interpreter=$(which python)
```

## Collect CloudVision Facts with `cv_facts`

`cv_facts` module collects all relevant information from a CloudVision instance. It is the baseline for all other modules to manage their elements.

```shell
$ ansible-playbook playbook.facts.yaml
```

## Manage Configlets with `cv_configlet`

`cv_configlet` module __creates__, __updates__ and __deletes__ configlet based on lsit of elements described in ansible variable and facts retrieved in a previous step

```shell
$ ansible-playbook playbook.configlet.demo.yaml --tags provision
```

This playbook will create 2 different configlets on CVP:

- `Test_Configlet`
- `Test_DYNAMIC_Configlet`


## Manage Containers with `cv_container`

`cv_container` module __creates__, __updates__ and __deletes__ containers based on list of elements described in ansible variable and facts retrieved in a previous step

__Build container topology__
```shell
$ ansible-playbook playbook.container.demo.yaml --tags provision
```

> This playbook assumes you have at least 3 devices attached to CVP and names `veos0{1-3}`

Container topology will be like:
```
- Tenant
    - Ansible_Fabric
        - Spines
            - veos03
        - Leaves
            - MLAG01
                - veos01
                - veos02
```

__Cleanup container topology__
```shell
$ ansible-playbook playbook.container.demo.yaml --tags cleanup
```

> This playbook assumes you have at least 3 devices attached to CVP and names `veos0{1-3}`

Container topology will be like:
```
- Tenant
    - staging
        - veos03
        - veos01
        - veos02
```

## Manage Devices with `cv_device`

`cv_device` manage elements related to devices. It allows user to manage configlet's attachement to devices, images.

```shell
$ ansible-playbook playbook.device.demo.yaml
```

## Manage tasks with `cv_task`

`cv_task` allows user to run or cancel any pending tasks on cloudvision.

```shell
$ ansible-playbook playbook.tasks.demo.yaml
```
