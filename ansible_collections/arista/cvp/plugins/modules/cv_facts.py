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
import logging
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection, ConnectionError
from ansible_collections.arista.cvp.plugins.module_utils.cv_client import CvpClient
from ansible_collections.arista.cvp.plugins.module_utils.cv_client_errors import CvpLoginError, CvpApiError


DOCUMENTATION = r'''
---
module: cv_facts
version_added: "2.9"
author: EMEA AS Team (@aristanetworks)
short_description: Collect facts from CloudVision Portal.
description:
  - Returns list of devices, configlets, containers and images
options:
  gather_subset:
    description:
      - When supplied, this argument will restrict the facts collected
      - to a given subset.  Possible values for this argument include
      - all, hardware, config, and interfaces.  Can specify a list of
      - values to include a larger subset.  Values can also be used
      - with an initial C(M(!)) to specify that a specific subset should
      - not be collected.
    required: false
    default: ['default']
    type: list
    choices:
      - default
      - config
      - tasks_pending
      - tasks_failed
      - tasks_all
  facts:
    description:
      - List of facts to retrieve from CVP.
      - By default, cv_facts returns facts for devices/configlets/containers/tasks
      - Using this parameter allows user to limit scope to a subet of information.
    required: false
    default: ['all']
    type: list
    choices:
      - all
      - devices
      - containers
      - configlets
      - tasks
'''

EXAMPLES = r'''
---
  tasks:
    - name: '#01 - Collect devices facts from {{inventory_hostname}}'
      cv_facts:
        facts:
          devices
      register: FACTS_DEVICES

    - name: '#02 - Collect devices facts (with config) from {{inventory_hostname}}'
      cv_facts:
        gather_subset:
          config
        facts:
          devices
      register: FACTS_DEVICES_CONFIG

    - name: '#03 - Collect confilgets facts from {{inventory_hostname}}'
      cv_facts:
        facts:
          configlets
      register: FACTS_CONFIGLETS

    - name: '#04 - Collect containers facts from {{inventory_hostname}}'
      cv_facts:
        facts:
          containers
      register: FACTS_CONTAINERS

    - name: '#10 - Collect ALL facts from {{inventory_hostname}}'
      cv_facts:
      register: FACTS
'''


def connect(module, debug=False):
    ''' Connects to CVP device using user provided credentials from playbook.
    :param module: Ansible module with parameters and client connection.
    :return: CvpClient object with connection instantiated.
    '''
    client = CvpClient()
    connection = Connection(module._socket_path)
    host = connection.get_option("host")
    port = connection.get_option("port")
    user = connection.get_option("remote_user")
    pswd = connection.get_option("password")
    if debug:
        logging.debug('*** Connecting to CVP')
    try:
        client.connect([host],
                       user,
                       pswd,
                       protocol="https",
                       port=port,
                       )
    except CvpLoginError as e:
        module.fail_json(msg=str(e))

    if debug:
        logging.debug('*** Connected to CVP')

    return client


def facts_devices(module, facts, debug=False):
    """
    Collect facts of all devices.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module with parameters and instances
    facts : dict
        Fact dictionary where devices information will be inserted.
    debug : bool, optional
        Activate debug logging, by default False

    Returns
    -------
    dict
        facts with devices content added.
    """

    facts['devices'] = []
    # Get Inventory Data for All Devices
    inventory = module.client.api.get_inventory()
    for device in inventory:
        if debug:
            logging.debug('  -> Working on %s', device['hostname'])
        device['name'] = device['hostname']
        # Add designed config for device
        if 'config' in module.params['gather_subset'] and device['streamingStatus'] == "active":
            device['config'] = module.client.api.get_device_configuration(device['key'])

        # Add parent container name
        container = module.client.api.get_container_by_id(device['parentContainerKey'])
        device['parentContainerName'] = container['name']

        # Add Device Specific Configlets
        configlets = module.client.api.get_configlets_by_device_id(device['key'])
        device['deviceSpecificConfiglets'] = []
        for configlet in configlets:
            if int(configlet['containerCount']) == 0:
                device['deviceSpecificConfiglets'].append(configlet['name'])

        # Add ImageBundle Info
        device['imageBundle'] = ""
        deviceInfo = module.client.api.get_net_element_info_by_device_id(device['key'])
        if "imageBundleMapper" in deviceInfo:
            # There should only be one ImageBudle but its id is not decernable
            # If the Image is applied directly to the device its type will be 'netelement'
            if len(list(deviceInfo['imageBundleMapper'].values())) > 0:
                if list(deviceInfo['imageBundleMapper'].values())[0]['type'] == 'netelement':
                    device['imageBundle'] = deviceInfo['bundleName']

        # Add device to facts list
        facts['devices'].append(device)

    return facts


def facts_configlets(module, facts, debug=False):
    """
    Collect facts of all configlets.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module with parameters and instances
    facts : dict
        Fact dictionary where configlets information will be inserted.
    debug : bool, optional
        Activate debug logging, by default False

    Returns
    -------
    dict
        facts with configlets content added.
    """

    facts['configlets'] = []
    configlets = module.client.api.get_configlets()['data']
    # Reduce configlet data to required fields
    for configlet in configlets:
        if debug:
            logging.debug('  -> Working on %s', configlet['name'])
        # Get list of devices attached to configlet.
        configlet['devices'] = []
        applied_devices = module.client.api.get_devices_by_configlet(configlet['name'])
        for device in applied_devices['data']:
            configlet['devices'].append(device['hostName'])

        # Get list of containers attached to configlet.
        configlet['containers'] = []
        applied_containers = module.client.api.get_containers_by_configlet(configlet['name'])
        for container in applied_containers['data']:
            configlet['containers'].append(container['containerName'])

        # Add configlet to facts list
        facts['configlets'].append(configlet)

    return facts


