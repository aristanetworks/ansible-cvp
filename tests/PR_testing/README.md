# How to test PR

- Deploy an [ATD](http://testdrive.arista.com) instance with `Datacenter` topology and `ceos` image
- Wait for your topology to deploy and drop into `Programmability IDE`
- On the terminal, run the install script to setup the environment for testing:
  - `cd persist`
  - `wget https://raw.githubusercontent.com/aristanetworks/ansible-cvp/devel/tests/PR_testing/install.sh`
  - `sh install.sh <pr-number>`
  - This script would place the ansible-cvp PR code base under `persist/arista-ansible` and example playbooks under `persist/PR_testing/examples`
- export the ATD lab password using:

  ```shell
  export LABPASSPHRASE=`cat /home/coder/.config/code-server/config.yaml| grep "password:" | awk '{print $2}'`
  ```

  > NOTE: This has to be exported everytime a new terminal session is created (including lab reboot).

- `cd persist/PR_testing`
- Run the desired playbook:
  - `ansible-playbook cv_device_v3/device_validate_config_valid.yaml -i inventory.yml`
- Run molecule tests:
  - Edit `persist/arista-ansible/ansible_collection/arista/cvp/examples/inventory.yml`
  - Run:
    - Navigate to `/home/coder/project/persist/arista-ansible/ansible-cvp/ansible_collections/arista/cvp` and run
    - `/home/coder/.local/bin/molecule converge -s <molecule-scenario>`
      - eg: `/home/coder/.local/bin/molecule converge -s cv_device_v3`

If not using ATD update the `ansible_password` in `ansible_collection/arista/cvp/examples/inventory.yml` and in `PR_testing/inventory.yml`.

HAPPY TESTING!
