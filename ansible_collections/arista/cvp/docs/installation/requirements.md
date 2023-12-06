<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Requirements

## Arista EOS version

- EOS **4.21.8M** or later
- Roles validated with eAPI transport -> `ansible_connection: httpapi`

## Arista CloudVision

!!! info
    Starting with version 2.0.0, the collection uses [cvprac](https://github.com/aristanetworks/cvprac) as CloudVision connection manager. So support for any new CloudVision server is tied to it's support in this Python library.

| ansible-cvp | 1.0.0 | 1.1.0 | >= 2.0.0 |>= 3.9.0 |
| ----------- | ----- | ----- | -------- | -------- |
| 2018.2 | ✅ | ✅ | ✅ | |
| 2019.x | ✅ | ✅ | ✅ | |
| 2020.1 | | ✅ | ✅ | |
| >= 2020.2 | | | ✅ | |
| >= 2021.3 | | | | ✅ |

## Python

- Python **3.9** or later

## Supported Ansible Versions

- ansible-core from **2.14.0** to **2.16.x**

## Additional Python Libraries required

```pip
--8<--
requirements.txt
--8<--
```

### Python requirements installation

In a shell, run the following commands after installing the collection from ansible-galaxy:

```shell
export ARISTA_CVP_DIR=$(ansible-galaxy collection list arista.cvp --format yaml | head -1 | cut -d: -f1)
pip3 install -r ${ARISTA_CVP_DIR}/arista/avd/requirements.txt
```

If the collection is cloned from GitHub, the requirements file can be referenced directly:

```shell
pip3 install -r ansible-avd/ansible_collections/arista/cvp/requirements.txt
```

!!! warning
    Depending of your operating system settings, `pip3` might be replaced by `pip`.