def facts_containers(module, facts, debug=False):
    """
    Collect facts of all containers.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module with parameters and instances
    facts : dict
        Fact dictionary where containers information will be inserted.
    debug : bool, optional
        Activate debug logging, by default False

    Returns
    -------
    dict
        facts with containers content added.
    """

    facts['containers'] = []

    # Get List of all Containers
    containers = module.client.api.get_containers()['data']
    for container in containers:
        if debug:
            logging.debug('  -> Working on %s', container['name'])
        container['devices'] = []
        # Get list of devices attached to container.
        applied_devices = module.client.api.get_devices_by_container_id(container['key'])
        for device in applied_devices:
            container['devices'].append(device['fqdn'])

        # Get list of configlets attached to container.
        container['configlets'] = []
        applied_configlets = module.client.api.get_configlets_by_container_id(container['key'])['configletList']
        for configlet in applied_configlets:
            container['configlets'].append(configlet['name'])

        # Add applied Images
        container['imageBundle'] = ""
        applied_images = module.client.api.get_image_bundle_by_container_id(container['key'])['imageBundleList']
        if len(applied_images) > 0:
            container['imageBundle'] = applied_images[0]['name']

        # Add container to facts list
        facts['containers'].append(container)

    return facts


def facts_tasks(module, facts, debug=False):
    """
    Collect facts of all tasks.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module with parameters and instances
    facts : dict
        Fact dictionary where tasks information will be inserted.
    debug : bool, optional
        Activate debug logging, by default False

    Returns
    -------
    dict
        facts with tasks content added.
    """

    facts['tasks'] = []
    tasks = []

    # Get List of Tasks
    if debug:
        logging.debug('  -> Extracting tasks with %s', str(module.params['gather_subset']))

    if 'tasks_pending' in module.params['gather_subset']:
        # We only get pending tasks
        tasks.extend(module.client.api.get_tasks_by_status(status='Pending'))

    if 'tasks_all' in module.params['gather_subset']:
        # User wants to get list of all tasks -- not default behavior
        tasks.extend(module.client.api.get_tasks()['data'])

    if 'tasks_failed' in module.params['gather_subset']:
        # User wants to get list of all tasks -- not default behavior
        tasks.extend(module.client.api.get_tasks_by_status(status='Failed'))

    if 'default' in module.params['gather_subset']:
        # By default we only extract pending tasks and not all tasks
        tasks.extend(module.client.api.get_tasks_by_status(status='Pending'))

    for task in tasks:
        if debug:
            logging.debug('  -> Working on %s', task)
        facts['tasks'].append(task)
    return facts


def facts_builder(module, debug=False):
    """
    Method to call every fact module for either devices/containers/configlets.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module with parameters and instances
    debug : bool, optional
        Activate debug logging, by default False

    Returns
    -------
    dict
        facts structure to return by Ansible
    """

    facts = {}
    # Get version data for CVP
    if debug:
        logging.debug('** Collecting CVP Information (version)')
    facts['cvp_info'] = module.client.api.get_cvp_info()

    # Extract devices facts
    if 'all' in module.params['facts'] or 'devices' in module.params['facts']:
        if debug:
            logging.debug('** Collecting devices facts ...')
        facts = facts_devices(module=module, facts=facts, debug=debug)

    # Extract configlet information
    if 'all' in module.params['facts'] or 'configlets' in module.params['facts']:
        if debug:
            logging.debug('** Collecting configlets facts ...')
        facts = facts_configlets(module=module, facts=facts, debug=debug)

    # Extract containers information
    if 'all' in module.params['facts'] or 'containers' in module.params['facts']:
        if debug:
            logging.debug('** Collecting containers facts ...')
        facts = facts_containers(module=module, facts=facts, debug=debug)

    # Extract tasks information
    if 'all' in module.params['facts'] or 'tasks' in module.params['facts']:
        if debug:
            logging.debug('** Collecting tasks facts ...')
        facts = facts_tasks(module=module, facts=facts, debug=debug)

    # Extract imageBundles information
    if 'all' in module.params['facts'] or 'images' in module.params['facts']:
        if debug:
            logging.debug('** Collecting images facts ...')
        facts['imageBundles'] = list()

    # End of Facts module
    if debug:
        logging.debug('** All facts done')
    return facts


def main():
    """
    main entry point for module execution.
    """
    debug_module = False
    if debug_module:
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename='cv_fact_v2.log', level=logging.DEBUG)

    argument_spec = dict(
        gather_subset=dict(type='list',
                           elements='str',
                           required=False,
                           choices=['default',
                                    'config',
                                    'tasks_pending',
                                    'tasks_all',
                                    'tasks_failed'],
                           default='default'),
        facts=dict(type='list',
                   elements='str',
                   required=False,
                   choices=['all',
                            'configlets',
                            'containers',
                            'devices',
                            'tasks'],
                   default='all'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    # Forge standard Ansible output
    result = dict(changed=False, ansible_facts={})

    # Connect to CVP Instance
    module.client = connect(module, debug=debug_module)

    # Get Facts from CVP
    result['ansible_facts'] = facts_builder(module, debug=debug_module)

    # Standard Ansible outputs
    module.exit_json(**result)


if __name__ == '__main__':
    main()
