# Common Error messages

> All Ansible error messages should be read from bottom to top.

## cv_facts error messages

### Unsupported CV version

Prior version __2.0.0__ `arista.cvp` collection ran test to determine Cloudvision version. If version is not supported, following error should happen:

```shell
\"/var/folders/q0/92fg6g7s1bv6kgfdcgfjwt0c0000gp/T/ansible_arista.cvp.cv_facts_payload_2ld7vf9v/ansible_arista.cvp.\
cv_facts_payload.zip/ansible_collections/arista/cvp/plugins/modules/cv_facts.py\", line 359, in facts_builder\n\
AttributeError: 'NoneType' object has no attribute 'get_cvp_info'\n", "module_stdout": "", "msg": "MODULE \
FAILURE\nSee stdout/stderr for the exact error", "rc": 1}
```

## cv_container

### Missing Treelib requirement

[Treelib](https://treelib.readthedocs.io/en/latest/) is a python library used to build container topology. When missing, Ansible raise following error message

```shell
\"/tmp/ansible_arista.cvp.cv_container_payload_YG2p15/ansible_arista.cvp.cv_container_payload.zip/ansible_collections\
/arista/cvp/plugins/modules/cv_container.py\", line 254, in tree_build_from_dict\n\
NameError: global name 'Tree' is not defined\n",
```

With newer version of the collection, module should fails with an specific message like below:

```shell
TASK [running cv_container in merge on cv_server] *****************************
Wednesday 07 October 2020  08:21:50 +0200 (0:00:20.050)       0:00:20.114 *****
Wednesday 07 October 2020  08:21:50 +0200 (0:00:20.050)       0:00:20.114 *****
fatal: [cv_server]: FAILED! => changed=false
  msg: treelib required for this module
```
