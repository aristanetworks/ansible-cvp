#!/usr/bin/env python
# coding: utf-8 -*-
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

from ansible_collections.arista.cvp.plugins.module_utils.container_tools import ContainerInput


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
#  cvp_data: dict,
#  user_topology: ContainerInput,
#  expected_response: CvAnsibleResponse.content)
USER_TOPOLOGY = [
    (True,
     'loose',
     {},
     ContainerInput({
                    'Global': {'parentContainerName': 'Tenant'},
                    'Site 1': {'parentContainerName': 'Global'},
                    'Site 1 Leaves': {'parentContainerName': 'Site 1'}
                    }),
     {
         'container_added': {
             'container_added_list': ['Global', 'Site 1', 'Site 1 Leaves'],
             'success': True,
             'changed': True,
             'taskIds': [0, 1, 2],
             'diff': {},
             'container_added_count': 3},
         'container_deleted': {
             'container_deleted_list': [],
             'success': False,
             'changed': False,
             'taskIds': [],
             'diff': {},
             'container_deleted_count': 0},
         'configlets_attached': {
             'configlets_attached_list': [],
             'success': False,
             'changed': False,
             'taskIds': [],
             'diff': {},
             'configlets_attached_count': 0},
         'configlets_detached': {
             'configlets_detached_list': [],
             'success': True,
             'changed': False,
             'taskIds': [],
             'diff': {},
             'configlets_detached_count': 0},
         'success': True,
         'changed': True,
         'taskIds': [0, 1, 2]}),
    (True,
     'loose',
     {'containers': {
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
     ContainerInput({
                    'Global': {'parentContainerName': 'Tenant'},
                    'Site 2': {'parentContainerName': 'Global'},
                    'Site 2 Leaves': {'parentContainerName': 'Site 2'}
                    }),
     {
         'container_added': {
             'container_added_list': [],
             'success': False,
             'changed': False,
             'taskIds': [],
             'diff': {},
             'container_added_count': 0},
         'container_deleted': {
             'container_deleted_list': [],
             'success': False,
             'changed': False,
             'taskIds': [],
             'diff': {},
             'container_deleted_count': 0},
         'configlets_attached': {
             'configlets_attached_list': [],
             'success': False,
             'changed': False,
             'taskIds': [],
             'diff': {},
             'configlets_attached_count': 0},
         'configlets_detached': {
             'configlets_detached_list': [],
             'success': True,
             'changed': False,
             'taskIds': [],
             'diff': {},
             'configlets_detached_count': 0},
         'success': False,
         'changed': False,
         'taskIds': []})
]
