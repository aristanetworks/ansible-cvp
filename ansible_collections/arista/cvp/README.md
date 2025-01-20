<!--
  ~ Copyright (c) 2023-2025 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# arista.cvp - Automate CloudVision with Ansible

## Description

[Arista Networks](https://www.arista.com/) supports Ansible for managing devices running the EOS operating system through [CloudVision platform (CVP)](https://www.arista.com/en/products/eos/eos-cloudvision). This collection includes a set of Ansible modules that perform specific configuration tasks on a CVP server. These tasks include collecting facts, managing configlets, building topology with containers and devices, and running tasks.

Even if the `arista.cvp` collection is integrated with the `arista.avd` collection to [automate configuration deployment](https://avd.arista.com/4.7/roles/eos_config_deploy_cvp/index.html), this collection can also be used outside of AVD tasks to populate your CloudVision server with your workflows.

## Requirements

The CVP collection has the following requirements:

- Python 3.10+
- Ansible Core 2.16.0 to 2.18.x
- Install the arista.cvp collection
- [Additional Python packages](#additional-python-dependencies)

For a full breakdown of the requirements, please see the official `arista.cvp` [documentation](https://cvp.avd.sh/en/stable/docs/installation/requirements/).

## Installations

| ansible-cvp | 1.0.0 | 1.1.0 | >= 2.0.0 |>= 3.9.0 |
| ----------- | ----- | ----- | -------- | -------- |
| 2018.2 | ✅ | ✅ | ✅ | |
| 2019.x | ✅ | ✅ | ✅ | |
| 2020.1 | | ✅ | ✅ | |
| >= 2020.2 | | | ✅ | |
| >= 2021.3 | | | | ✅ |

### Python

- Python `>=3.9`

Please check the minimum version supported by your ansible installation on the [ansible website](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-node-requirements).

### Additional Python Libraries required

**Ansible version:**

- ansible-core>=2.16.0,<2.19.0

**3rd party Python libraries:**

- [cvprac](https://github.com/aristanetworks/cvprac)
- requests
- jsonschema
- treelib (for modules in version 1)

```shell
ansible-galaxy collection install arista.cvp
```

You can also include it in a requirements.yml file and install it with ansible-galaxy collection install -r requirements.yml, using the format:

```yaml
collections:
  - name: arista.cvp
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the Ansible package.

To upgrade the collection to the latest available version, run the following command:

```shell
ansible-galaxy collection install arista.cvp --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version 3.10.1:

```shell
ansible-galaxy collection install arista.cvp:==3.10.1
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/collections_guide/index.html) for more details.

### Additional Python Dependencies

The CVP collection requires the installation of additional Python packages. To ensure you install the correct versions, run the following commands:

```shell
export ARISTA_CVP_DIR=$(ansible-galaxy collection list arista.cvp --format yaml | head -1 | cut -d: -f1)
pip3 install -r ${ARISTA_CVP_DIR}/arista/cvp/requirements.txt
```

## Use Cases

This example outlines how to use `arista.cvp` to create a container's topology on Arista CloudVision.

A dedicated repository is available for step-by-step examples on [ansible-cvp-toi](https://github.com/arista-netdevops-community/ansible-cvp-toi).

A [complete end-to-end demo](https://github.com/arista-netdevops-community/ansible-avd-cloudvision-demo) using [Arista Validated Design collection](https://github.com/aristanetworks/ansible-avd) and CloudVision modules is available as an example.

Below is a very basic example of build a container topology on a CloudVision platform, assuming you have three vEOS named `veos0{1,3}` and a configlet named `alias`.

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

As modules of this collection are based on [`HTTPAPI` connection plugin](https://docs.ansible.com/ansible/latest/plugins/httpapi.html), authentication elements shall be declared using this plugin mechanism and are automatically shared with `arista.cvp.cv_*` modules.

## Testing

Please see our [pipeline workflows](https://github.com/aristanetworks/ansible-cvp/actions) to view the in-depth testing performed against the collection.

## Contributing

Contributing pull requests are gladly welcomed for this repository. If you are planning a significant change, please start a discussion first to ensure we can merge it.

You can also open an [issue](https://github.com/aristanetworks/ansible-cvp/issues) to report any problem or to submit enhancement.

## Support

- The `arista.avd` Ansible collection version 4.x releases and higher offer full support from Arista TAC, which includes the `arista.cvp` Ansible collection. If your organization has the [A-Care subscription](https://www.arista.com/assets/data/pdf/AVD-A-Care-TAC-Support-Overview.pdf) please don't hesitate to contact TAC with any questions or issues.
- Community support is provided via [Github discussions board](https://github.com/aristanetworks/ansible-cvp/discussions).

## License

The project is published under [Apache 2.0 License](https://github.com/aristanetworks/ansible-cvp/blob/devel/ansible_collections/arista/cvp/LICENSE)
