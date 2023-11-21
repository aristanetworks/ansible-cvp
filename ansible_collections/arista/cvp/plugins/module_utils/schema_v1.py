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

import logging
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


LOGGER = logging.getLogger('arista.cvp.json_schema')

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


def validate_cv_inputs(user_json, schema):
    """
    validate_cv_inputs JSON SCHEMA Validation.

    Run a JSON validation against a muser's defined JSONSCHEMA.

    Parameters
    ----------
    user_json : json
        JSON to validate
    schema : JSON
        JSON Schema to use to validate JSON

    Returns
    -------
    boolean
        True if valid, False if not.
    """
    try:
        jsonschema.validate(instance=user_json, schema=schema)
    except jsonschema.ValidationError as error_message:
        LOGGER.error("Invalid inputs %s", str(error_message))
        return False
    return True
