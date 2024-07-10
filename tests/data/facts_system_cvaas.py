#!/usr/bin/env python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#
# Copyright 2022 Arista Networks
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

# from .static_content import CONFIGLET_CONTENT

"""
cvaas_facts - Test data for system/test_cv_facts.py
"""

"""
FACTS_CONTAINERS_TEST Tests structure:
    - `name`: Name of the test to use in pytest report
    - `name_expected`: Name we expect from fact module
    - `container_id`: ID of the container to use to get `name_expected` with fact module
    - `is_present_expected`: Set if container should be present on CV or not.
"""

FACTS_CONTAINERS_TEST = [
    {
        'name': 'undefined_container',
        'name_expected': 'Undefined',
        'container_id': 'undefined_container',
        'is_present_expected': True,
    },
    {
        'name': 'undefined_container2',
        'name_expected': 'Undefined',
        'container_id': 'undefined_container2',
        'is_present_expected': False,
    }
]

"""
FACT_DEVICE_TEST Tests structure:
    - `name`: Name of the test to use in pytest report
    - `name_expected`: Name we expect from fact module
    - `sysmac`: SysMac to use in testing
    - `configlet_expected`: List of configlets we expect to see from the fact module
    - `is_present_expected`: Set if device should be present on CV or not.
"""

FACT_DEVICE_TEST = [
    {
        'name': 'leaf-1-unit-test',
        'name_expected': 'leaf-1-unit-test',
        'sysmac': '50:00:00:d5:5d:c0',
        'is_present_expected': True,
        'configlet_expected': ['cvaas-unit-01', 'leaf1-unit-test', 'leaf2-unit-test', 'test_configlet', 'test_device_configlet']
    },
]

"""
FACT_FILTER_TEST Tests structure:
    - `name`: Name of the test to use in pytest report
    - `filter`: filter string to use in test. Support Reg Exp
    - `result_device_expected`: List of expected devices returned by facts
    - `result_configlet_expected`: List of expected configlets returned by facts
"""

FACT_FILTER_TEST = [
    {
        'name': 'basic string for empty',
        'filter': 'arista',
        'result_device_expected': [],
        'result_configlet_expected': []
    },
    {
        'name': 'hostname string',
        'filter': 'leaf-1-unit-test',
        'result_device_expected': ['leaf-1-unit-test'],
        'result_configlet_expected': ['leaf-1-unit-test']
    },
    {
        'name': 'simple regex',
        'filter': 'leaf.*',
        'result_device_expected': ['leaf-1-unit-test', 'leaf-2-unit-test', 'leaf-2-unit-test'],
        'result_configlet_expected': ['leaf-1-unit-test', 'leaf-2-unit-test']
    }
]
