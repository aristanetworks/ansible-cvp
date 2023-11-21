#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable = duplicate-code
# flake8: noqa: R0801
#


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


# JSON Schema to represent CV_CONFIGLET inputs.
SCHEMA_CV_CONFIGLET = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "title": "CV CONFIGLET SCHEMA",
    "description": "The root schema to validate cv_configlet inputs",
    "default": {},
    "examples": [
        {
            "TEAM01-alias": "alias a1 show version",
            "TEAM01-another-configlet": "alias a2 show version"
        }
    ],
    "type": "object",
    "patternProperties": {
        "^[A-Za-z0-9\\s\\._%\\+-]+$": {
            "type": "string"
        }
    },
    "additionalProperties": False
}

# JSON Schema to represent CV_DEVICE inputs.
SCHEMA_CV_DEVICE = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "array",
    "title": "The root schema",
    "description": "The root schema comprises the entire JSON document.",
    "default": [],
    "examples": [
        [
            {
                "fqdn": "CV-ANSIBLE-EOS01",
                "ipAddress": "192.0.2.100",
                "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
                "systemMacAddress": "50:8d:00:e3:78:aa",
                "parentContainerName": "ANSIBLE2",
                "configlets": [
                    "01TRAINING-01",
                    "CV-EOS-ANSIBLE01"
                ]
            }
        ]
    ],
    "items": {
        "additionalItems": True,
        "$id": "#/items",
        "anyOf": [
            {
                "$id": "#/items/anyOf/0",
                "type": "object",
                "title": "The first anyOf schema",
                "description": "An explanation about the purpose of this instance.",
                "default": {},
                "examples": [
                    {
                        "fqdn": "CV-ANSIBLE-EOS01",
                        "ipAddress": "192.0.2.100",
                        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
                        "systemMacAddress": "50:8d:00:e3:78:aa",
                        "parentContainerName": "ANSIBLE2",
                        "configlets": [
                            "01TRAINING-01",
                            "CV-EOS-ANSIBLE01"
                        ],
                        "imageBundle": "test_bundle"
                    }
                ],
                "anyOf": [
                    {
                        "required": [
                            "fqdn",
                            "parentContainerName",
                        ],
                    },
                    {
                        "required": [
                            "serialNumber",
                            "parentContainerName",
                        ],
                    }
                ],
                "additionalProperties": True,
                "properties": {
                    "ipAddress": {
                        "$id": "#/items/anyOf/0/properties/ipAddress",
                        "type": "string",
                        "title": "The ipAddress schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                            "192.0.2.5"
                        ]
                    },
                    "fqdn": {
                        "$id": "#/items/anyOf/0/properties/fqdn",
                        "type": "string",
                        "title": "The fqdn schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                            "CV-ANSIBLE-EOS01"
                        ]
                    },
                    "serialNumber": {
                        "$id": "#/items/anyOf/0/properties/serialNumber",
                        "type": "string",
                        "title": "The serialNumber schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                            "79AEA53101E7340AEC9AA4819D5E1F5B"
                        ]
                    },
                    "systemMacAddress": {
                        "$id": "#/items/anyOf/0/properties/systemMacAddress",
                        "type": "string",
                        "title": "The systemMacAddress schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                            "50:8d:00:e3:78:aa"
                        ]
                    },
                    "parentContainerName": {
                        "$id": "#/items/anyOf/0/properties/parentContainerName",
                        "type": "string",
                        "title": "The parentContainerName schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                            "ANSIBLE2"
                        ]
                    },
                    "configlets": {
                        "$id": "#/items/anyOf/0/properties/configlets",
                        "type": "array",
                        "title": "The configlets schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": [],
                        "minItems": 0,
                        "examples": [
                            [
                                "01TRAINING-01",
                                "CV-EOS-ANSIBLE01"
                            ]
                        ],
                        "items": {
                            "$id": "#/items/anyOf/0/properties/configlets/items",
                            "anyOf": [
                                {
                                    "$id": "#/items/anyOf/0/properties/configlets/items/anyOf/0",
                                    "type": "string",
                                    "title": "The first anyOf schema",
                                    "description": "An explanation about the purpose of this instance.",
                                    "default": "",
                                    "examples": [
                                        "01TRAINING-01",
                                        "CV-EOS-ANSIBLE01"
                                    ]
                                }
                            ]
                        }
                    },
                    "imageBundle": {
                        "$id": "#/items/anyOf/0/properties/imageBundle",
                        "type": "string",
                        "title": "The imageBundle name",
                        "description": "The imageBundle is the name of the image bundle applied to a container or device.",
                        "default": [],
                        "examples": [
                            "spine_image_bundle"
                        ]
                    }
                },
            }
        ]
    }
}

