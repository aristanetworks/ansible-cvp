<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_image_v3

EOS Image management with CloudVision

Module added in version 3.3.0
## Synopsis

CloudVision Portal Image management module.

Due to a current limitation in CloudVision API,
authentication with token is not supported for this module only.

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| image  |   str | False  |  | | Name of the image file, including path if needed. |
| image_list  |   list | False  |  | | List of name of the image file, including path if needed. |
| bundle_name  |   str | False  |  | | Name of the bundle to manage. |
| mode  |   str | False  |  image  | <ul> <li>bundle</li>  <li>image</li> </ul> | What to manage with the module. |
| action  |   str | False  |  get  | <ul> <li>get</li>  <li>add</li>  <li>remove</li> </ul> | Action to perform with the module. |


## Examples

```yaml

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

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).


## Author

Ansible Arista Team (@aristanetworks)
