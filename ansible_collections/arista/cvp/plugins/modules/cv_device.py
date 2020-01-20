#!/usr/bin/python
# coding: utf-8 -*-
#
# FIXME: required to pass ansible-test
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

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

import re
import logging
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection, ConnectionError
from ansible_collections.arista.cvp.plugins.module_utils.cv_client import CvpClient
from ansible_collections.arista.cvp.plugins.module_utils.cv_client_errors import CvpLoginError, CvpApiError
from time import sleep

# Activate or not debug mode for logging & development
DEBUG_MODULE = True

DOCUMENTATION = r'''
---
module: cv_device
version_added: "2.9"
author: EMEA AS Team (@aristanetworks)
short_description: Provision, Reset, or Update CloudVision Portal Devices.
description:
  - CloudVison Portal Device compares the list of Devices in
  - in devices against cvp-facts then adds, resets, or updates them as appropriate.
  - If a device is in cvp_facts but not in devices it will be reset to factory defaults
  - If a device is in devices but not in cvp_facts it will be provisioned
  - If a device is in both devices and cvp_facts its configlets and imageBundles will be compared
  - and updated with the version in devices if the two are different.
options:
  devices:
    description: Yaml dictionary to describe intended devices
                 configuration from CVP stand point.
    required: true
    type: dict
  cvp_facts:
    description: Facts from CVP collected by cv_facts module
    required: true
    type: dict
  device_filter:
    description: Filter to apply intended mode on a set of configlet.
                 If not used, then module only uses ADD mode. device_filter
                 list devices that can be modified or deleted based
                 on configlets entries.
    required: false
    default: ['none']
    type: list
  state:
    description:
        - If absent, devices will be removed from CVP and moved back to undefined.
        - If present, devices will be configured or updated.
    required: false
    default: 'present'
    choices: ['present', 'absent']
    type: str
'''

EXAMPLES = r'''
---
- name: Test cv_device
  hosts: cvp
  connection: local
  gather_facts: no
  collections:
    - arista.cvp
  vars:
    configlet_list:
      cv_device_test01: "alias a{{ 999 | random }} show version"
      cv_device_test02: "alias a{{ 999 | random }} show version"
    # Device inventory for provision activity: bind configlet
    devices_inventory:
      veos01:
        name: veos01
        configlets:
          - cv_device_test01
          - SYS_TelemetryBuilderV2_172.23.0.2_1
          - veos01-basic-configuration
          - SYS_TelemetryBuilderV2
  tasks:
      # Collect CVP Facts as init process
    - name: "Gather CVP facts from {{inventory_hostname}}"
      cv_facts:
      register: cvp_facts
      tags:
        - always

    - name: "Configure devices on {{inventory_hostname}}"
      tags:
        - provision
      cv_device:
        devices: "{{devices_inventory}}"
        cvp_facts: '{{cvp_facts.ansible_facts}}'
        device_filter: ['veos']
      register: cvp_device
'''

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_device')
MODULE_LOGGER.info('Start cv_device module execution')


def connect(module):
    """
    Connects to CVP device using user provided credentials from playbook.
    
    Parameters
    ----------
    module : AnsibleModule
        Ansible module.
    
    Returns
    -------
    CvpClient
        CvpClient object with connection instantiated.
    """
    client = CvpClient()
    connection = Connection(module._socket_path)
    host = connection.get_option("host")
    port = connection.get_option("port")
    user = connection.get_option("remote_user")
    pswd = connection.get_option("password")
    try:
        client.connect([host],
                       user,
                       pswd,
                       protocol="https",
                       port=port,
                       )
    except CvpLoginError as e:
        module.fail_json(msg=str(e))
    return client


### GET functions ###


def device_get_from_facts(module, device_name):
    """
    Get device information from CVP facts.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.
    device_name : string
        Hostname to search in facts.

    Returns
    -------
    dict
        Device facts if found, else None.
    """
    for device in module.params['cvp_facts']['devices']:
        if device['hostname'] == device_name:
            return device
    return None


def facts_devices(module):
    """
    Extract Facts of all devices from cv_facts.
    
    Parameters
    ----------
    module : AnsibleModule
        Ansible module.
    
    Returns
    -------
    dict:
        Facts of all devices
    """
    if 'cvp_facts' in module.params:
        if 'devices' in module.params['cvp_facts']:
            return module.params['cvp_facts']['devices']
    return []


