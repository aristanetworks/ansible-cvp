# Installation using GIT

## Setup using Git to install collection

You can git clone this repository and use examples folder for testing. This folder contains a set of pre-configured playbook and ansible configuration:

### Clone repository

```shell
$ git clone https://github.com/aristanetworks/ansible-cvp.git
$ cd ansible-cvp
```

### Build and install collection

```shell
$ ansible-galaxy collection build --force ansible_collections/arista/cvp
$ ansible-galaxy collection install arista-cvp-<VERSION>.tar.gz
```

## Setup using Git for local testing.

### Clone repository

```shell
# Clone repository
$ git clone https://github.com/aristanetworks/ansible-cvp.git

# Move to git folder
cd ansible-cvp
```

### Install python virtual-environment

```shell
# Install virtualenv if not part of your system
$ python -m pip install virtualenv
```

### Create virtual environment

```shell
# Create a virtual env named .venv
$ virtualenv --no-site-packages -p $(which python2.7) .venv

# Activate virtualenv
$ source .venv/bin/activate
```

### Install collection requirements

```shell
# Install repsoitory requirements
$ pip install -r requirements.txt
```

### (Optional) Update your ansible.cfg

Only if you want to use your own playbooks outside of __`examples/`__folder of the repository.

```shell
# Get your current location
$ pwd
/path/to/ansible/cvp/collection_repository

# Update your ansible.cfg
$ vim ansible.cfg
collections_paths = /path/to/ansible/cvp/collection_repository
```
