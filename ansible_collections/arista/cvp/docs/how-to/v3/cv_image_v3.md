# Configure Images and Image Bundles on Cloudvision

__cv_image_v3__ manage devices on CloudVision:

- Support images package upload
- Support listing existing image bundles
- Support creating and deleting image bundles

!!! warning
    Because of a current limitation in CV API, token based authentication is not supported at the moment.

## Modules options

- `action`: Action to do with module. Can be one of the following: `get`, `add`, `remove`
- `mode`: What to manage with the module. Can be either `image` or `bundle`
- `bundle_name`: Name of the bundle to take care.
- `image`: File path of the image to upload
- `image_list`: List of file paths to upload to cloudvision


## Specific settings

As this module is in charge of uploading large files to Cloudvision, it is highly recommended to change the default value for [ansible_command_timeoutandansible_connect_timeout](https://docs.ansible.com/ansible/latest/network/getting_started/network_connection_options.html) to allow ansible enough time to upload the files.

As it is dependant of execution environment, these values must be defined by user and it can be updated only for a specific task:

```yaml
- name: Update Image bundle
    hosts: cv_server
    gather_facts: no
    tasks:
        - name: "Update an image bundle {{inventory_hostname}}"
          vars:
            ansible_command_timeout: < your defined timeout value>
            ansible_connect_timeout: < your defined timeout value>
...
```

## Examples

### Get list of images

```yaml
---
- name: Get Image list from Cloudvision
    hosts: cv_server
    gather_facts: no
    vars:
    tasks:
    - name: "Gather CVP image information facts {{inventory_hostname}}"
        arista.cvp.cv_image_v3:
            mode: image
            action: get
        register: image_data
```

### Update an image bundle

```yaml
- name: Update Image bundle
    hosts: cv_server
    gather_facts: no
    vars:
    tasks:
        - name: "Update an image bundle {{inventory_hostname}}"
          vars:
            ansible_command_timeout: 1200
            ansible_connect_timeout: 1200
          arista.cvp.cv_image_v3:
            mode: bundle
            action: add
            bundle_name: Test_bundle
            image_list:
               - '../images/swix/TerminAttr-1.16.4-1.swix'
               - '~/EOS-4.25.4M.swi'
```
