<!--
  ~ Copyright (c) 2023-2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# How to test PR

## Setup

- Deploy an [ATD](http://testdrive.arista.com) instance with `Datacenter` topology and `ceos` image
- Wait for your topology to deploy and drop into `Programmability IDE`
- On the terminal, run the install script to setup the environment for testing:

  - ```shell
    cd persist
    ```

  - ```shell
    wget https://raw.githubusercontent.com/aristanetworks/ansible-cvp/devel/tests/PR_testing/install.sh
    ```

  - ```shell
    sh install.sh <pr-number>
    ```

  - This script would place the ansible-cvp PR code base under `persist/arista-ansible` and example playbooks under `persist/PR_testing/examples`

- Export the ATD lab password using:

  ```shell
  export LABPASSPHRASE=`cat /home/coder/.config/code-server/config.yaml| grep "password:" | awk '{print $2}'`
  ```

  > NOTE: This has to be exported every time a new terminal session is created (including lab reboot).

## Run Example Playbooks

- Change directory to `persist/PR_testing`

  ```shell
  cd persist/PR_testing
  ```

- Run the desired playbook:

  ```shell
  ansible-playbook cv_device_v3/device_validate_config_valid.yaml -i inventory.yml
  ```

  > NOTE: If not using ATD update the `ansible_password` in `PR_testing/inventory.yml`.

## Run molecule tests

- Run the molecule test:
  - Navigate to `/home/coder/project/persist/arista-ansible/ansible-cvp/ansible_collections/arista/cvp` and run `/home/coder/.local/bin/molecule converge -s <molecule-scenario>`
    - eg:

    ```shell
    /home/coder/.local/bin/molecule converge -s cv_device_v3
    ```

  > NOTE: If not using ATD update the `ansible_password` in `ansible_collection/arista/cvp/examples/inventory.yml`.

HAPPY TESTING!
