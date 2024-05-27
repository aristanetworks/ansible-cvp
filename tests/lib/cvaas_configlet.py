#!/usr/bin/env python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable = duplicate-code
# flake8: noqa: R0801
#


from .static_content import CONFIGLET_CONTENT

"""
cvaas_configlet - Test data for system/test_cv_configlet.py
"""

"""
Configlet Test structure:
    - `name`: Name of the configlet to use for CV
    - `content`: Content of the configlet captured by ansible and pushed to CV (can deviate from CV)
    - `content_expected`: Content that should be on CV. Used for diff tests
    - `is_present_expected`: Set if configlet should be present on CV or not. Used for system tests.

List of specific tests:
    - `is_present_expected` is True:
        - test_configlet_data_from_cv
        - test_update_configlet
    - `is_present_expected` is False:
        - test_create_configlet
        - test_delete_configlet
"""

SYSTEM_CONFIGLETS_TESTS = [
    {
        'name': 'system-configlet-tests01',
        'config': CONFIGLET_CONTENT,
        'config_expected': CONFIGLET_CONTENT,
        'is_present_expected': True,
        'is_valid_expected': True
    },
    {
        'name': 'system-configlet-tests02',
        'config': 'alias sib show ip interfaces',
        'config_expected': 'alias sib show ip interfaces brief',
        'is_present_expected': True,
        'is_valid_expected': True
    },
    {
        'name': 'system-configlet-tests03',
        'config': 'alias sib2 show ip interfaces brief',
        'config_expected': 'alias sib2 show ip interfaces brief',
        'is_present_expected': False,
        'is_valid_expected': True
    },
    {
        'name': 'system-configlet-tests04',
        'config': CONFIGLET_CONTENT,
        'config_expected': CONFIGLET_CONTENT,
        'is_present_expected': False,
        'is_valid_expected': True
    },
]
