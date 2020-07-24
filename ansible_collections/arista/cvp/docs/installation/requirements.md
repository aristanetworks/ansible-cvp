# Requirements

## Arista CloudVision

__arista.cvp__ collection supports list of Cloudvision version as listed below:

- __CVP 2018.x.x__: starting version [`ansible-cvp 1.0.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v1.0.0)
- __CVP 2019.x.x__: starting version [`ansible-cvp 1.0.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v1.0.0)
- __CVP 2020.x.x__: starting version [`ansible-cvp 1.1.0`](https://github.com/aristanetworks/ansible-cvp/releases/tag/v1.1.0)

When a CVP version is supported starting a specific version, any upcoming version will support that version until a specific announcement was made.

## Python

- Python 3.x

__Additional Python Libraries required:__

- requests >= `2.22.0`
- treelib version `1.5.5` or later

## Supported Ansible Versions

ansible 2.9 or later


## Install requirements

To install project's requirements, use `pip` from the root of the repository

```shell
# Requirement to use arista.cvp collection
$ pip install -r requirements.txt

# Requirements to develop arista.cvp collection
$ pip install -r development/requirements-dev.txt
```
