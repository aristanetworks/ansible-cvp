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


LOGGER = logging.getLogger(__name__)


def validate_json_schema(user_json: dict, schema):
    """
    validate_cv_inputs JSON SCHEMA Validation.

    Run a JSON validation against a muser's defined JSONSCHEMA.

    Parameters
    ----------
    user_json : dict
        JSON to validate
    schema : jsonschema
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
