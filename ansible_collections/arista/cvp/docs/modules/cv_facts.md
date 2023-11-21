<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# cv_facts

Collect facts from CloudVision Portal.

Module added in version 1.0.0
## Synopsis

Returns list of devices, configlets, containers and images

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| gather_subset  |   list | False  |  ['default']  | <ul> <li>default</li>  <li>config</li>  <li>tasks_pending</li>  <li>tasks_failed</li>  <li>tasks_all</li> </ul> | When supplied, this argument will restrict the facts collected to a given subset.  Possible values for this argument include all, hardware, config, and interfaces. Can specify a list of values to include a larger subset. Values can also be used with an initial `!` to specify that a specific subset should not be collected. |
| facts  |   list | False  |  ['all']  | <ul> <li>all</li>  <li>devices</li>  <li>containers</li>  <li>configlets</li>  <li>tasks</li> </ul> | List of facts to retrieve from CVP. By default, cv_facts returns facts for devices, configlets, containers, and tasks. Using this parameter allows user to limit scope to a subset of information. |


## Examples

```yaml

---
  tasks:
    - name: '#01 - Collect devices facts from {{inventory_hostname}}'
      cv_facts:
        facts:
          devices
      register: FACTS_DEVICES

    - name: '#02 - Collect devices facts (with config) from {{inventory_hostname}}'
      cv_facts:
        gather_subset:
          config
        facts:
          devices
      register: FACTS_DEVICES_CONFIG

    - name: '#03 - Collect confilgets facts from {{inventory_hostname}}'
      cv_facts:
        facts:
          configlets
      register: FACTS_CONFIGLETS

    - name: '#04 - Collect containers facts from {{inventory_hostname}}'
      cv_facts:
        facts:
          containers
      register: FACTS_CONTAINERS

    - name: '#10 - Collect ALL facts from {{inventory_hostname}}'
      cv_facts:
      register: FACTS

```

For a complete list of examples, check them out on our [GitHub repository](https://github.com/aristanetworks/ansible-cvp/tree/devel/ansible_collections/arista/cvp/examples).

## Module output

??? output "Example output"
    ```yaml
    --8<--
    docs/outputs/cv_facts.txt
    --8<--
    ```

## Author

Ansible Arista Team (@aristanetworks)
