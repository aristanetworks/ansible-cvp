# cv\_container\_v3

Manage Provisioning topology.

Module added in version 2.9

<div class="contents" data-local="" data-depth="2">

</div>

## Synopsis

CloudVision Portal Configlet configuration requires a dictionary of
containers with their parent, to create and delete containers on CVP
side. Returns number of created and/or deleted containers

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
<td>cvp_facts<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>Facts from CVP collected by cv_facts module</div>
</td>
</tr>

<tr>
<td>topology<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>Yaml dictionary to describe intended containers</div>
</td>
</tr>

</table>
</br>

## Examples:

    - name: Create container topology on CVP
      hosts: cvp
      connection: local
      gather_facts: no
      vars:
        verbose: False
        containers:
            Fabric:
                parent_container: Tenant
            Spines:
                parent_container: Fabric
                configlets:
                    - container_configlet
      tasks:
        - name: 'running cv_container'
          arista.cvp.cv_container_v3:
            topology: "{{CVP_CONTAINERS}}"

### Author

  - EMEA AS Team (@aristanetworks)

### Status

This module is flagged as **preview** which means that it is not
guaranteed to have a backwards compatible interface.
