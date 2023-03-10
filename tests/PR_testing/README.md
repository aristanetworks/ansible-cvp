# How to test PR

- Deploy an [ATD](http://testdrive.arista.com) instance with `Datacenter` topology and `ceos` image
- Wait for your topology to deploy and drop into `Programmability IDE`
- On the terminal, run the install script to setup the environment for testing:
  - `cd persist`
  - `wget https://raw.githubusercontent.com/aristanetworks/ansible-cvp/devel/tests/PR_testing/install.sh`
  - `sh install.sh <pr-number>`
  - This script would place the ansible-cvp PR code base under `persist/arista-ansible` and example playbooks under `persist/PR_testing/examples`
- Edit `persist/PR_testing/inventory.yaml`
  - Update the `ansible_password` variables under `CloudVision`

    ```yaml
    ...
    CloudVision:
        ...
        ansible_password: <lab credential password>
        ...
    ...
    ```

- `cd persist/PR_testing`
- Run the desired playbook:
  - `ansible-playbook cv_device_v3/device_validate_config_valid.yaml -i inventory.yaml`

HAPPY TESTING!
