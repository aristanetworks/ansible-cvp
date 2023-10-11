# cv_facts_v3

Collect facts from CloudVision

Module added in version 3.3.0
## Synopsis

Returns list of devices, configlets, containers, images and tasks from CloudVision

## Module-specific Options

The following options may be specified for this module:

| parameter | type | required | default | choices | comments |
| ------------- |-------------| ---------|----------- |--------- |--------- |
| facts  |   list | False  |  ['configlets', 'containers', 'devices', 'images', 'tasks']  | <ul> <li>configlets</li>  <li>containers</li>  <li>devices</li>  <li>images</li>  <li>tasks</li> </ul> |  <ul> <li>List of facts to retrieve from CVP.</li>  <li>By default, cv_facts returns facts for devices, configlets, containers, images, and tasks.</li>  <li>Using this parameter allows user to limit scope to a subset of information.</li> </ul> |
| regexp_filter  |   str | False  |  .*  | | Regular Expression to filter containers, configlets, devices and tasks in facts. |
| verbose  |   str | False  |  short  | <ul> <li>long</li>  <li>short</li> </ul> | Get all data from CVP or get only cv_modules data. |


## Examples

```yaml

  tasks:
  - name: '#01 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:

  - name: '#02 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - configlets
    register: FACTS_DEVICES

  - name: '#03 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - devices
        - containers
    register: FACTS_DEVICES

  - name: '#04 - Collect devices facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - devices
      regexp_filter: "spine1"
      verbose: long
    register: FACTS_DEVICES

  - name: '#05 - Collect images facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - images
    register: FACTS_DEVICES

  - name: '#06 - Collect task facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - tasks
      regexp_filter: 'Pending' # get facts filtered by task status - 'Failed', 'Pending', 'Completed', 'Cancelled'
      verbose: 'long'
    register: FACTS_DEVICES

  - name: '#07 - Collect task facts from {{inventory_hostname}}'
    arista.cvp.cv_facts_v3:
      facts:
        - tasks
      regexp_filter: 95 # get facts filtered by task_Id (int)
      verbose: 'long'
    register: FACTS_DEVICES

```

## Author

Ansible Arista Team (@aristanetworks)