def configlets_get_from_facts(cvp_device):
    """
    Return list of devices's attached configlets from CV Facts.

    Parameters
    ----------
    cvp_device : dict
        Device facts from CV.

    Returns
    -------
    list
        List of existing device's configlets.
    """
    if 'deviceSpecificConfiglets' in cvp_device:
        return cvp_device['deviceSpecificConfiglets']
    return []


def configlet_get_fact_key(configlet_name, cvp_facts):
    for configlet in cvp_facts['configlets']:
        if configlet_name == configlet['name']:
            return configlet['key']
    return None

def tasks_get_fitlered(taskid_list, module):
    """
    Get tasks information from a list of tasks.

    Parameters
    ----------
    taskid_list : list
        List of task IDs to get.
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    list
        List of tasks from CVP.
    """
    tasks = module.client.api.get_tasks_by_status('Pending')
    task_list = list()
    for task in tasks:
        if task['workOrderId'] in taskid_list:
            task_list.append(task)
    return task_list


def get_unique_from_list(source_list, compare_list):
    """
    Extract unique entries from list.

    Compare source_list to compare_list and return entries from source_list
    and not in compare_list.

    Parameters
    ----------
    source_list : list
        Input list to compare to base list
    compare_list : list
        Base list to compare input list to.

    Returns
    -------
    list
        List of unique entries
    """
    unique_entries = list()
    for entry in source_list:
        if entry not in compare_list:
            unique_entries.append(entry)
    return unique_entries


### Test Functions ###


def is_in_filter(hostname_filter=['all'], hostname='eos'):
    """
    Check if device is part of the filter or not.

    Parameters
    ----------
    hostname_filter : list, optional
        Device filter, by default ['all']
    hostname : str
        Device hostname to compare against filter.

    Returns
    -------
    boolean
        True if device hostname is part of filter. False if not.
    """
    if DEBUG_MODULE:
        logging.info(' * is_in_filter - filter is %s', str(hostname_filter))
        logging.info(' * is_in_filter - hostname is %s', str(hostname))

    if 'all' in hostname_filter:
        return True
    elif any(element in hostname for element in hostname_filter):
        return True
    if DEBUG_MODULE:
        logging.info(' * is_in_filter - NOT matched')
    return False


def is_in_container(device, container='undefined_container'):
    """
    Check if device is attached to given container.

    Parameters
    ----------
    device : dict
        Device information from cv_facts
    container : str, optional
        Container name to check if device is attached to, by default 'undefined_container'
    
    Returns
    -------
    boolean
        True if attached to container, False if not.
    """
    if 'parentContainerKey' in device:
        if container == device['parentContainerKey']:
            return True
    return False


def is_device_target(hostname, device_list):
    """
    Check if CV Device is part of devices listed in module inputs.

    Parameters
    ----------
    hostname : string
        CV Device hostname
    device_list : dict
        Device list provided as module input.

    Returns
    -------
    boolean
        True if hostname is in device_list. False if not.
    """
    if hostname in device_list.keys():
        return True
    return False


def is_list_diff(list1, list2):
    """
    Check if 2 list have some differences.

    Parameters
    ----------
    list1 : list
        First list to compare.
    list2 : list
        Second list to compare.

    Returns
    -------
    boolean
        True if lists have diffs. False if not.
    """
    has_diff = False
    for entry1 in list1:
        if entry1 not in list2:
            has_diff = True
    for entry2 in list2:
        if entry2 not in list1:
            has_diff = True
    return has_diff


### Module dedicated functions ###


