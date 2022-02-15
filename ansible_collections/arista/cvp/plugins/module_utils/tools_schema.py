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
