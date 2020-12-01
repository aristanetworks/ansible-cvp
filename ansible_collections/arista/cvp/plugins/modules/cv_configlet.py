#!/usr/bin/python
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

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r'''
---
module: cv_configlet
version_added: "2.9"
author: EMEA AS Team (@aristanetworks)
short_description: Create, Delete, or Update CloudVision Portal Configlets.
description:
  - CloudVison Portal Configlet compares the list of configlets and config in
  - configlets against cvp-facts then adds, deletes, or updates
  - them as appropriate.
  - If a configlet is in cvp_facts but not in configlets it will be deleted.
  - If a configlet is in configlets but not in cvp_facts it will be created.
  - If a configlet is in both configlets and cvp_facts it configuration will
  - be compared and updated with the version in configlets
  - if the two are different.
options:
  configlets:
    description: List of configlets to managed on CVP server.
    required: true
    type: dict
  configlets_notes:
    description: Add a note to the configlets.
    required: false
    default: 'Managed by Ansible'
    type: str
  cvp_facts:
    description: Facts extracted from CVP servers using cv_facts module
    required: true
    type: dict
  configlet_filter:
    description: Filter to apply intended mode on a set of configlet.
                 If not used, then module only uses ADD mode. configlet_filter
                 list configlets that can be modified or deleted based
                 on configlets entries.
    required: false
    default: ['none']
    type: list
  state:
    description:
        - If absent, configlets will be removed from CVP if they are not bound
        - to either a container or a device.
        - If present, configlets will be created or updated.
    required: false
    default: 'present'
    choices: ['present', 'absent']
    type: str
'''

EXAMPLES = r'''
---
- name: Test cv_configlet_v2
  hosts: cvp
  connection: local
  gather_facts: no
  vars:
    configlet_list:
      Test_Configlet: "! This is a Very First Testing Configlet\n!"
      Test_DYNAMIC_Configlet: "{{ lookup('file', 'templates/configlet_'+inventory_hostname+'.txt') }}"
  tasks:
    - name: 'Collecting facts from CVP {{inventory_hostname}}.'
      tags:
        - always
      cv_facts:
      register: cvp_facts

    - name: 'Create configlets on CVP {{inventory_hostname}}.'
      tags:
        - provision
      cv_configlet:
        cvp_facts: "{{cvp_facts.ansible_facts}}"
        configlets: "{{configlet_list}}"
        configlets_notes: "Configlet managed by Ansible"
        configlet_filter: ["New", "Test","base-chk","base-firewall"]
      register: cvp_configlet
'''

# Required by Ansible and CVP
import re
import logging
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.tools as tools
import ansible_collections.arista.cvp.plugins.module_utils.schema as schema

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_configlet')
MODULE_LOGGER.info('Start cv_configlet module execution')


def get_tasks(taskIds, module):
    taskList = list()
    tasksField = {'workOrderId': 'workOrderId', 'workOrderState': 'workOrderState',
                  'currentTaskName': 'currentTaskName', 'description': 'description',
                  'workOrderUserDefinedStatus': 'workOrderUserDefinedStatus', 'note': 'note',
                  'taskStatus': 'taskStatus', 'workOrderDetails': 'workOrderDetails'}
    tasks = module.client.api.get_tasks_by_status('Pending')
    # Reduce task data to required fields
    for task in tasks:
        taskFacts = {}
        for field in task.keys():
            if field in tasksField:
                taskFacts[tasksField[field]] = task[field]
        taskList.append(taskFacts)
    return taskList


