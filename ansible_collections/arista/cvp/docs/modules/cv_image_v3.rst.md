# cv_image_v3

Create, Delete, or Update CloudVision Portal Images and Image Bundles.

Module added in version 3.0.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVison Portal Image allows you to upload an EOS, or other software image into CVP, get a list of CVP images or image Bundles. The bundle mode allows for the creation of a named EOS bundle (consisting of one or more images present on the system), update of the bundle, or deletion of the bundle.

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
<td>mode<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>image</td>
<td><ul><li>image</li><li>bundle</li></ul></td>
<td>
    <div>Indicate if you are looking to work with software images, or image bundles</div>
</td>
</tr>

<tr>
<td>action<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td>get</td>
<td><ul><li>get</li><li>add</li><li>remove</li></ul></td>
<td>
    <div>Get a list of images/bundles, add a new image/bundle, or remove an image bundle (see caveats)</div>
</td>
</tr>

<tr>
<td>image<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>Name of the image file, including path if needed (when adding a bundle)</div>
</td>
</tr>

<tr>
<td>image_list<br/><div style="font-size: small;"></div></td>
<td>list of str</td>
<td>yes, when adding/updating bundles</td>
<td></td>
<td></td>
<td>
    <div>List of image names</div>
</td>
</tr>

<tr>
<td>bundle_name<br/><div style="font-size: small;"></div></td>
<td>str</td>
<td>no</td>
<td></td>
<td></td>
<td>
    <div>Name of the image bundle</div>
</td>
</tr>

</table>
</br>

## Examples:

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

## Caveats

- If running in bundle-add mode, and the `bundle_name` already exists, then the existing bundle is updated to match the new image list
- When uploading large images, the connection may time out with the default settings. The solution is to add the following `vars` to the task
```yaml
      vars: 
        ansible_command_timeout: 1200
        ansible_connect_timeout: 600
```
- When removing a bundle, if the image contained within the bundle is not in use anywhere else, it will be deleted

### Author

-   EMEA AS Team (@aristanetworks)
