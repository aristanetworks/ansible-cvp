#!/usr/bin/env python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#


from ansible_collections.arista.cvp.plugins.module_utils.container_tools import ContainerInput
import pytest

CVP_DEVICES = [
    {
        "fqdn": "CV-ANSIBLE-EOS01",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE",
        "configlets": [
                "CV-EOS-ANSIBLE01"
        ],
        "imageBundle": []
    },
    {
        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE",
        "configlets": [
            "CV-EOS-ANSIBLE01"
        ],
        "imageBundle": []
    }
]

# container_tools.build_topology() unit tests parameters
# (present: bool,
#  apply_mode: str,
#  cvp_database: dict,
#  user_topology: ContainerInput,
#  expected_response: CvAnsibleResponse.content)
USER_TOPOLOGY = [
    pytest.param(
        True,
        'loose',
        {},
        ContainerInput({'Global': {'parentContainerName': 'Tenant'},
                        'Site 1': {'parentContainerName': 'Global'},
                        'Site 1 Leaves': {'parentContainerName': 'Site 1'}
                        }),
        {
            'bundle_attached': {
                'bundle_attached_count': 0,
                'bundle_attached_list': [],
                'changed': False,
                'diff': {},
                'errors': [],
                'warnings': [],
                'success': False,
                'taskIds': []},
            'bundle_detached': {
                'bundle_detached_count': 0,
                'bundle_detached_list': [],
                'changed': False,
                'diff': {},
                'errors': [],
                'warnings': [],
                'success': False,
                'taskIds': []},
            'container_added': {
                'container_added_list': ['Global', 'Site 1', 'Site 1 Leaves'],
                'warnings': [],
                'errors': [],
                'success': True,
                'changed': True,
                'taskIds': [0, 1, 2],
                'diff': {},
                'container_added_count': 3},
            'container_deleted': {
                'container_deleted_list': [],
                'warnings': [],
                'errors': [],
                'success': False,
                'changed': False,
                'taskIds': [],
                'diff': {},
                'container_deleted_count': 0},
            'configlets_attached': {
                'configlets_attached_list': [],
                'warnings': [],
                'errors': [],
                'success': False,
                'changed': False,
                'taskIds': [],
                'diff': {},
                'configlets_attached_count': 0},
            'configlets_detached': {
                'configlets_detached_list': [],
                'warnings': [],
                'errors': [],
                'success': False,
                'changed': False,
                'taskIds': [],
                'diff': {},
                'configlets_detached_count': 0},
            'success': True,
            'changed': True,
            'taskIds': [0, 1, 2]},
        id='create topology'),
    pytest.param(
        True,
        'loose',
        {
            'containers': {
                'Global': {'key': 'container_1234abcd-1234-abcd-12ab-123456abcdef',
                           'name': 'Global',
                           'parentContainerId': 'root'},
                'Site 2': {'key': 'container_1234abcd-1234-abcd-12ab-123456abcdef',
                           'name': 'Site 2',
                           'parentContainerId': 'container_1234abcd-1234-abcd-12ab-123456abcdef'},
                'Site 2 Leaves': {'key': 'container_1234abcd-1234-abcd-12ab-123456abcdef',
                                  'name': 'Site 2 Leaves',
                                  'parentContainerId': 'container_1234abcd-1234-abcd-12ab-123456abcdef'}
            }
        },
        ContainerInput({'Global': {'parentContainerName': 'Tenant'},
                        'Site 2': {'parentContainerName': 'Global'},
                        'Site 2 Leaves': {'parentContainerName': 'Site 2'}
                        }),
        {
            'bundle_attached': {
                'bundle_attached_count': 0,
                'bundle_attached_list': [],
                'changed': False,
                'diff': {},
                'errors': [],
                'warnings': [],
                'success': False,
                'taskIds': []},
            'bundle_detached': {
                'bundle_detached_count': 0,
                'bundle_detached_list': [],
                'changed': False,
                'diff': {},
                'errors': [],
                'warnings': [],
                'success': False,
                'taskIds': []},
            'container_added': {
                'container_added_list': [],
                'warnings': [],
                'errors': [],
                'success': False,
                'changed': False,
                'taskIds': [],
                'diff': {},
                'container_added_count': 0},
            'container_deleted': {
                'container_deleted_list': [],
                'warnings': [],
                'errors': [],
                'success': False,
                'changed': False,
                'taskIds': [],
                'diff': {},
                'container_deleted_count': 0},
            'configlets_attached': {
                'configlets_attached_list': [],
                'warnings': [],
                'errors': [],
                'success': False,
                'changed': False,
                'taskIds': [],
                'diff': {},
                'configlets_attached_count': 0},
            'configlets_detached': {
                'configlets_detached_list': [],
                'warnings': [],
                'errors': [],
                'success': False,
                'changed': False,
                'taskIds': [],
                'diff': {},
                'configlets_detached_count': 0},
            'success': False,
            'changed': False,
            'taskIds': []},
        id='create already present topology')
]


# container_tools.get_container_id() unit tests parameters
# (cvp_database: dict,
#  name: str,
#  expected_id: str)
TEST_CONTAINERS = [
    pytest.param({}, 'Tenant', 'root', id='root container'),
    pytest.param({'containers': {
        'unit-test-1': {'key': 'container_1234abcd-1234-abcd-12ab-123456abcdef',
                        'name': 'unit-test-1',
                        'parentContainerId': 'root'}
    }
    },
        'unit-test-1',
        'container_1234abcd-1234-abcd-12ab-123456abcdef',
        id='fake container'
    )
]
