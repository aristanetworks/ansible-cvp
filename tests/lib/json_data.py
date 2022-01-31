#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable = duplicate-code
# flake8: noqa: R0801
#
# GNU General Public License v3.0+
#
# Copyright 2019 Arista Networks AS-EMEA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
json_data.py - Declares & initializes the variables and mock data used in the testcases.
"""

from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas.v3 import SCHEMA_CV_CONTAINER, SCHEMA_CV_DEVICE, SCHEMA_CV_CONFIGLET
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from .static_content import CONFIGLET_CONTENT

# Mapping between data name and its schema
schemas = {}

# Mook data to use in validation
mook_data = {}
# Mapping between data name and valid examples
mook_data["valid"] = {}
# Mapping between data name and invalid examples
mook_data["invalid"] = {}

# Methods allowed to search devices
search_methods = {}
# Fake container topology
container_topology = []

modes = ["valid", "invalid"]

#######################################
# Module to schema mapping
#######################################

schemas["container"] = SCHEMA_CV_CONTAINER
schemas["device"] = SCHEMA_CV_DEVICE
schemas["configlet"] = SCHEMA_CV_CONFIGLET

#########################################
# Search methods allowed in cv_device_v3
#########################################

search_methods = [Api.device.FQDN, Api.device.SYSMAC]

#######################################
# Container Examples
#######################################

mook_data["valid"]["container"] = [
    {
        "PYTEST": {
            "parentContainerName": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "PYTEST"
        },
        "Spines": {
            "parentContainerName": "PYTEST",
            "configlets": [
                "01TRAINING-01"
            ]
        },
        "POD01": {
            "parentContainerName": "Leafs"
        }
    },
    {
        "DC-2": {
            "parentContainerName": "Tenant"
        },
        "DC_Leafs": {
            "parentContainerName": "DC-2"
        }
    },
    {
        "DC1_BL1": {
            "parentContainerName": "DC1_L3LEAFS"
        },
        "DC1_FABRIC": {
            "parentContainerName": "Tenant"
        },
        "DC1_L2LEAF1": {
            "parentContainerName": "DC1_L2LEAFS"
        },
        "DC1_L2LEAF2": {
            "parentContainerName": "DC1_L2LEAFS"
        },
        "DC1_L2LEAFS": {
            "parentContainerName": "DC1_FABRIC"
        },
        "DC1_L3LEAFS": {
            "parentContainerName": "DC1_FABRIC"
        },
        "DC1_LEAF1": {
            "parentContainerName": "DC1_L3LEAFS"
        },
        "DC1_LEAF2": {
            "parentContainerName": "DC1_L3LEAFS"
        },
        "DC1_LEAF3": {
            "parentContainerName": "DC1_L3LEAFS"
        },
        "DC1_LEAF4": {
            "parentContainerName": "DC1_L3LEAFS"
        },
        "DC1_SPINES": {
            "parentContainerName": "DC1_FABRIC"
        }
    },
    {
        "DC2": {
            "parentContainerName": "Tenant"
        }
    },
    {
        "DC2": {
            "parentContainerName": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "DC2"
        },
        "Spines": {
            "parentContainerName": "DC2",
            "configlets": [
                "01TRAINING-01"
            ]
        }
    },
    {
        "DC2": {
            "parentContainerName": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "DC2"
        },
        "Spines": {
            "parentContainerName": "DC2",
            "configlets": [
                "01TRAINING-01"
            ]
        },
        "POD01": {
            "parentContainerName": "Leafs"
        }
    },
    {
        "DC-2": {
            "parentContainerName": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "DC-2"
        }
    }
]

mook_data["invalid"]["container"] = [
    {
        "PYTEST": {
            "parent_container": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "PYTEST"
        },
        "Spines": {
            "parentContainerName": "PYTEST",
            "configlets": [
                "01TRAINING-01"
            ]
        },
        "POD01": {
            "parentContainerName": "Leafs"
        }
    },
    {
        "PYTEST": {
            "default": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "PYTEST"
        },
        "Spines": {
            "parentContainerName": "PYTEST",
            "configlets": [
                "01TRAINING-01"
            ]
        }
    }
]

#######################################
# Device Examples
#######################################

mook_data["valid"]["device"] = [
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
    }],
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
        "fqdn": "DC1-SPINE2",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ]
    }],
    [{
        "fqdn": "DC1-SPINE3",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES"
    },
        {
        "fqdn": "DC1-SPINE4",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "imageBundle": []
    }]
]

mook_data["invalid"]["device"] = [
    [{
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ],
        "imageBundle": []
    }]
]

#######################################
# Configlet Examples
#######################################

mook_data["valid"]["configlet"] = [
        {"configlet_device01": "alias sib show version"},
        {"configlet-device01": "alias sib show version"},
        {"configlet-device_01": CONFIGLET_CONTENT},
]

mook_data["invalid"]["configlet"] = [
        {"configlet_device01": 100},
        {"configlet_device02": True},
        {"configlet_device02": False},
        {"configlet-device_01": "alias sib show version", 'version': 1},
]

#######################################
# Container Topology
#######################################

CONTAINER_IDS = ["Tenant", "container-1111-2222-3333-4444",
                 "container_222_ccc_rrr"]

container_topology = [
    {
        "DC2": {
            "parentContainerName": "Tenant"
        }
    },
    {
        "DC2": {
            "parentContainerName": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "DC2"
        },
        "Spines": {
            "parentContainerName": "DC2",
            "configlets": [
                "01TRAINING-01"
            ]
        }
    },
    {
        "DC2": {
            "parentContainerName": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "DC2"
        },
        "Spines": {
            "parentContainerName": "DC2",
            "configlets": [
                "01TRAINING-01"
            ]
        },
        "POD01": {
            "parentContainerName": "Leafs"
        }
    },
    {
        "DC-2": {
            "parentContainerName": "Tenant"
        },
        "Leafs": {
            "parentContainerName": "DC-2"
        }
    }
]

##############################################
# CVP data used to mock cvprac.api.CvpClient #
##############################################

CVP_DATA_CONTAINERS = {
    'Tenant': {'name': 'Tenant',
               'key': 'root',
               'root': True,
               'undefined': False,
               'userId': 'cvp system',
               'dateTimeInLongFormat': 1639759767913,
               'mode': 'expand'},
    'ansible-cvp-tests-1': {'name': 'ansible-cvp-tests-1',
                            'key': 'container_274787b2-c45a-4b0c-8b97-eb4011909b02',
                            'root': False,
                            'undefined': False,
                            'userId': 'cvpadmin',
                            'dateTimeInLongFormat': 1640359353713,
                            'mode': 'expand'},
    'Simple Fabric': {'name': 'Simple Fabric',
                      'key': 'container_6ac90bc0-f6d4-436f-bff0-8c064c247f01',
                      'root': False,
                      'undefined': False,
                      'userId': 'cvpadmin',
                      'dateTimeInLongFormat': 1640019781757,
                      'mode': 'expand'},
    'BadKey': {'bad_name': 'BadKey',
               'bad_key': 'root',
               'bad_root': True,
               'bad_undefined': False,
               'bad_userId': 'cvp system',
               'bad_dateTimeInLongFormat': 1639759767913,
               'bad_mode': 'expand'},
    'NotExists': None
}

##############################################
# CVP data used to play with Facts           #
##############################################

mook_data['valid']['facts']= {
    'device_ids': ['50:01:00:1e:cf:92']
}
mook_data['invalid']['facts']= {
    'device_ids': ['00:00:00:00:00:00']
}