def build_configlets_list(module):
    """
    Generate list of configlets per action type.

    Examples:
    ---------
    >>> intend_list = build_configlets_list(module=module)
    >>> print(intend_list)
    {
        'create': [
            {
                'data': {
                    'name': 'configletName',
                    ...
                },
                'config': '...'
            }
        ],
        'keep': [
            {
                'data': {
                    'name': 'configletName',
                    ...
                }
            }
        ],
        'delete': [
            {
                'data': {
                    'name': 'configletName',
                    ...
                }
            }
        ],
        'update': [
            {
                'data': {
                    'name': 'configletName',
                    ...
                },
                'config': '...',
                'diff': ''
            }
        ]
    }

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    dict
        dictionnary of list on per action type
    """
    # Structure to store list for create / update / delete actions.
    intend = dict()
    # Place to save configlets to create
    intend['create'] = list()
    # Place to save configlets to keep on Cloudvision
    intend['keep'] = list()
    # Place to save configlets to update on Cloudvision
    intend['update'] = list()
    # Place to save configlets to delete from CV
    intend['delete'] = list()

    MODULE_LOGGER.info(' * build_configlets_list - configlet filter is: %s', str(module.params['configlet_filter']))

    for configlet in module.params['cvp_facts']['configlets']:
        # Only deal with Static configlets not Configletbuilders or
        # their derived configlets
        # Include only configlets that match filter elements "all" or any user's defined names.
        if configlet['type'] == 'Static':
            if tools.match_filter(input=configlet['name'],
                                  filter=module.params['configlet_filter']):
                # Test if module should keep, update or delete configlet
                if configlet['name'] in module.params['configlets']:
                    # Scenario where configlet module is set to create.
                    if module.params['state'] == 'present':
                        ansible_configlet = module.params['configlets'][configlet['name']]
                        configlet_compare = tools.compare(
                            configlet['config'], ansible_configlet, 'CVP', 'Ansible')
                        # compare function returns a floating point number
                        if configlet_compare[0] == 1.0:
                            intend['keep'].append({'data': configlet})
                        else:
                            intend['update'].append(
                                {'data': configlet, 'config': ansible_configlet, 'diff': ''.join(configlet_compare[1])})
                    # Mark configlet to be removed as module mode is absent
                    elif module.params['state'] == 'absent':
                        intend['delete'].append({'data': configlet})
                # Configlet is not in expected topology and match filter.
                else:
                    intend['delete'].append({'data': configlet})

    # Look for new configlets, if a configlet is not CVP assume it has to be created
    for ansible_configlet in module.params['configlets']:
        found = False
        for cvp_configlet in module.params['cvp_facts']['configlets']:
            if str(ansible_configlet) == str(cvp_configlet['name']):
                found = True
        if not found and tools.match_filter(input=ansible_configlet, filter=module.params['configlet_filter']):
            intend['create'].append(
                {'data': {'name': str(ansible_configlet)},
                 'config': str(module.params['configlets'][ansible_configlet])}
            )
    return intend


