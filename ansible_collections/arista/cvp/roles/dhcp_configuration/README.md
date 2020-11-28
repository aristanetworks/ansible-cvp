# dhcp_configuration role

Ansible role to provision and configure Zero Touch Provisioning on a CloudVision server. Role will do the following:

- Install DHCP package
- Activate DHCPd service on CloudVision.
- Create `/etc/dhcp/dhcpd.conf` file with relevant information.
- Reload `dhcpd` service to apply changes.

## Requirements

No specific requirements to use this role.

## Tested Platforms

Below is a list of platforms where DHCPd configuration has been tested:

- Centos 7 / 8
- Ubuntu 18.02
- Arista Cloudvision 2019 and onward (for lab purpose)

This role should work on any platform running [ISC-DHCP server](https://www.isc.org/dhcp/).

> If role is applied to Cloudvision server, DHCP configuration may be erased during upgrade process. Use it at your own risk in a production environment.

## Role Variables

```yaml
mode:                 < offline/online - Select if role configure a DHCP server or just generate dhcpd.conf file locally. (default online) >
# Offline only variables
output_dir:           < path where to save dhcpd.conf file when using offline mode.>

# Online only variables
dhcp_packages: []     < List of packages to install as part of DHCP service. (default is ['dhcp'])>
dhcp_packages_state:  < Flag to install or remove DHCP package. (default is present)>
dhcp_config_dir:      < Folder where dhcp config is saved. (default is /etc/dhcp/)>
dhcp_config:          < Configuration file for DHCP service. (default is {{ dhcp_config_dir }}/dhcpd.conf)>
dhcp_service:         < Name of the service running on the system for DHCP. (default is dhcpd)>

# Data for template engine. For both offline and online mode
ztp:
  default:            < Section with default value for hosts configuration >
    registration:     < * Default URL to get Script to register to CV or initial configuration >
    gateway:          < Gateway to use by default if not set per device >
    nameservers:      < List of default NS to use on a per host basis >
    use_system_mac:   < true | false Configure DHCP for system-mac-address provided in show version (default false) >
  general:            < Section to define subnets parameters >
    subnets:
      - network:      < * Subnet where DHCP will listen for request >
        netmask:      < * Netmask of given subnet >
        gateway:      < Gateway to configure for given subnet >
        nameservers:  < List of name-servers to configure for given subnet >
        start:        < First IP available in the pool >
        end:          < Last IP available in the pool >
        lease_time:   < Maximum lease time before device loose IP. Renewal is max/2 >
  clients:            < List of clients on a mac-address basis >
    - name:           < * Hostname to provide when device do a DHCP request >
      mac:            < * Mac address of the host. Mac address value MUST be protected by either single or dual quotes >
      ip4:            < * IP Address of the host >
      registration:   < Registration URL to use for the host. If not set, default value will be applied >
      gateway:        < Gateway to use for the host. If not set, default value will be applied >
      nameservers:    < List of NS to use for the host. If not set, default value will be applied >
```

Variables with `*` are mandatory, others are optional and might be skipped if not needed in your setup.

## Dependencies

No dependency required for this role.

## Example Playbook

### Generate DHCPD configuration to deploy on a DHCP server

```yaml
---
- name: Configure DHCP service on CloudVision
  hosts: dhcp_server
  gather_facts: false
  collection:
    - arista.cvp
  vars:
    ztp:
      default:
        registration: 'http://10.255.0.1/ztp/bootstrap'
        gateway: 10.255.0.3
        nameservers:
          - '10.255.0.3'
      general:
        subnets:
          - network: 10.255.0.0
            netmask: 255.255.255.0
            gateway: 10.255.0.3
            nameservers:
              - '10.255.0.3'
            start: 10.255.0.200
            end: 10.255.0.250
            lease_time: 300
      clients:
        - name: DC1-SPINE1
          mac: '0c:1d:c0:1d:62:01'
          ip4: 10.255.0.11
        - name: DC1-SPINE2
          mac: '0c:1d:c0:1d:62:02'
          ip4: 10.255.0.12
        - name: DC1-LEAF1A
          mac: '0c:1d:c0:1d:62:11'
          ip4: 10.255.0.13
  tasks:
  - name: 'Execute DHCP configuration role'
    import_role:
      name: arista.cvp.dhcp_configuration
    vars:
      mode: offline
      output_dir: '{{inventory}}'
```

### Configure Server to act as ZTP server

Below is a basic playbook running `arista.cvp.dhcp_configuration` role

```yaml
---
- name: Configure DHCP service on CloudVision
  hosts: dhcp_server
  gather_facts: true
  collection:
    - arista.cvp
  vars:
    ztp:
      default:
        registration: 'http://10.255.0.1/ztp/bootstrap'
        gateway: 10.255.0.3
        nameservers:
          - '10.255.0.3'
      general:
        subnets:
          - network: 10.255.0.0
            netmask: 255.255.255.0
            gateway: 10.255.0.3
            nameservers:
              - '10.255.0.3'
            start: 10.255.0.200
            end: 10.255.0.250
            lease_time: 300
      clients:
        - name: DC1-SPINE1
          mac: '0c:1d:c0:1d:62:01'
          ip4: 10.255.0.11
        - name: DC1-SPINE2
          mac: '0c:1d:c0:1d:62:02'
          ip4: 10.255.0.12
        - name: DC1-LEAF1A
          mac: '0c:1d:c0:1d:62:11'
          ip4: 10.255.0.13
  tasks:
  - name: 'Execute DHCP configuration role'
    import_role:
      name: arista.cvp.dhcp_configuration
```

Inventory is configured like below:

```yaml
---
all:
  children:
    CVP:
      hosts:
        dhcp_server:
          ansible_host: 1.1.1.1
          ansible_user: user1
          ansible_password: password1
          ansible_become_password: password1
          ansible_python_interpreter: $(which python3)
```

If you are not using __root__ user, configure `ansible_become_password` since role always use `become: true`.

SSH connection is managed by [`paramiko`](http://www.paramiko.org/).

## License

Project is published under [Apache 2.0 License](../../../../../LICENSE)
