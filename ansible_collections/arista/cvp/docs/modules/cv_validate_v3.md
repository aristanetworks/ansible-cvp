# cv_validate_v3

CVP/Local configlet Validation

Module added in version 3.7.0
## Synopsis

CloudVision Portal Validate module to Validate configlets against a device on CVP.

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| devices  |   list | True  |  | | CVP devices and configlet information. |
| validate_mode  |   str | True  |  | <ul> <li>stop_on_error</li>  <li>stop_on_warning</li>  <li>ignore</li> </ul> | Indicate how cv_validate_v3 should behave on finding errors and/or warnings. |


## Examples

```yaml

# offline validation
- name: offline configlet validation
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - device_name: leaf1
        search_type: hostname #[hostname | serialNumber | fqdn]
        local_configlets:
          valid: "interface Ethernet1\n  description test_validate"
          error: "ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111"

  tasks:
    - name: validate module
      arista.cvp.cv_validate_v3:
        devices: "{{CVP_DEVICES}}"
        validate_mode: stop_on_error # | stop_on_warning | valid

# online validation
- name: Online configlet validation
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - device_name: leaf1.aristanetworks.com
        search_type: fqdn #[hostname | serialNumber | fqdn]
        cvp_configlets:
          - valid
          - invalid

  tasks:
    - name: validate module
      arista.cvp.cv_validate_v3:
        devices: "{{CVP_DEVICES}}"
        validate_mode: stop_on_error # | stop_on_warning | valid

```

## Author

Ansible Arista Team (@aristanetworks)

## Full schema

Please see the [schema documentation](../schema/cv_validate_v3.md).
