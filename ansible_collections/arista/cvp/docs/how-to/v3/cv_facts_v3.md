# Get provisioning information from CloudVision

**cv_facts_v3** get provisioning information from CloudVision:

- Support static configlets
- Support List of containers
- Support list of devices

## Inputs

This module does not support input data except module options.

### Optional module inputs

- `facts`: List of facts to get from CloudVision. It can be any of the following entries: [`devices`, `configlets`, `container`]
- `regexp_filter`: [Regualr expression](https://docs.python.org/3/howto/regex.html) to filter `configlets` and `devices` to only collect facts for interesting entries.
- `verbose`: Facts Verbosity.
  - `full` -  get all data from CV.
  - `short` -  get only cv_modules data.
  - Default is `short`

```yaml
tasks:
- name: '#01 - Collect devices facts from {{inventory_hostname}}'
  arista.cvp.cv_facts_v3:

- name: '#02 - Collect devices facts from {{inventory_hostname}}'
  arista.cvp.cv_facts_v3:
    facts:
    - configlets
  register: FACTS_DEVICES

- name: '#03 - Collect devices facts from {{inventory_hostname}}'
  arista.cvp.cv_facts_v3:
    facts:
    - devices
    - containers
  register: FACTS_DEVICES

- name: '#04 - Collect devices facts from {{inventory_hostname}}'
  arista.cvp.cv_facts_v3:
    facts:
    - devices
    - containers
    regexp_filter: '.*LEAF|BORDER.*'
    verbose: long
  register: FACTS_DEVICES
```

## Module output

`cv_facts_v3` returns:

```yaml
ok: [CloudVision] =>
  msg:
    changed: false
    data:
      cvp_configlets:
        spine-2-unit-test: |-
          lldp timer 20
          username ansible privilege 15 role network-admin secret sha512 $6$DJfSedWCtJPVTpp3$HOxiovAxJlrzr4WdOnqWbT9iXwdcfXvPiN4Z5K1Z4xZfdc9G85kgwkjufLUvBp.gNe4q/fbzAugZpvHC3yc7a1
          daemon TerminAttr
             exec /usr/bin/TerminAttr -cvaddr=apiserver.cv-staging.corp.arista.io:443 -cvcompression=gzip -taillogs -cvauth=token-secure,/tmp/cv-onboarding-token -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -disableaaa
             no shutdown
          hostname spine-2-unit-test
          ip name-server vrf default 192.0.2.40
          dns domain ire.aristanetworks.com
          interface Management1
             mtu 1380
             ip address 192.0.2.165/24
          ip route 0.0.0.0/0 192.0.2.1
          ntp server ntp.aristanetworks.com
      cvp_containers:
        CVPRACTEST:
          configlets: []
          parentContainerName: ansible-tests
          imageBundle: ""
      cvp_devices:
      - configlets:
        - leaf-2-unit-test
        - test_configlet
        - leaf-1-unit-test
        - test_device_configlet
        - cvaas-unit-test-01
        fqdn: leaf-1-unit-test.ire.aristanetworks.com
        hostname: leaf-1-unit-test
        parentContainerName: ansible-tests
        ipAddress: 192.0.2.165
        serialNumber: A2BC886CB9408A0453A3CFDD9C251999
        systemMacAddress: 50:00:00:d5:5d:c0
        imageBundle: ""
      - configlets: []
        fqdn: leaf-2-unit-test.ire.aristanetworks.com
        hostname: leaf-2-unit-test
        ipAddress: 192.0.2.166
        parentContainerName: ansible-tests
        serialNumber: 08A7E527AF711F688A6AD7D78BB5AD0A
        systemMacAddress: 50:00:00:cb:38:c2
        imageBundle: ""
      - configlets:
        - test_configlet
        fqdn: leaf-2-unit-test.ire.aristanetworks.com
        hostname: leaf-2-unit-test
        ipAddress: 192.0.2.167
        parentContainerName: ansible-tests
        serialNumber: 24666013EF2271599935B4A894F356E1
        systemMacAddress: 50:00:00:03:37:66
        imageBundle: ""
    failed: false
```

!!! info
    All sections can be natively reused in their respective module to reconfigure CloudVision. It can be used as a custom backup task or to synchronize multiple CloudVision instances.