def build_existing_devices_list(module):
    """
    Build List of existing devices to update.

    Structure output:
    >>> configlets_get_from_facts(cvp_device)
    {
        [
            {
                "name": "veos01",
                "configlets": [
                    "cv_device_test01",
                    "SYS_TelemetryBuilderV2_172.23.0.2_1",
                    "veos01-basic-configuration",
                    "SYS_TelemetryBuilderV2"
                ],
                "cv_configlets": [
                    "cv_device_test01",
                    "SYS_TelemetryBuilderV2_172.23.0.2_1"
                ],
                "parentContainerName": "DC1_VEOS",
                "imageBundle": []
            }
        ]
    }

    Parameters
    ----------
    module : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    # Get variable from module
    devices_filter = module.params['device_filter']
    devices_ansible = module.params['devices']
    devices_info = list()
    facts_device = facts_devices(module)
    if DEBUG_MODULE:
            logging.debug(' * build_existing_devices_list - device filter is: %s', str(devices_filter))
    for cvp_device in facts_device:
        if DEBUG_MODULE:
            logging.debug(' * build_existing_devices_list - start %s', str(cvp_device['hostname']))
        if is_in_filter(hostname_filter=devices_filter,
                        hostname=cvp_device['hostname']):
            if DEBUG_MODULE:
                logging.debug(' * build_existing_devices_list - device is in filter')
            
            # Check if device is in module input
            if is_device_target(hostname=cvp_device['hostname'],
                                device_list=devices_ansible):
                if DEBUG_MODULE:
                    logging.debug(' * build_existing_devices_list - device is in target')
                # Target device not in 'undefined' container
                if is_in_container(device=cvp_device,
                                   container='undefined_container') is not True:
                    if DEBUG_MODULE:
                        logging.debug(' * build_existing_devices_list - device is not in undefined_container')
                    device_ansible = devices_ansible[cvp_device['hostname']]
                    # Get CV facts part of structure
                    device_ansible['cv_configlets'] = configlets_get_from_facts(cvp_device=cvp_device)
                    # imageBundle MUST be implemented later.
                    # Add device to the list
                    devices_info.append(device_ansible)
    if DEBUG_MODULE:
        logging.info(' * build_existing_devices_list - devices_info: %s', str(devices_info))
    return devices_info


def build_new_devices_list(module):
    """
    Build List of new devices to register in CV.

    Structure output:
    >>> configlets_get_from_facts(cvp_device)
    {
        [
            {
                "name": "veos01",
                "configlets": [
                    "cv_device_test01",
                    "SYS_TelemetryBuilderV2_172.23.0.2_1",
                    "veos01-basic-configuration",
                    "SYS_TelemetryBuilderV2"
                ],
                "cv_configlets": [],
                "parentContainerName": "DC1_VEOS",
                "imageBundle": []
            }
        ]
    }

    Parameters
    ----------
    module : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    # Get variable from module
    devices_filter = module.params['device_filter']
    devices_ansible = module.params['devices']
    device_info = dict()
    devices_info = list()
    facts_devices = facts_devices(module)
    # Loop in Input devices to see if it is part of CV Facts
    for ansible_device_hostname, ansible_device in devices_ansible.items():
        if is_in_filter(hostname_filter=devices_filter,
                        hostname=ansible_device_hostname):
            cvp_device = device_get_from_facts(module=module,
                                               device_name=ansible_device_hostname)
            if len(cvp_device) >= 0:
                if is_in_container(device=cvp_device,
                                   container='undefined_container'):
                    device_info = {'name': ansible_device_hostname,
                                   'parentContainerName': ansible_device['parentContainerName'],
                                   'configlets': ansible_device['configlets'],
                                   'cv_configlets': [],
                                   'imageBundle': ansible_device['imageBundle'],
                                   'message': 'Device will be provisionned'}
                # Device not in undefined container
                else:
                    message = "Device %s cannot be provisioned - Telemetry Only" % ansible_device['name']
                    device_info = {'message': message}
            # Device not in CV Facts entries
            else:
                    message = "Device %s cannot be provisioned - Not in CV facts" % ansible_device['name']
                    device_info = {'message': message}
            devices_info.append(device_info)
    return devices_info


def configlet_prepare_cvp_update(configlet_name_list, facts):
    """
    Build configlets strcuture to configure CV.

    CV requires to get a specific list of dict to add/delete configlets
    attached to device. This function create this specific structure.

    Example:
    ----------
    >>> configlet_prepare_cvp_update(configlet_name_list, facts)
    [
        {
            'name': MyConfiglet,
            'key': <<KEY Extracted from cv_facts>>
        }
    ]

    Parameters
    ----------
    configlet_name_list : list
        List of configlets name to build
    facts : dict
        Dict from cv_facts

    Returns
    -------
    list
        List of dictionary required to be passed to CV.
    """
    configlets_structure = list()
    for configlet_name in configlet_name_list:
        configlet_data = dict()
        configlet_key = configlet_get_fact_key(configlet_name=configlet_name,
                                               cvp_facts=facts)
        configlet_data['name'] = configlet_name
        configlet_data['key'] = configlet_key
        configlets_structure.append(configlet_data)
    return configlets_structure

