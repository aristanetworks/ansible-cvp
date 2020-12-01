# Debug logs

If required, `arista.cvp` collection supports debug log to get more information about process execution and save all these information in a log file.

> Only for advanced users and support requests.

## Activate debug

In your shell, create a file named `activate-arista-cvp-log.sh`:

```shell
$ vim activate-arista-cvp-log.sh

#!/bin/sh

if [[ ! -z ANSIBLE_CVP_LOG_FILE ]]; then
    export ANSIBLE_CVP_LOG_FILE=arista.cvp.debug.log
fi
if [[ ! -z ANSIBLE_CVP_LOG_LEVEL ]]; then
    export ANSIBLE_CVP_LOG_LEVEL=debug
fi
if [[ ! -z ANSIBLE_CVP_LOG_APICALL ]]; then
    export ANSIBLE_CVP_LOG_APICALL=warning
fi

echo "Configure module for logging:"
echo "  - Logging Level: ${ANSIBLE_CVP_LOG_LEVEL}"
echo "  - Logging File: ${ANSIBLE_CVP_LOG_FILE}"
echo "  - URL Lib logging: ${ANSIBLE_CVP_LOG_APICALL}"
```

Then, when you want to activate log, run this command:

```shell
$ source activate-arista-cvp-log.sh
Configure module for logging:
  - Logging Level: debug
  - Logging File: arista.cvp.debug.log
  - URL Lib logging: warning
```

## Get debug logs

After your run your playbook, a log file should be available in your shell and you can read it with following command:

```shell
$ less arista.cvp.debug.log

[...]
2020-10-05 18:13:43,065 - arista.cvp.cv_facts: INFO - func: facts_builder (L:429) - ** Collecting configlets facts ...
2020-10-05 18:13:43,066 - arista.cvp.cv_facts: INFO - func: facts_configlets (L:246) - Collecting facts v2
2020-10-05 18:13:44,700 - arista.cvp.cv_facts: INFO - func: facts_configlets (L:253) - Devices part of facts, using cached version
2020-10-05 18:13:44,700 - arista.cvp.cv_facts: INFO - func: facts_configlets (L:260) - Containers part of facts, using cached version
2020-10-05 18:13:44,700 - arista.cvp.cv_facts: INFO - func: facts_configlets (L:273) - building list of mapping with devices and containers for configlet AVD_DC1-LEAF2B
2020-10-05 18:13:44,700 - arista.cvp.tools_inventory: DEBUG - func: find_hostname_by_mac (L:49 ) - device data: {'modelName': 'vEOS', 'internalVersion': '4.24.0F', 'systemMacAddress': '0c:1d:c0:7f:d9:6c', 'bootupTimestamp': 1600691806.3303108, 'version': '4.24.0F', 'architecture': '', 'internalBuild': 'da8d6269-c25f-4a12-930b-c3c42c12c38a', 'hardwareRevision': '', 'domainName': 'eve.emea.lab', 'hostname': 'DC1-LEAF2B', 'fqdn': 'DC1-LEAF2B.eve.emea.lab', 'serialNumber': '86277F11ED731FAA3943F1838B6799AA', 'danzEnabled': False, 'mlagEnabled': False, 'streamingStatus': 'active', 'parentContainerKey': 'container_99ea374c-7bc7-454a-b529-31fd181edab3', 'status': 'Registered', 'complianceCode': '0000', 'complianceIndication': '', 'ztpMode': False, 'unAuthorized': False, 'ipAddress': '10.73.1.16', 'key': '0c:1d:c0:7f:d9:6c', 'deviceInfo': 'Registered', 'deviceStatus': 'Registered', 'isMLAGEnabled': False, 'isDANZEnabled': False, 'parentContainerId': 'con:
[...]
```
