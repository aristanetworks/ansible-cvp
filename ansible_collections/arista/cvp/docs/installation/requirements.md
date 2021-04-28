# Requirements

## Arista EOS version

- EOS __4.21.8M__ or later
- Roles validated with eAPI transport -> `ansible_connection: httpapi`

## Arista Cloudvision

[Cloudvision](https://www.arista.com/en/products/eos/eos-cloudvision) instance must be supported by [Cloudvision ansible collection](https://cvp.avd.sh/)

## Python

- Python __3.6.8__ or later

## Supported Ansible Versions

- ansible __2.9.2__ or later

## Additional Python Libraries required

- [Jinja2](https://pypi.org/project/Jinja2/)
- [netaddr](https://pypi.org/project/netaddr/)
- [requests](https://pypi.org/project/requests/)
- [cvprac](https://github.com/aristanetworks/cvprac)
- [json-schema](https://github.com/Julian/jsonschema)

### Python requirements installation

In a shell, run following command:

```shell
$ pip3 install -r ansible_collections/arista/cvp/requirements.txt
```

```pip
--8<--
requirements.txt
--8<--
```

> Depending of your operating system settings, `pip3` might be replaced by `pip`.

## Ansible runner requirements

A optional docker container is available with all the requirements already installed. To use this container, Docker must be installed on your ansible runner.

To install Docker on your system, you can refer to the following page: [Docker installation step by step](https://docs.docker.com/engine/installation/)

Or if you prefer you can run this oneLiner installation script:

```shell
$ curl -fsSL get.docker.com | sh
```

In addition, docker-compose should be considered to run a stack of containers: https://docs.docker.com/compose/install/
