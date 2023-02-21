# Requirements

## Arista EOS version

- EOS **4.21.8M** or later
- Roles validated with eAPI transport -> `ansible_connection: httpapi`

## Arista CloudVision

!!! info
    Starting version 2.0.0, collection uses [cvprac](https://github.com/aristanetworks/cvprac) as CloudVision connection manager. So support for any new CLoudvision server is tied to it support in this python library.

| ansible-cvp | 1.0.0 | 1.1.0 | 2.0.0 & higher |
| ----------- | ----- | ----- | -------------- |
| 2018.2 | ✅ | ✅ | ✅ |
| 2019.x | ✅ | ✅ | ✅ |
| 2020.1 | | ✅ | ✅ |
| >= 2020.2 | | | ✅ |

## Python

- Python **3.9** or later

## Supported Ansible Versions

- ansible-core from **2.12.6** to **2.15.0** excluding **2.13.0**

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
