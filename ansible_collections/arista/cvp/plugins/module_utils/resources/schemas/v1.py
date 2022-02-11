#!/usr/bin/env python
# coding: utf-8 -*-
#
# GNU General Public License v3.0+
#
# Copyright 2022 Arista Networks AS-EMEA
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
    "type": "object",
    "$schema": "http://json-schema.org/draft-03/schema",
    "id": "#",
    "title": "CV DEVICE SCHEMA",
    "description": "The root schema to validate cv_device inputs",
    "default": {},
    "examples": [
        {
            "DC1-SPINE1": {
                "name": "DC1-SPINE1",
                "parentContainerName": "DC1_SPINES",
                "configlets": [
                    "AVD_DC1-SPINE1",
                    "01TRAINING-01"
                ],
                "imageBundle": []
            },
            "DC1-SPINE2": {
                "name": "DC1-SPINE1",
                "parentContainerName": "DC1_SPINES",
                "configlets": [
                    "AVD_DC1-SPINE2",
                    "01TRAINING-01"
                ],
                "imageBundle": []
            }
        }
    ],
    "patternProperties": {
        "^[A-Za-z0-9\\._%\\+-]+$": {
            "type": "object",
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
                    "id": "imageBundle",
                    "type": "array",
                    "contains": {
                        "type": "string"
                    },
                    "required": False
                },
            }
        }
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
                "parent_container": "Tenant"
            },
            "Leafs": {
                "parent_container": "DC2"
            },
            "Spines": {
                "parent_container": "DC2"
            },
            "POD01": {
                "parent_container": "Leafs"
            }
        }
    ],
    "required": True,
    "patternProperties": {
        "^[A-Za-z0-9\\._%\\+-]+$": {
            "type": "object",
            "required": True,
            "properties": {
                "parent_container": {
                    "id": "parent_container",
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
                "devices": {
                    "id": "devices",
                    "type": "array",
                    "contains": {
                        "type": "string"
                    },
                    "required": False
                },
            }
        }
    }
}
