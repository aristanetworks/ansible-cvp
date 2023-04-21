# How to test PR

## Setup

- Deploy an [ATD](http://testdrive.arista.com) instance with `Datacenter` topology and `ceos` image

- Wait for your topology to deploy and drop into `Programmability IDE`
- On the terminal, run the install script to setup the environment for testing:

  ```shell
  cd persist
  wget https://raw.githubusercontent.com/aristanetworks/ansible-cvp/devel/tests/PR_testing/install.sh
  sh install.sh <pr-number>
  ```

  - This script would place the ansible-cvp PR code base under `persist/arista-ansible` and example playbooks under `persist/PR_testing/examples`

## Run Example Playbooks

- Edit `persist/PR_testing/inventory.yml`
  - Update the `ansible_password` variables under `CloudVision`

    ```yaml
    ...
    CloudVision:
        ...
        ansible_password: <lab credential password>
        ...
    ...
    ```

- Change directory to `persist/PR_testing`

  ```shell
  cd persist/PR_testing
  ```

- Run the desired playbook:

  ```shell
  ansible-playbook cv_device_v3/device_validate_config_valid.yaml -i inventory.yml
  ```

## Run molecule tests

- Edit `persist/arista-ansible/ansible_collection/arista/cvp/examples/inventory.yml`
  - Update `ansible_password` variable under `CloudVision`
- Run:
  - Navigate to `/home/coder/project/persist/arista-ansible/ansible-cvp/ansible_collections/arista/cvp` and run `/home/coder/.local/bin/molecule converge -s <molecule-scenario>`
  - eg:

    ```shell
    /home/coder/.local/bin/molecule converge -s cv_device_v3
    ```

HAPPY TESTING!
