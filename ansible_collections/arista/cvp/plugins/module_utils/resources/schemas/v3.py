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
                        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
                        "systemMacAddress": "50:8d:00:e3:78:aa",
                        "parentContainerName": "ANSIBLE2",
                        "configlets": [
                            "01TRAINING-01",
                            "CV-EOS-ANSIBLE01"
                        ],
                        "imageBundle": []
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
                        "type": "array",
                        "title": "The imageBundle schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": [],
                        "examples": [
                            []
                        ],
                        "items": {
                            "$id": "#/items/anyOf/0/properties/imageBundle/items"
                        }
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
                }
            }
        }
    }
}