def action_update(update_configlets, module):
    """
    Manage configlet Update process

    Example:
    --------
    >>> action_update(...)
    {
        'changed': True,
        'failed': False,
        'update': {
            'CONFIGLET_01': success
        },
        'diff': "",
        'taskIds': [
            ...
        ]
    }

    Parameters
    ----------
    update_configlets : list
        List of configlet to update on CV.
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    dict:
        A dict with all action results.
    """
    response_data = list()
    diff = ''
    flag_failed = False
    flag_changed = False
    taskIds = list()
    configlets_notes = str(module.params['configlets_notes'])

    for configlet in update_configlets:
        if module.check_mode:
            response_data.append({configlet['data']['name']: 'will be updated'})
            MODULE_LOGGER.info('[check mode] - Configlet %s updated on cloudvision', str(
                configlet['data']['name']))
            flag_changed = True
            diff += configlet['data']['name'] + \
                ":\n" + configlet['diff'] + "\n\n"
        else:
            try:
                update_resp = module.client.api.update_configlet(config=configlet['config'],
                                                                 key=configlet['data']['key'],
                                                                 name=configlet['data']['name'],
                                                                 wait_task_ids=True)
            except Exception as error:
                # Mark module execution with error
                flag_failed = True
                # Build error message to report in ansible output
                errorMessage = re.split(':', str(error))[-1]
                message = "Configlet %s cannot be updated - %s" % (configlet['name'], errorMessage)
                # Add logging to ansible response.
                response_data.append({configlet['name']: message})
                # Generate logging error message
                MODULE_LOGGER.error('Error updating configlet %s: %s', str(
                    configlet['data']['name']), str(error))
            else:
                MODULE_LOGGER.debug('CV response is %s', str(update_resp))
                if "errorMessage" in str(update_resp):
                    # Mark module execution with error
                    flag_failed = True
                    # Build error message to report in ansible output
                    message = "Configlet %s cannot be updated - %s" % (configlet['name'], update_resp['errorMessage'])
                    # Add logging to ansible response.
                    response_data.append({configlet['data']['name']: message})
                    # Generate logging error message
                    MODULE_LOGGER.error('Error updating configlet %s: %s', str(
                        configlet['data']['name']), str(update_resp['errorMessage']))
                else:
                    # Inform module a changed has been done
                    flag_changed = True
                    # Add note to configlet to mark as managed by Ansible
                    module.client.api.add_note_to_configlet(
                        configlet['data']['key'], configlets_notes)
                    # Save result for further traces.
                    response_data.append({configlet['data']['name']: "success"})
                    # Save configlet diff
                    diff += configlet['data']['name'] + ":\n" + configlet['diff'] + "\n\n"
                    # Collect generated tasks
                    if 'taskIds' in update_resp and len(update_resp['taskIds']) > 0:
                        taskIds.append(update_resp['taskIds'])
                    MODULE_LOGGER.info('Configlet %s updated on cloudvision', str(
                        configlet['data']['name']))
    return {'changed': flag_changed,
            'failed': flag_failed,
            'update': response_data,
            'diff': diff,
            'taskIds': taskIds}


def action_delete(delete_configlets, module):
    """
    Manage configlet Deletion process

    Example:
    --------
    >>> action_delete(...)
    {
        'changed': True,
        'failed': False,
        'delete': {
            'CONFIGLET_01': success
        },
        'taskIds': []
    }

    Parameters
    ----------
    delete_configlets : list
        List of configlet to delete from CV.
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    dict:
        A dict with all action results.
    """
    response_data = list()
    flag_failed = False
    flag_changed = False

    for configlet in delete_configlets:
        if module.check_mode:
            response_data.append({configlet['data']['name']: 'will be deleted'})
            MODULE_LOGGER.info('[check mode] - Configlet %s deleted from cloudvision', str(
                configlet['data']['name']))
            flag_changed = True
        else:
            try:
                delete_resp = module.client.api.delete_configlet(
                    name=configlet['data']['name'],
                    key=configlet['data']['key'])
            except Exception as error:
                # Mark module execution with error
                flag_failed = True
                # Build error message to report in ansible output
                errorMessage = re.split(':', str(error))[-1]
                message = "Configlet %s cannot be deleted - %s" % (
                    configlet['data']['name'], errorMessage)
                # Add logging to ansible response.
                response_data.append({configlet['data']['name']: message})
                # Generate logging error message
                MODULE_LOGGER.error('Error deleting configlet %s: %s', str(
                    configlet['data']['name']), str(error))
            else:
                if "error" in str(delete_resp).lower():
                    # Mark module execution with error
                    flag_failed = True
                    # Build error message to report in ansible output
                    message = "Configlet %s cannot be deleted - %s" % (
                        configlet['data']['name'], delete_resp['errorMessage'])
                    # Add logging to ansible response.
                    response_data.append({configlet['data']['name']: message})
                    # Generate logging error message
                    MODULE_LOGGER.error('Error deleting configlet %s: %s', str(
                        configlet['data']['name']), delete_resp['errorMessage'])
                else:
                    # Inform module a changed has been done
                    flag_changed = True
                    response_data.append({configlet['data']['name']: "success"})
                    MODULE_LOGGER.info('Configlet %s deleted from cloudvision', str(
                        configlet['data']['name']))
    return {'changed': flag_changed,
            'failed': flag_failed,
            'delete': response_data,
            'taskIds': []}


