# Collections Plugins Directory

<<<<<<< HEAD
`arista.cvp` collection provides a set of plugins to configure Arista EOS devices with a CloudVision Platform server.

__List of available modules__

- __arista.cvp.cv_facts__ - Collect CVP facts from server like list of containers, devices, configlet and tasks.
- __arista.cvp.cv_configlet__:  Manage configlet configured on CVP.
- __arista.cvp.cv_container__:  Manage container topology and attach configlet and devices to containers.
- __arista.cvp.cv_device__: Manage devices configured on CVP
- __arista.cvp.cv_task__:  Run tasks created on CVP.
=======
This directory can be used to ship various plugins inside an Ansible collection. Each plugin is placed in a folder that
is named after the type of plugin it is in. It can also include the `module_utils` and `modules` directory that
would contain module utils and modules respectively.

Here is an example directory of the majority of plugins currently supported by Ansible:

```
└── plugins
    ├── action
    ├── become
    ├── cache
    ├── callback
    ├── cliconf
    ├── connection
    ├── filter
    ├── httpapi
    ├── inventory
    ├── lookup
    ├── module_utils
    ├── modules
    ├── netconf
    ├── shell
    ├── strategy
    ├── terminal
    ├── test
    └── vars
```

A full list of plugin types can be found at [Working With Plugins](https://docs.ansible.com/ansible/devel/plugins/plugins.html).
>>>>>>> upstream/grant-release
