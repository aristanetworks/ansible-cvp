# cv_validate_v3

CVP/Local configlet Validation

Module added in version 3.7.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVision Portal Validate module to Validate configlets against a
device on CVP.

## Module-specific Options

The following options may be specified for this module:

<table border=1 cellpadding=4>

<tr>
<th class="head">parameter</th>
<th class="head">type</th>
<th class="head">required</th>
<th class="head">default</th>
<th class="head">choices</th>
<th class="head">comments</th>
</tr>

<tr>
<td>devices<br/><div style="font-size: small;"></div></td>
<td>list</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>CVP devices and configlet information.</div>
</td>
</tr>

<tr>
<td>validate_mode<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>yes</td>
<td></td>
<td><ul><li>stop_on_error</li><li>stop_on_warning</li><li>ignore</li></ul></td>
<td>
    <div>Indicate how cv_validate_v3 should behave on finding errors and/or warnings.</div>
</td>
</tr>

</table>
</br>

## Examples:

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

### Author

- Ansible Arista Team (@aristanetworks)

### Full Schema

Get full schema docs [here](../../schema/cv_validate_v3/).
