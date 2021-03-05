#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=bare-except
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: cv_container
version_added: "2.9"
author: EMEA AS Team (@aristanetworks)
short_description: Manage Provisioning topology.
description:
  - CloudVision Portal Configlet configuration requires a dictionary of containers with their parent,
    to create and delete containers on CVP side.
  - Returns number of created and/or deleted containers
options:
  topology:
    description: Yaml dictionary to describe intended containers
    required: true
    type: dict
  cvp_facts:
    description: Facts from CVP collected by cv_facts module
    required: true
    type: dict
'''

EXAMPLES = r'''
- name: Create container topology on CVP
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    verbose: False
    containers:
        Fabric:
            parent_container: Tenant
        Spines:
            parent_container: Fabric
            configlets:
                - container_configlet
            images:
                - 4.22.0F
            devices:
                - veos01
  tasks:
    - name: "Build Container topology on {{inventory_hostname}}"
      cv_container:
        topology: "{{containers}}"
        state: present
      register: CVP_CONTAINERS_RESULT
'''

import logging
import traceback
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.schema as schema
from ansible_collections.arista.cvp.plugins.module_utils.container_tools import CvContainerTools, ContainerInput
try:
    from cvprac.cvp_client_errors import CvpClientError, CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


# Ansible module preparation
ansible_module: AnsibleModule

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_container_v3')
MODULE_LOGGER.info('Start cv_container_v3 module execution')


def check_import():
    """
    check_import Check all imports are resolved
    """
    if HAS_CVPRAC is False:
        ansible_module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not schema.HAS_JSONSCHEMA:
        ansible_module.fail_json(msg="JSONSCHEMA is required. Please install using pip install jsonschema")


def check_schemas():
    """
    check_schemas Validate schemas for user's input
    """
    if not schema.validate_cv_inputs(user_json=ansible_module.params['topology'], schema=schema.SCHEMA_CV_CONTAINER):
        MODULE_LOGGER.error("Invalid configlet input : %s",
                            str(ansible_module.params['configlets']))
        ansible_module.fail_json(
            msg='Container input data are not compliant with module.')


def build_topology(cv_topology: CvContainerTools, user_topology: ContainerInput, present: bool = True):
    response = dict()
    containers_created_counter = 0
    configlet_attached_counter = 0
    containers_created = list()
    configlet_attached = list()
    taskIds = list()

    # Create containers topology in Cloudvision
    if present is True:
        for user_container in user_topology.ordered_list_containers:
            MODULE_LOGGER.info('Start creation process for container %s under %s', str(
                user_container), str(user_topology.get_parent(container_name=user_container)))
            resp = cv_topology.create_container(container=user_container, parent=user_topology.get_parent(container_name=user_container))
            if resp['success'] is True:
                if resp["success"] is True:
                    containers_created_counter += 1
                    containers_created.append(user_container)
                    taskIds += resp['taskIds']

            if user_topology.has_configlets(container_name=user_container):
                resp = cv_topology.configlets_attach(
                container=user_container, configlets=user_topology.get_configlets(container_name=user_container))
                if resp['success'] is True:
                    if resp["success"] is True:
                        configlet_attached_counter = len(
                            user_topology.get_configlets(container_name=user_container))
                        configlet_attached = user_topology.get_configlets(container_name=user_container)
                        taskIds += resp['taskIds']

    # Remove containers topology from Cloudvision
    else:
        for user_container in reversed(user_topology.ordered_list_containers):
            MODULE_LOGGER.info('Start deletion process for container %s under %s', str(
                user_container), str(user_topology.get_parent(container_name=user_container)))
            resp = cv_topology.delete_container(
                container=user_container, parent=user_topology.get_parent(container_name=user_container))
            if resp['success'] is True:
                if resp["success"] is True:
                    containers_created_counter += 1
                    containers_created.append(user_container)
                    taskIds += resp['taskIds']


    # Create ansible message
    response['containers_created'] = {"containers_created": containers_created_counter,
                                      "containers_created_list": containers_created}
    response['containers_deleted'] = {"containers_deleted": containers_created_counter,
                                      "containers_deleted_list": containers_created}
    response['configlets_attached'] = {"configlet_attached": configlet_attached_counter,
                                       "configlet_attached_list": configlet_attached}
    response['taskIds'] = taskIds
    return response


# ------------------------------------------------------------ #
#               MAIN section -- starting point                 #
# ------------------------------------------------------------ #

if __name__ == '__main__':
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        topology=dict(type='dict', required=True),                      # Topology to configure on CV side.
        state=dict(type='str',
                   required=False,
                   default='present',
                   choices=['present', 'absent'])
    )

    # Make module global to use it in all functions when required
    ansible_module = AnsibleModule(argument_spec=argument_spec,
                                   supports_check_mode=True)
    # Instantiate ansible results
    result = dict(changed=False, data={}, failed=False)
    result['data']['taskIds'] = list()
    result['data']['tasks'] = list()
    result['data']['changed'] = False

    # Test all libs are correctly installed
    check_import()

    # Test user input against schema definition
    check_schemas()

    # Create CVPRAC client
    cv_client = tools_cv.cv_connect(ansible_module)

    # Instantiate data
    cv_topology = CvContainerTools(cv_connection=cv_client, ansible_module=ansible_module)
    user_topology = ContainerInput(user_topology=ansible_module.params['topology'])

    # Create topology
    if ansible_module.params['state'] == 'present':
        cv_response = build_topology(cv_topology=cv_topology, user_topology=user_topology)
        MODULE_LOGGER.debug('Received response from Topology builder: %s', str(cv_response))
        if cv_response['containers_created']['containers_created'] > 0 or cv_response['configlets_attached']['configlets_attached'] > 0:
            result['data']['changed'] = True
        result['data']['creation_result'] = cv_response['containers_created']
        result['data']['configlet_attach_result'] = cv_response['configlets_attached']
        result['data']['taskIds'] += cv_response['taskIds']

    elif ansible_module.params['state'] == 'absent':
        cv_response = build_topology(cv_topology=cv_topology, user_topology=user_topology, present=False)
        MODULE_LOGGER.debug(
            'Received response from Topology builder: %s', str(cv_response))
        if cv_response['containers_deleted']['containers_deleted'] > 0:
            result['data']['changed'] = True
        result['data']['containers_deleted'] = cv_response['containers_deleted']

    ansible_module.exit_json(**result)