# JSON Schema to represent CV_CONTAINER inputs.
SCHEMA_CV_CONTAINER = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-03/schema",
    "id": "#",
    "title": "CV CONTAINER SCHEMA",
    "description": "The root schema to validate cv_container inputs",
    "default": {},
    "examples": [
        {
            "DC2": {
                "parentContainerName": "Tenant"
            },
            "Leafs": {
                "parentContainerName": "DC2"
            },
            "Spines": {
                "parentContainerName": "DC2"
            },
            "POD01": {
                "parentContainerName": "Leafs"
            }
        }
    ],
    "required": True,
    "patternProperties": {
        "^[A-Za-z0-9\\._%\\+-]+$": {
            "type": "object",
            "required": True,
            "additionalProperties": False,
            "properties": {
                "parentContainerName": {
                    "id": "parentContainerName",
                    "type": "string",
                    "required": True
                },
                "configlets": {
                    "id": "configlets",
                    "type": "array",
                    "contains": {
                        "type": "string"
                    },
                    "required": False
                },
                "imageBundle": {
                    "$id": "#/items/anyOf/0/properties/imageBundle",
                    "type": "string",
                    "required": False,
                    "title": "The name of the image bundle",
                    "description": "The name of the image bundle to be associated with the container.",
                    "default": "",
                    "examples": [
                        {"imageBundle": "spine_image_bundle"}
                    ],
                    "items": {
                        "$id": "#/items/anyOf/0/properties/imageBundle/items"
                    }
                }
            }
        }
    }
}

