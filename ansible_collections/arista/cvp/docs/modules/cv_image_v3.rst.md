# cv_image_v3

EOS Image management with Cloudvision

Module added in version 3.3.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVision Portal Image management module.

Due to a current limitation in Cloudvision API, authentication with
token is not supported for this module only.

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
<td>action<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>get</td>
<td><ul><li>get</li><li>add</li><li>remove</li></ul></td>
<td>
    <div>Action to do with module</div>
</td>
</tr>

<tr>
<td>bundle_name<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>Name of the bundle to manage</div>
</td>
</tr>

<tr>
<td>image<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>Name of the image file, including path if needed</div>
</td>
</tr>

<tr>
<td>image_list<br/><div style="font-size: small;"></div></td>
<td>list</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>List of name of the image file, including path if needed</div>
</td>
</tr>

<tr>
<td>mode<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>image</td>
<td><ul><li>bundle</li><li>image</li></ul></td>
<td>
    <div>What to manage with module</div>
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
