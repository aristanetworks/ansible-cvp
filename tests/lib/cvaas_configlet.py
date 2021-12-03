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

from .cvaas_content import CONFIGLET_CONTENT

"""
cvaas_configlet - Test data for system/test_cv_configlet.py
"""


# List of specific tests:
#   - is_present_expected is True:
#       - test_configlet_data_from_cv
#       - test_update_configlet
#   - is_present_expected is False:
#       - test_create_configlet
#       - test_delete_configlet

SYSTEM_CONFIGLETS_TESTS = [
    {
        'name': 'system-configlet-tests01',
        'config': CONFIGLET_CONTENT,
        'config_expected': CONFIGLET_CONTENT,
        'is_present_expected': True
    },
    {
        'name': 'system-configlet-tests02',
        'config': 'alias sib show ip interfaces',
        'config_expected': 'alias sib show ip interfaces brief',
        'is_present_expected': True
    },
    {
        'name': 'system-configlet-tests03',
        'config': 'alias sib2 show ip interfaces brief',
        'config_expected': 'alias sib2 show ip interfaces brief',
        'is_present_expected': False,
    },
    {
        'name': 'system-configlet-tests04',
        'config': CONFIGLET_CONTENT,
        'config_expected': CONFIGLET_CONTENT,
        'is_present_expected': False,
    },
]