### Device Actions ###


def devices_new(module):
    if DEBUG_MODULE:
        logging.error(' * devices_new - not yet supported')
    pass


def devices_update(module, mode='overide'):
    """
    Method to manage configlet update for device.

    Example:
    ----------
    >>> devices_update(module=module)
    {
        "taskIds": [ 108 ],
        "updated": [
            {
                "DC1-SPINE1": "Configlets-['108']"
            }
        ]
    }

    Parameters
    ----------
    module : AnsibleModule
        Ansible Module.
    mode : str, optional
        Mode to use to play with configlet, by default 'overide'

    Returns
    -------
    dict
        Dict result with tasks and information.
    """
    if DEBUG_MODULE:
        logging.debug(' * devices_update - Entering devices_update')
    devices_update = build_existing_devices_list(module=module)
    devices_updated = 0
    result_update = list()
    result_tasks_generated = list()
    newTasks = []  # Task Ids that have been identified during device actions
    taskList = []  # Tasks that have a pending status after function runs

    if DEBUG_MODULE:
        logging.debug(' * devices_update - entering update function', str(devices_update))
        logging.debug(' * devices_update - devices_update is %', str(devices_update))

    for device_update in devices_update:
        if DEBUG_MODULE:
            logging.info(' * devices_update - updating device: %s', str(device_update['name']))
        # Start configlet update
        if is_list_diff(device_update['configlets'], device_update['cv_configlets']):
            # Get list of configlet to update: in ansible inputs and not in facts
            configlets_delete = get_unique_from_list(source_list=device_update['cv_configlets'],
                                                     compare_list=device_update['configlets'])
            # Transform output to be CV compliant:
            # [{name: configlet_name, key: configlet_key_from_cv_facts}]
            configlets_delete = configlet_prepare_cvp_update(configlet_name_list=configlets_delete,
                                                             facts=module.params['cvp_facts'])

            # Get list of configlets to delete: in facts but not on ansible inputs
            configlets_add = get_unique_from_list(source_list=device_update['configlets'],
                                                  compare_list=device_update['cv_configlets'])
            # Transform output to be CV compliant:
            # [{name: configlet_name, key: configlet_key_from_cv_facts}]
            configlets_add = configlet_prepare_cvp_update(configlet_name_list=configlets_add,
                                                          facts=module.params['cvp_facts'])

            # Get device facts from cv facts
            device_facts = device_get_from_facts(module=module, device_name=device_update['name'])

            if DEBUG_MODULE:
                logging.info(' * devices_update - configlet add: %s', str(configlets_add))
                logging.info(' * devices_update - configlet delete: %s', str(configlets_delete))

            # Execute configlet update on device
            try:
                device_action = module.client.api.update_configlets_on_device(app_name='Ansible',
                                                                              device=device_facts,
                                                                              add_configlets=configlets_add,
                                                                              del_configlets=configlets_delete)
            except Exception as error:
                errorMessage = str(error)
                message = "Device %s Configlets cannot be updated - %s" % (device_update['name'], errorMessage)
                result_update.append({device_update['name']: message})
            else:
                # Capture and report error message sent by CV during update
                if "errorMessage" in str(device_action):
                    message = "Device %s Configlets cannot be Updated - %s" % (device_update['name'], device_action['errorMessage'])
                    result_update.append({device_update['name']: message})
                else:
                    changed = True
                    if 'taskIds' in str(device_action):
                        for taskId in device_action['data']['taskIds']:
                            result_tasks_generated.append(taskId)
                        result_update.append({device_update['name']: "Configlets-%s" % device_action['data']['taskIds']})
                    else:
                        result_update.append({device_update['name']: "Configlets-No_Specific_Tasks"})
    # Get CVP Information about generated tasks
    tasks_cvp = tasks_get_fitlered(taskid_list=result_tasks_generated, module=module)

    # Build response structure
    data = {'updated': result_update, 'tasksIds': result_tasks_generated}

    if DEBUG_MODULE:
        logging.info('devices_update - result output: %s', str(data))

    return data