def action_create(create_configlets, module):
    """
    Manage configlet Update process

    Example:
    --------
    >>> action_update(...)
    {
        'changed': True,
        'failed': False,
        'create': {
            'CONFIGLET_01': success
        },
        'taskIds': []
    }

    Parameters
    ----------
    create_configlets : list
        List of configlet to create on CV.
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    dict:
        A dict with all action results.
    """
    response_data = list()
    flag_failed = False
    flag_changed = False
    configlets_notes = str(module.params['configlets_notes'])

    for configlet in create_configlets:
        # Run section to guess changes when module runs with --check flag
        if module.check_mode:
            response_data.append({configlet['data']['name']: "will be created"})
            MODULE_LOGGER.info('[check mode] - Configlet %s created on cloudvision', str(
                configlet['data']['name']))
            flag_changed = True
        else:
            try:
                new_resp = module.client.api.add_configlet(
                    name=configlet['data']['name'],
                    config=configlet['config'])
            except Exception as error:
                # Mark module execution with error
                flag_failed = True
                # Build error message to report in ansible output
                errorMessage = re.split(':', str(error))[-1]
                message = "Configlet %s cannot be created - %s" % (configlet['data']['name'], errorMessage)
                # Add logging to ansible response.
                response_data.append({configlet['data']['name']: message})
                # Generate logging error message
                MODULE_LOGGER.error('Error creating configlet %s: %s', str(configlet['data']['name']), str(error))
            else:
                if "errorMessage" in str(new_resp):
                    # Mark module execution with error
                    flag_failed = True
                    # Build error message to report in ansible output
                    message = "Configlet %s cannot be created - %s" % (
                        configlet['data']['name'], new_resp['errorMessage'])
                    # Add logging to ansible response.
                    response_data.append({configlet['data']['name']: message})
                    # Generate logging error message
                    MODULE_LOGGER.error(
                        'Error creating configlet %s: %s', str(configlet['data']['name']), str(new_resp))
                else:
                    module.client.api.add_note_to_configlet(
                        new_resp, configlets_notes)
                    flag_changed = True  # noqa # pylint: disable=unused-variable
                    response_data.append({configlet['data']['name']: "success"})
                    MODULE_LOGGER.info('Configlet %s created on cloudvision', str(configlet['data']['name']))
    return {'changed': flag_changed,
            'failed': flag_failed,
            'create': response_data,
            'taskIds': []}


def update_response(cv_response, ansible_response, module, type='create'):
    """
    Extract information to build ansible response.

    Parameters
    ----------
    cv_response : dict
        Response from Cloudvision got from action_* functions.
    ansible_response : dict
        Structure to print out ansible information.
    module : AnsibleModule
        Ansible module.`
    type : str, optional
        Type of action to manage. Must be either create / update / delete, by default 'create'

    Returns
    -------
    dict
        Updated structure to print out ansible information.
    """
    # Forge list of configlets managed
    if type == 'create':
        ansible_response['data']['new'] = cv_response[type]
    elif type == 'update':
        ansible_response['data']['updated'] = cv_response[type]
    elif type == 'delete':
        ansible_response['data']['deleted'] = cv_response[type]

    # Forge additional outputs
    # Get optional list of tasks
    if 'taskIds' in cv_response and len(cv_response['taskIds']) > 0:
        ansible_response['data']['tasks'] = ansible_response['data']['tasks'] + \
            get_tasks(taskIds=cv_response['taskIds'], module=module)

    # Extract DIFF results
    if 'diff' in cv_response and cv_response['diff']:
        ansible_response['diff'] = ansible_response['diff'] + cv_response['diff']
    # Update changed flag if required
    if cv_response['changed']:
        ansible_response['changed'] = cv_response['changed']
    # Update failed status if required
    if cv_response['failed']:
        ansible_response['failed'] = True

    # Provide complete response
    return ansible_response


