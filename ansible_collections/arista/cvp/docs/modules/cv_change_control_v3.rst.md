# cv_image_v3

EOS Image management with Cloudvision

Module added in version 3.X.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVision Portal Change Control Module.


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
<td>name<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>blank</td>
<td></td>
<td>
    <div>Name of the change control. If none is provided for state == set, a name will be generated based on time timestamp.</div>
</td>
</tr>

<tr>
<td>change<br/><div style="font-size: small;"></div></td>
<td>dict</td>
<td>no (unless state==set)</td>
<td></td>
<td></td>
<td>
    <div>A dict containing the details of the CC</div>
</td>
</tr>

<tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>yes</td>
<td>get</td>
<td><ul><li>get</li><li>set</li><li>remove</li></ul></td>
<td>
    <div>Set will create a new CC, unless the 'key' identifying the CC is included</div>
</td>
</tr>


</table>
</br>

## Examples:

    ---
    - name: CVP Image Tests
      hosts: cv_server
      gather_facts: no
      vars:
      tasks:
        - name: "Gather CVP image information facts {{inventory_hostname}}"
          arista.cvp.cv_image_v3:
             mode: image
             action: get
          register: image_data

        - name: "Print out facts from {{inventory_hostname}}"
          debug:
            msg: "{{image_data}}"


        - name: "Get CVP image image bundles {{inventory_hostname}}"
          arista.cvp.cv_image_v3:
            mode: bundle
            action: get
          register: image_bundle_data

        - name: "Print out images from {{inventory_hostname}}"
          debug:
            msg: "{{image_bundle_data}}"


        - name: "Update an image bundle {{inventory_hostname}}"
          vars:
            ansible_command_timeout: 1200
            ansible_connect_timeout: 600
          arista.cvp.cv_image_v3:
            mode: bundle
            action: add
            bundle_name: Test_bundle
            image_list:
               - TerminAttr-1.16.4-1.swix
               - EOS-4.25.4M.swi

### Author

-   EMEA AS Team (@aristanetworks)