def devices_reset(module):
    """
    Method to reset devices.

    Reset all devices listed in module.params['devices'].

    Example:
    ----------
    >>> devices_reset(module=module)
    {
        "taskIds": [ 108 ],
        "reset": [
            {
                "DC1-SPINE1": "Reset-['108']"
            }
        ]
    }

    Parameters
    ----------
    module : AnsibleModule
        Ansible Module.

    Returns
    -------
    dict
        Dict result with tasks and information.
    """
    # If any configlet changed updated 'changed' flag
    changed = False
    # Compare configlets against cvp_facts-configlets
    reset_device = []  # devices to factory reset
    reset = []
    newTasks = []  # Task Ids that have been identified during device actions
    taskList = []  # Tasks that have a pending status after function runs

    for cvp_device in module.params['cvp_facts']['devices']:
        # Include only devices that match filter elements, "all" will
        # include all devices.
        if is_in_filter(hostname_fitler=module.params['device_filter'], hostname=cvp_device['hostname']):
            try:
                device_action = module.client.api.reset_device("Ansible", cvp_device)
            except Exception as error:
                errorMessage = str(error)
                message = "Device %s cannot be reset - %s" % (cvp_device['hostname'], errorMessage)
                reset.append({cvp_device['hostname']: message})
            else:
                if "errorMessage" in str(device_action):
                    message = "Device %s cannot be Reset - %s" % (cvp_device['hostname'], device_action['errorMessage'])
                    reset.append({cvp_device['hostname']: message})
                else:
                    changed = True
                    if 'taskIds' in str(device_action):
                        for taskId in device_action['data']['taskIds']:
                            newTasks.append(taskId)
                            reset.append({cvp_device['hostname']: 'Reset-%s' % taskId})
                    else:
                        reset.append({cvp_device['hostname']: 'Reset-No_Tasks'})
    data = {'reset': reset, 'taskIds': newTasks}
    return data


def devices_action(module):
    """
    Manage all actions related to devices.

    Action ordonancer and output bui

    Structure output:
    >>> devices_action(module)
    {
    "changed": "False",
    "data": {
        "tasks": [
            {
                "workOrderId": "108",
                "name": "",
                "workOrderState": "ACTIVE"
            }
        ],
        "updated": [
            {
                "DC1-SPINE1": "Configlets-['108']"
            }
        ],
        "tasksIds": [
            "108"
        ]
    }
}

    Parameters
    ----------
    module : AnsibleModule
        Ansible Module.

    Returns
    -------
    dict
        Json structure to stdout to ansible.
    """
    # change_mode = module.params['configlet_mode']
    cvp_facts = module.params['cvp_facts']
    topology_devices = module.params['devices']
    topology_state = module.params['state']

    results = dict()
    results['changed'] = False
    results['data'] = dict()
    results['data']['tasks'] = list()

    if DEBUG_MODULE:
        logging.debug(' * devices_action - parameters: %s', str(topology_state))

    if topology_state == 'present':
        # update devices that need to be updated
        if DEBUG_MODULE:
            logging.debug(' * devices_action - Updating devices')
        result_update = devices_update(module=module)
        if DEBUG_MODULE:
            logging.debug('   - devices_action - Update results is: %s', str(result_update))
        results['data'].update(result_update)
        # Get CV info for generated tasks
        tasks_generated = tasks_get_fitlered(taskid_list=result_update['tasksIds'], module=module)
        results['data']['tasks'] = results['data']['tasks'] + tasks_generated

    # Call reset function to restart ZTP process on devices.
    elif topology_state == 'absent':
        if DEBUG_MODULE:
            logging.debug(' * devices_action - Reseting devices')
        result_reset = devices_reset(module)
        if DEBUG_MODULE:
            logging.debug('   - devices_action - Reset results is: %s', str(result_reset))
        results['changed'] = True
        results['data'].update(result_reset)
        tasks_generated = tasks_get_fitlered(taskid_list=result_update['tasksIds'], module=module)
        results['data']['tasks'].append(tasks_generated)

    if DEBUG_MODULE:
            logging.debug('   - devices_action - final result is: %s', str(results))
    return results


def main():
    """
    Module entry point.
    """
    argument_spec = dict(
        devices=dict(type='dict',
                     required=True),
        cvp_facts=dict(type='dict',
                       required=True),
        device_filter=dict(type='list',
                           default='all'),
        state=dict(type='str',
                   choices=['present', 'absent'],
                   default='present',
                   required=False))

    if DEBUG_MODULE:
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename='cv_device_v2.log', level=logging.DEBUG)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    # Connect to CVP instance
    module.client = connect(module)

    result = devices_action(module=module)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