SCHEMA_CV_TAG = {
    "$schema": "https://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "title": "Root Schema",
    "type": "array",
    "default": [],
    "items": {
        "title": "A Schema",
        "type": "object",
        "default": {},
        "required": [],
        "properties": {
            "device": {
                "title": "The device Schema",
                "type": "string",
                "default": "",
                "examples": [
                    "leaf1"
                ]
            },
            "device_id": {
                "title": "The device Schema",
                "type": "string",
                "default": "",
                "examples": [
                    "JPE19181517"
                ]
            },
            "device_tags": {
                "title": "The device_tags Schema",
                "type": "array",
                "default": [],
                "items": {
                    "title": "A Schema",
                    "type": "object",
                    "required": [
                        "name",
                        "value"
                    ],
                    "properties": {
                        "name": {
                            "title": "The name Schema",
                            "type": "string",
                            "examples": [
                                "tag1",
                                "tag2"
                            ]
                        },
                        "value": {
                            "title": "The value Schema",
                            "type": ["integer", "string"],
                            "examples": [
                                "value1",
                                "value2"
                            ]
                        }
                    },
                    "examples": [
                        {
                            "name": "tag1",
                            "value": "value1"
                        },
                        {
                            "name": "tag2",
                            "value": "value2"
                        }]
                },
                "examples": [
                    [
                        {
                            "name": "tag1",
                            "value": "value1"
                        },
                        {
                            "name": "tag2",
                            "value": "value2"
                        }]
                ]
            },
            "interface_tags": {
                "title": "The interface_tags Schema",
                "type": "array",
                "default": [],
                "items": {
                    "title": "A Schema",
                    "type": "object",
                    "required": [
                        "tags"
                    ],
                    "properties": {
                        "interface": {
                            "title": "The interface Schema",
                            "type": "string",
                            "examples": [
                                "Ethernet1",
                                "Ethernet2"
                            ]
                        },
                        "tags": {
                            "title": "The tags Schema",
                            "type": "array",
                            "items": {
                                "title": "A Schema",
                                "type": "object",
                                "required": [
                                    "name",
                                    "value"
                                ],
                                "properties": {
                                    "name": {
                                        "title": "The name Schema",
                                        "type": "string",
                                        "examples": [
                                            "tag1",
                                            "tag2"
                                        ]
                                    },
                                    "value": {
                                        "title": "The value Schema",
                                        "type": ["integer", "string"],
                                        "examples": [
                                            "value1",
                                            "value2"
                                        ]
                                    }
                                },
                                "examples": [
                                    {
                                        "name": "tag1",
                                        "value": "value1"
                                    },
                                    {
                                        "name": "tag2",
                                        "value": "value2"
                                    },
                                    {
                                        "name": "tag1",
                                        "value": "value1"
                                    },
                                    {
                                        "name": "tag2",
                                        "value": "value2"
                                    }]
                            },
                            "examples": [
                                [
                                    {
                                        "name": "tag1",
                                        "value": "value1"
                                    },
                                    {
                                        "name": "tag2",
                                        "value": "value2"
                                    }],
                                [
                                    {
                                        "name": "tag1",
                                        "value": "value1"
                                    },
                                    {
                                        "name": "tag2",
                                        "value": "value2"
                                    }]
                            ]
                        }
                    },
                    "examples": [
                        {
                            "interface": "Ethernet1",
                            "tags": [
                                {
                                    "name": "tag1",
                                    "value": "value1"
                                },
                                {
                                    "name": "tag2",
                                    "value": "value2"
                                }]
                        },
                        {
                            "interface": "Ethernet2",
                            "tags": [
                                {
                                    "name": "tag1",
                                    "value": "value1"
                                },
                                {
                                    "name": "tag2",
                                    "value": "value2"
                                }]
                        }]
                },
                "examples": [
                    [
                        {
                            "interface": "Ethernet1",
                            "tags": [
                                {
                                    "name": "tag1",
                                    "value": "value1"
                                },
                                {
                                    "name": "tag2",
                                    "value": "value2"
                                }]
                        },
                        {
                            "interface": "Ethernet2",
                            "tags": [
                                {
                                    "name": "tag1",
                                    "value": "value1"
                                },
                                {
                                    "name": "tag2",
                                    "value": "value2"
                                }]
                        }]
                ]
            }
        },
        "examples": [{
            "device": "leaf1",
            "device_tags": [
                {
                    "name": "tag1",
                    "value": "value1"
                },
                {
                    "name": "tag2",
                    "value": "value2"
                }],
            "interface_tags": [
                {
                    "interface": "Ethernet1",
                    "tags": [
                        {
                            "name": "tag1",
                            "value": "value1"
                        },
                        {
                            "name": "tag2",
                            "value": "value2"
                        }
                    ]
                },
                {
                    "interface": "Ethernet2",
                    "tags": [
                        {
                            "name": "tag1",
                            "value": "value1"
                        },
                        {
                            "name": "tag2",
                            "value": "value2"
                        }
                    ]
                }
            ]
        }]
    },
    "examples": [
        [{
            "device": "leaf1",
            "device_tags": [
                {
                    "name": "tag1",
                    "value": "value1"
                },
                {
                    "name": "tag2",
                    "value": "value2"
                }
            ],
            "interface_tags": [
                {
                    "interface": "Ethernet1",
                    "tags": [
                        {
                            "name": "tag1",
                            "value": "value1"
                        },
                        {
                            "name": "tag2",
                            "value": "value2"
                        }
                    ]
                },
                {
                    "interface": "Ethernet2",
                    "tags": [
                        {
                            "name": "tag1",
                            "value": "value1"
                        },
                        {
                            "name": "tag2",
                            "value": "value2"
                        }
                    ]
                }
            ]
        }]
    ]
}