def action_manager(module):
    """
    Function to manage all tasks execution.

    Examples:
    ---------
    >>> action_manager(module=module)
    {
        "changed": false,
        "data": {
            "new": [
                {
                    "CONFIGLET_01": "success"
                }
            ],
            "updated": [
                {
                    "CONFIGLET_02": "success"
                }
            ],
            "deleted": [
                {
                    "CONFIGLET_03": "success"
                }
            ],
            "tasks": [
                {
                    ...
                }
            ]
        },
        "diff": "",
        "failed": false
    }

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    dict:
        Dictionary as module result.
    """
    # Collect lists to execute actions.
    intend_list = build_configlets_list(module=module)
    # Create initial output structure.
    action_results = {'changed': False, 'failed': False, 'data': {'new': list(),
                      'updated': list(), 'deleted': list(), 'tasks': list()},
                      'diff': ''}
    # Default flag for changed set to False
    flag_changed = False  # noqa # pylint: disable=unused-variable
    # Default flag for failed set to False
    flag_failed = False  # noqa # pylint: disable=unused-variable

    # MODULE_LOGGER.debug('Current intended list is: %s', str(intend_list))

    # Create new configlets and only if state is not absent
    if len(intend_list['create']) > 0 and module.params['state'] != "absent":
        MODULE_LOGGER.info('Start configlets creation process')
        temp_res = action_create(
            create_configlets=intend_list['create'],
            module=module)
        action_results = update_response(
            cv_response=temp_res,
            ansible_response=action_results,
            type='create',
            module=module)

    # Update existing configlets and only if state is not absent
    if len(intend_list['update']) > 0 and module.params['state'] != "absent":
        MODULE_LOGGER.info('Start configlets update process')
        temp_res = action_update(
            update_configlets=intend_list['update'],
            module=module)
        action_results = update_response(
            cv_response=temp_res,
            ansible_response=action_results,
            type='update',
            module=module)

    # Delete configlets.
    if len(intend_list['delete']) > 0:
        MODULE_LOGGER.info('Start configlets deletion process')
        temp_res = action_delete(
            delete_configlets=intend_list['delete'],
            module=module)
        action_results = update_response(
            cv_response=temp_res,
            ansible_response=action_results,
            type='delete',
            module=module)

    return action_results


def main():
    """
    main entry point for module execution.
    """
    argument_spec = dict(
        configlets=dict(type='dict', required=True),
        configlets_notes=dict(type='str', default='Managed by Ansible', required=False),
        cvp_facts=dict(type='dict', required=True),
        configlet_filter=dict(type='list', default='none'),
        state=dict(type='str',
                   choices=['present', 'absent'],
                   default='present',
                   required=False))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    MODULE_LOGGER.info('starting module cv_configlet')
    if module.check_mode:
        MODULE_LOGGER.warning('! check_mode is enable')
        # module.exit_json(changed=True)

    if not tools.HAS_DIFFLIB:
        module.fail_json(msg='difflib required for this module')

    if not tools_cv.HAS_CVPRAC:
        module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not schema.HAS_JSONSCHEMA:
        module.fail_json(
            msg="jsonschema is required. Please install using pip install jsonschema")

    if not schema.validate_cv_inputs(user_json=module.params['configlets'], schema=schema.SCHEMA_CV_CONFIGLET):
        MODULE_LOGGER.error("Invalid configlet input : %s", str(module.params['configlets']))
        module.fail_json(
            msg='Configlet input data are not compliant with module.')

    result = dict(changed=False, data={})
    # messages = dict(issues=False)
    # Connect to CVP instance
    if not module.check_mode:
        module.client = tools_cv.cv_connect(module)

    # Pass module params to configlet_action to act on configlet
    result = action_manager(module)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
