# How to test PR

- Deploy an [ATD](http://testdrive.arista.com) instance with `Datacenter` topology
- Wait for your topology to deploy and drop into `Programmability IDE`
- On the terminal, run the install script to setup the environment for testing:
  - `cd persist`
  - `curl -fsSL https://github.com/aristanetworks/ansible-cvp/tree/devel/tests/PR_testing/install.sh <PR-number> | sh`
  - This script would place the ansible-cvp PR code base under `persist/arista-ansible` and example playbooks under `persist/PR_testing/examples`
- Edit `persist/PR_testing/inventory.yaml`
  - Update the `ansible_httpapi_host` and `ansible_host` variables under `CloudVision`
  - Update the `ansible_user` and `ansible_password` variables under `CloudVision`

    ```yaml
    ...
    CloudVision:
        ansible_httpapi_host: <testvalidateconfig-1-0cdc46b0.topo.testdrive.arista.com>
        ansible_host: <testvalidateconfig-1-0cdc46b0.topo.testdrive.arista.com>
        ansible_user: <lab credential username>
        ansible_password: <lab credential password>
    ...
    ```

- From `persist` directory, you can run the desired playbook and start testing the PR.

HAPPY TESTING!
