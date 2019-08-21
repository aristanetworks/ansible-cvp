# Installation notes


<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Installation notes](#installation-notes)
  - [User installation](#user-installation)
  - [Installation for dev environment](#installation-for-dev-environment)
    - [Create a virtual environment](#create-a-virtual-environment)
    - [Install project's requirements](#install-projects-requirements)
    - [Update cvprac library](#update-cvprac-library)

<!-- /code_chunk_output -->


## User installation

To Be done later

## Installation for dev environment

### Create a virtual environment

A virtual environment is __strongly__ recommended to not break your current Python setup

```
$ virtualenv -p $(which python) .venv
$ source .venv/bin/activate
```

> If `virtualenv` is not available in your system, you can install it with following command: `pip install virtualenv`

### Install project's requirements

To work with this project, a list of python requirements must be satisfied. To install them, use following command:

```
$ pip install -r requirements.txt
```

Once you did it, ensure you have correct elements:

- Ansible with correct version:

```
$ ansible --version
ansible 2.8.3
  config file = None
  configured module search path = ['/Users/arista/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /Users/arista/Projects/.venv/lib/python3.7/site-packages/ansible
  executable location = /Users/arista/Projects/.venv/bin/ansible
  python version = 3.7.3 (default, Mar 27 2019, 09:23:15) [Clang 10.0.1 (clang-1001.0.46.3)]
```

- __cvprac__ installed in correct path:

```
$ ls .venv/lib/python2.7/site-packages/cvprac/
__init__.py          __pycache__          cvp_api.py           cvp_client.py        cvp_client_errors.py
```

### Update cvprac library

To support Ansible module for CVP, __cvprac__ has been updated in this project. As it is an early stage development, cvprac changes have not been pushed back to __cvprac__.

```
$ cp CVPRACv2/* .venv/lib/python2.7/site-packages/cvprac/
```

Then, you can validate cvprac has been updated correctly:

```
$ python --version
Python 2.7.10

$ python          
Python 2.7.10 (default, Feb 22 2019, 21:55:15) 
[GCC 4.2.1 Compatible Apple LLVM 10.0.1 (clang-1001.0.37.14)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from cvprac import cvp_apiV2
>>> exit()
```

