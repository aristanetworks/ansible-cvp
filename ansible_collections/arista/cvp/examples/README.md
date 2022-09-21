# Ansible-CVP Example Playbooks

This section contains a number of sample ansible playbooks to demonstrate the features in question. The description of each playbook notes the actions taken, as well as any specific vars that may need to be adjusted for your own applications.

## Playbooks

### [Assign Image Bundle To Device](./assign-image-bundle-to-device.yaml)

This playbook assigns an image bundle (already existing on the server) named `leaf_bundle` to the switch (with serial number `JPE504a004ea054`).

As it is running in strict mode (not required) we also provide the list of configlets.

Note: This playbook will create a task to deploy the image bundle to the device, but this will *not* be executed.
