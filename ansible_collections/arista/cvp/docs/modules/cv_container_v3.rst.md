# cv_container_v3

Manage Provisioning topology.

Module added in version 3.0.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVision Portal Configlet configuration requires a dictionary of
containers with their parent, to create and delete containers on CVP
side. Module also supports to configure configlets at container level.
Returns number of created and/or deleted containers

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
<td>apply_mode<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>loose</td>
<td><ul><li>loose</li><li>strict</li></ul></td>
<td>
    <div>Set how configlets are attached/detached on container. If set to strict all configlets not listed in your vars are detached.</div>
</td>
</tr>

<tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>present</td>
<td><ul><li>present</li><li>absent</li></ul></td>
<td>
    <div>Set if ansible should build or remove devices on CLoudvision</div>
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

    # task in loose mode (default)
    - name: Create container topology on CVP
      hosts: cvp
      connection: local
      gather_facts: no
      vars:
        verbose: False
        containers:
            Fabric:
                parentContainerName: Tenant
            Spines:
                parentContainerName: Fabric
                configlets:
                    - container_configlet
      tasks:
        - name: 'running cv_container'
          arista.cvp.cv_container_v3:
            topology: "{{CVP_CONTAINERS}}"

    # task in strict mode
    - name: Create container topology on CVP
      hosts: cvp
      connection: local
      gather_facts: no
      vars:
        verbose: False
        containers:
            Fabric:
                parentContainerName: Tenant
            Spines:
                parentContainerName: Fabric
                configlets:
                    - container_configlet
      tasks:
        - name: 'running cv_container'
          arista.cvp.cv_container_v3:
            topology: "{{CVP_CONTAINERS}}"
            apply_mode: strict

### Author

-   EMEA AS Team (@aristanetworks)
