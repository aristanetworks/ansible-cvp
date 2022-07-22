# cv_tag_v3

Create/Assign/Delete/Unassign tags on CVP

Module added in version 3.4.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVison Portal Tag module to Create/Assign/Delete/Unassign tags on
CloudVision

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
<td>auto_create<br/><div style="font-size: small;"></div></td>
<td>bool</td>
<td>no</td>
<td>True</td>
<td><ul><li>yes</li><li>no</li></ul></td>
<td>
    <div>auto_create tags before assigning</div>
</td>
</tr>

<tr>
<td>mode<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td></td>
<td><ul><li>create</li><li>delete</li><li>assign</li><li>unassign</li></ul></td>
<td>
    <div>action to carry out on the tags create - create tags delete - delete tags assign - assign existing tags to device unassign - unassign existing tags from device</div>
</td>
</tr>

<tr>
<td>tags<br/><div style="font-size: small;"></div></td>
<td>list</td>
<td>yes</td>
<td></td>
<td></td>
<td>
    <div>CVP tags</div>
</td>
</tr>

</table>
</br>

## Examples:

    ---
    - name: "create tags"
      arista.cvp.cv_tag_v3:
        tags: "{{CVP_TAGS}}"
        mode: create
        auto_create: true

### Author

-   Ansible Arista Team (@aristanetworks)