SCHEMA_CV_CHANGE_CONTROL = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/object1669851072.json",
    "title": "Root",
    "type": "object",
    "required": [
        "stages"
    ],
    "properties": {
        "name": {
            "$id": "#root/change/name",
            "title": "Name",
            "type": "string",
            "default": "",
            "examples": [
                "Ansible playbook test change"
            ],
            "pattern": "^.*$"
        },
        "notes": {
            "$id": "#root/change/notes",
            "title": "Notes",
            "type": "string",
            "default": "",
            "examples": [
                "Created via playbook"
            ],
            "pattern": "^.*$"
        },
        "activities": {
            "$id": "#root/change/activities",
            "title": "Activities",
            "type": "array",
            "default": [],
            "items": {
                "$id": "#root/change/activities/items",
                "title": "Items",
                "type": "object",
                "oneOf": [
                    {"required": ["action"]},
                    {"required": ["task_id"]}
                ],
                "properties": {
                    "action": {
                        "$id": "#root/change/activities/items/action",
                        "title": "Action",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "Switch Healthcheck"
                        ],
                        "pattern": "^.*$"
                    },
                    "name": {
                        "$id": "#root/change/activities/items/name",
                        "title": "Name",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "Switch1_healthcheck"
                        ],
                        "pattern": "^.*$"
                    },
                    "arguments": {
                        "$id": "#root/change/activities/items/arguments",
                        "title": "Arguments",
                        "type": "array",
                        "default": [],
                        "items": {
                            "$id": "#root/change/activities/items/arguments/items",
                            "title": "Items",
                            "type": "object",
                            "required": [
                                "name",
                                "value"
                            ],
                            "properties": {
                                "name": {
                                    "$id": "#root/change/activities/items/arguments/items/name",
                                    "title": "Name",
                                    "type": "string",
                                    "default": "",
                                    "examples": [
                                        "DeviceID"
                                    ],
                                    "pattern": "^.*$"
                                },
                                "value": {
                                    "$id": "#root/change/activities/items/arguments/items/value",
                                    "title": "Value",
                                    "type": "string",
                                    "default": "",
                                    "examples": [
                                        "<device serial number>"
                                    ],
                                    "pattern": "^.*$"
                                }
                            }
                        }
                    },
                    "stage": {
                        "$id": "#root/change/activities/items/stage",
                        "title": "Stage",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "Pre-Checks"
                        ],
                        "pattern": "^.*$"
                    },
                    "task_id": {
                        "$id": "#root/change/activities/items/task_id",
                        "title": "Task_id",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "20"
                        ],
                        "pattern": "^.*$"
                    },
                    "timeout": {
                        "$id": "#root/change/activities/items/timeout",
                        "title": "Timeout",
                        "type": "integer",
                        "examples": [
                            10
                        ],
                        "default": 0
                    }
                }
            }
        },
        "stages": {
            "$id": "#root/change/stages",
            "title": "Stages",
            "type": "array",
            "default": [],
            "items": {
                "$id": "#root/change/stages/items",
                "title": "Items",
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "$id": "#root/change/stages/items/name",
                        "title": "Name",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "Leaf1a_upgrade"
                        ],
                        "pattern": "^.*$"
                    },
                    "mode": {
                        "$id": "#root/change/stages/items/mode",
                        "title": "Mode",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "parallel"
                        ],
                        "pattern": "^.*$"
                    },
                    "parent": {
                        "$id": "#root/change/stages/items/parent",
                        "title": "Parent",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "Upgrades"
                        ],
                        "pattern": "^.*$"
                    }
                }
            }
        }
    }
}

SCHEMA_CV_VALIDATE = {
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "$id": "http://example.com/example.json",
    "type": "array",
    "default": [],
    "title": "Root Schema",
    "additionalProperties": False,
    "items": {
        "type": "object",
        "default": {},
        "title": "A Schema",
        "required": ["device_name"],
        "properties": {
            "device_name": {
                "type": "string",
                "default": "",
                "title": "The device_name Schema",
                "description": "The name of the device based on the search type (hostname, fqdn or serialNumber).",
                "examples": [
                    "leaf1"
                ]
            },
            "search_type": {
                "type": "string",
                "default": "hostname",
                "title": "The search_type Schema",
                "description": "Device search type. Possible choices: fqdn, hostname, serialNumber",
                "examples": [
                    "serialNumber",
                    "fqdn",
                    "hostname"
                ]
            },
            "local_configlets": {
                "type": "object",
                "default": {},
                "title": "The local_configlets Schema",
                "description": "Configlets loaded from the local machine either read from file or cleartext in the playbook",
                "required": [],
                # "patternProperties": {
                #     "^[A-Za-z0-9\\s\\._%\\+-]+$": {
                #         "type": "string"
                #     }
                # },
                "examples": [{
                    "configlet1": "{{lookup('file', 'configlet1.cfg')}}"
                }]
            },
            "cvp_configlets": {
                "type": "array",
                "default": [],
                "title": "The cvp_configlets Schema",
                "description": "List of configlets from CloudVision's database to validate against devices.",
                "items": {
                    "type": "string",
                    "default": "",
                    "title": "A Schema",
                    "examples": [
                        "configlet5"
                    ]
                },
                "examples": [
                    ["configlet5", "leaf_mlag"]
                ]
            }
        },
        "examples": [{
            "device_name": "AVD1234567",
            "search_type": "serialNumber",
            "local_configlets": {
                "configlet1": "{{lookup('file', 'configlet1.cfg')}}"
            },
            "cvp_configlets": [
                "configlet5"
            ]
        }]
    },
    "examples": [
        [{
            "device_name": "leaf1",
            "search_type": "serialNumber",
            "local_configlets": {
                "configlet1": "{{lookup('file', 'configlet1.cfg')}}"
            },
            "cvp_configlets": [
                "configlet5"
            ]
        }]
    ]
}
