# cv_container_v3

Manage Provisioning topology.

Module added in version 3.0.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVision Portal Configlet configuration requires a dictionary of
containers with their parent, to create and delete containers on CVP
side The Module also supports assigning configlets at the container
level Returns number of created and/or deleted containers With the
argument <span class="title-ref">apply_mode</span> set to <span
class="title-ref">loose</span> the module will only add new containers
When <span class="title-ref">apply_mode</span> is set to <span
class="title-ref">strict</span> the module will try to remove
unspecified containers from CloudVision. This will fail if the container
has configlets attached to it or devices are placed in the container.

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
    <div>Set how configlets are attached/detached to containers. If set to strict all configlets not listed in your vars will be detached.</div>
</td>
</tr>

<tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>present</td>
<td><ul><li>present</li><li>absent</li></ul></td>
<td>
    <div>Set if Ansible should build or remove devices on CloudVision</div>
</td>
</tr>

<tr>
<td>topology<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>YAML dictionary to describe intended containers</div>
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
            topology: "{{containers}}"

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
            topology: "{{containers}}"
            apply_mode: strict

### Author

- Ansible Arista Team (@aristanetworks)

### Full Schema

Get full schema docs [here](../../schema/cv_container_v3/).
