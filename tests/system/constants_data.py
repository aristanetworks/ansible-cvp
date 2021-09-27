"""
constants_data.py - Initializes variables used in the system testcases.
"""


USER_CONTAINERS = [
    {"PYTEST": {"parentContainerName": "Tenant"}, "Leafs": {"parentContainerName": "PYTEST"}, "Spines": {
        "parentContainerName": "PYTEST", "configlets": ["01TRAINING-01"]}, "POD01": {"parentContainerName": "Leafs"}},
    {"DC-2": {"parentContainerName": "Tenant"}, "DC_Leafs": {
        "parentContainerName": "DC-2"}}
]

CV_CONTAINERS_NAME_ID_LIST = [{"name": "Tenant", "id": "root"}]

STATIC_CONFIGLET_NAME = ["01TRAINING-01"]

TOPOLOGY_STATE = ["present", "absent"]

ANSIBLE_CV_SEARCH_MODE = "hostname"
# IS_HOSTNAME_SEARCH = True

CVP_DEVICES = [
    {
        "fqdn": "CV-ANSIBLE-EOS01",
        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE",
        "configlets": [
                "01TRAINING-01",
                "CV-EOS-ANSIBLE01"
        ],
    }
]

CVP_DEVICES_UNKNOWN = [
    {
        "fqdn": "CV-ANSIBLE-TEST01",
        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE",
        "configlets": [
                "01TRAINING-01",
                "CV-EOS-ANSIBLE01"
        ],
        "imageBundle": []
    },
    {
        "fqdn": "TEST",
        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE",
    }
]

CVP_DEVICES_SCHEMA_TEST = [
    [{
        "fqdn": "DC1-SPINE1.eve.emea.lab",
        "serialNumber": "ddddddd",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ],
        "imageBundle": []
    }],
    [{
        "fqdn": "DC1-SPINE1",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ]
    }],
    [{
        "fqdn": "DC1-SPINE1",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES"
    }],
    [{
        "fqdn": "DC1-SPINE1",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "imageBundle": []
    }]
]

CHECK_MODE = True

CONTAINER_DESTINATION = "ANSIBLE2"
