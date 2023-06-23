# Validate Configlet

**cv_validate_v3** Online and Offline configlet validation:

- Validate configlet on CloudVision against a device (online validation)
- Validate local configlet against a device (offline validation)

## Inputs

The documentation is available in the [module section](../../modules/cv_validate_v3.rst.md).

### Input variables

- devices information
- validate_mode (`stop_on_error`, `stop_on_warning`, `ignore`)

### Example

```yaml
  - name: validate module
    arista.cvp.cv_validate_v3:
      devices: "{{CVP_DEVICES}}"
      validate_mode: stop_on_error
```

### Example of offline configlet validation

```yaml
- name: offline configlet validation
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - device_name: leaf1
        search_type: serialNumber #[hostname | serialNumber | fqdn]
        local_configlets:
          valid: "interface Ethernet1\n  description test_validate"
          error: "ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111"

  tasks:
    - name: validate module
      arista.cvp.cv_validate_v3:
        devices: "{{CVP_DEVICES}}"
        validate_mode: stop_on_error # | stop_on_warning | valid
```

### Example of online configlet validation

```yaml
- name: Online configlet validation
  hosts: cv_server
  connection: local
  gather_facts: no
  vars:
    CVP_DEVICES:
      - device_name: leaf1
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

## Validation Mode

| Mode              |   Description   |
|-------------------|-----------------------|
| stop_on_error     | Stop playbook execution when validation throws an error |
| stop_on_warning   | Stop playbook execution when validation throws a warning or error |
| ignore            | Ignore errors and warnings. Playbook execution does not stop |

## Module output

```yaml
msg:
  changed: false
  configlets_validated:
    changed: false
    configlets_validated_count: 1
    configlets_validated_list:
    - validate_valid_on_serialNumber_validated
    diff: {}
    errors: []
    success: true
    taskIds: []
    warnings: []
  failed: false
  success: true
  taskIds: []
```
