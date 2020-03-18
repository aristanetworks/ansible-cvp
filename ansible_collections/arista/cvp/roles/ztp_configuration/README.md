zto_configuration role
=======================

Ansible role to provision and configure Zero Touch Provisioning on a CloudVision server. Role will do the following:

- Activate DHCPd service on CloudVision.
- Create `/etc/dhcp/dhcpd.conf` file with relevant information.
- Reload `dhcpd` service to apply changes.

Requirements
------------

- dhcp server installed on remote server.

Supported Platforms
-------------------

Below is a list of platforms where DHCPd configuration has been tested:

- Arista Cloudvision 2019 and onward.
- Centos 7
- Centos 8

Role Variables
--------------

```yaml
ztp:
  default:            < Section with default value for hosts configuration >
    registration:     < * Default URL to get Script to register to CV or initial configuration >
    gateway:          < Gateway to use by default if not set per device >
    nameservers:      < List of default NS to use on a per host basis >
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

Dependencies
------------

No dependency required for this role.

Example Playbook
----------------

Below is a basic playbook running `arista.cvp.ztp_configuration` role

```yaml
---
- name: Configure ZTP service on CloudVision
  hosts: ztp_server
  gather_facts: no
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
  - name: 'Execute ZTP configuration role'
    import_role:
      name: arista.cvp.ztp_configuration
```

Inventory is configured like below:

```yaml
---
all:
  children:
    CVP:
      hosts:
        cv_ztp:
          ansible_host: 1.1.1.1
          ansible_user: root
          ansible_password: password
```

If you are not using `root` user, please also add `ansible_become_pass`

## License

Project is published under [Apache 2.0 License](../../../../../LICENSE)
