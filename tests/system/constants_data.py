# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""
constants_data.py - Initializes variables used in the system testcases.
"""

USER_CONTAINERS = [
    {"PYTEST": {"parentContainerName": "Tenant"}, "Leafs": {"parentContainerName": "PYTEST"}, "Spines": {
        "parentContainerName": "PYTEST", "configlets": ["leaf-1-unit-test"]}, "POD01": {"parentContainerName": "Leafs"}},
    {"DC-2": {"parentContainerName": "Tenant"}, "DC_Leafs": {
        "parentContainerName": "DC-2"}}
]

CV_CONTAINERS_NAME_ID_LIST = [{"name": "Tenant", "id": "root"}]

STATIC_CONFIGLET_NAME_ATTACH = ["leaf-1-unit-test"]

STATIC_CONFIGLET_NAME_DETACH = [{"name": "leaf-1-unit-test"}]

TOPOLOGY_STATE = ["present", "absent"]

ANSIBLE_CV_SEARCH_MODE = "hostname"

CVP_DEVICES = [
    {
        "fqdn": "leaf-1-unit-test.ire.aristanetworks.com",
        "hostname": "leaf-1-unit-test",
        "serialNumber": "A2BC886CB9408A0453A3CFDD9C251999",
        "systemMacAddress": "50:00:00:d5:5d:c0",
        "parentContainerName": "ansible-cvp-tests",
        "configlets": [
                "leaf-1-unit-test"
        ],
    }
]

CVP_DEVICES_1 = [
    {
        "fqdn": "spine-2-unit-test.ire.aristanetworks.com",
        "hostname": "spine-2-unit-test",
        "serialNumber": "08A7E527AF711F688A6AD7D78BB5AD0A",
        "systemMacAddress": "50:00:00:cb:38:c2",
        "parentContainerName": "ansible-cvp-tests",
        "configlets": [],
    }
]

CVP_DEVICES_UNKNOWN = [
    {
        "fqdn": "CV-ANSIBLE-TEST01.ire.aristanetworks.com",
        "hostname": "CV-ANSIBLE-TEST01",
        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE",
        "configlets": [
                "01TRAINING-01",
                "CV-EOS-ANSIBLE01"
        ],
        "imageBundle": "test_image_bundle"
    },
    {
        "fqdn": "TEST.ire.aristanetworks.com",
        "hostname": "TEST",
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
        "imageBundle": "test_image_bundle"
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
        "imageBundle": "test_image_bundle"
    }]
]

CHECK_MODE = True

CONTAINER_DESTINATION = "ansible-cvp-tests-2"
