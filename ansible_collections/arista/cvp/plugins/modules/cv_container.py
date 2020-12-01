#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=bare-except
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
  mode:
    description: Allow to save topology or not
    required: false
    default: merge
    choices:
      - merge
      - override
      - delete
    type: str
  configlet_filter:
    description: Filter to apply intended set of configlet on containers.
                 If not used, then module only uses ADD mode. configlet_filter
                 list configlets that can be modified or deleted based
                 on configlets entries.
    required: false
    default: ['none']
    type: list
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
    - name: "Gather CVP facts {{inventory_hostname}}"
      cv_facts:
      register: cvp_facts
    - name: "Build Container topology on {{inventory_hostname}}"
      cv_container:
        cvp_facts: "{{cvp_facts.ansible_facts}}"
        topology: "{{containers}}"
        mode: merge
      register: CVP_CONTAINERS_RESULT
'''

import sys
import logging
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.tools as tools
import ansible_collections.arista.cvp.plugins.module_utils.tools_tree as tools_tree
import ansible_collections.arista.cvp.plugins.module_utils.schema as schema
from ansible.module_utils.basic import AnsibleModule

# List of Ansible default containers
builtin_containers = tools_tree.BUILTIN_CONTAINERS

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_container')
MODULE_LOGGER.info('Start cv_container module execution')


def create_builtin_containers(facts):
    """
    Update builtin containers with root container name

    Parameters
    ----------
    facts : dict
        CloudVision facts from cv_facts
    debug : bool, optional
        Activate debug output, by default False
    """
    root = tools_tree.get_root_container(containers_fact=facts['containers'])
    builtin_containers.append(root)


def process_container(module, container, parent, action):
    """
    Execute action on CVP side to create / delete container.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    container : string
        Name of container to manage
    parent : string
        Name of parent of container to manage
    action : string
        Action to run on container. Must be one of: 'show/add/delete'
    """
    MODULE_LOGGER.debug('run process_container with %s / %s', str(container), str(action))
    containers = module.client.api.get_containers()
    # Ensure the parent exists
    parent = next((item for item in containers['data'] if
                   item['name'] == parent), None)
    if not parent and module.check_mode is False:
        module.fail_json(msg=str('Parent container (' + str(parent) + ') does not exist for container ' + str(container)))
    elif not parent and module.check_mode:
        return [True, {'taskIDs': 'unset-id-to-create-container'},
                {'container': container}]

    cont = next((item for item in containers['data'] if
                 item['name'] == container), None)
    # If module runs in dry_run, emulate CV response
    if module.check_mode is True:
        if cont and action == "delete":
            MODULE_LOGGER.debug(
                '[check mode] - run action %s on %s', str(action), str(container))
            return [True, {'taskIDs': 'unset-id-to-delete-container'},
                    {'container': cont}]
        elif action == "add":
            MODULE_LOGGER.debug(
                'check mode] - run action %s on %s', str(action), str(cont))
            return [True, {'taskIDs': 'unset-id-to-create-container'},
                    {'container': cont}]
        else:
            return [False]
    # For default processing
    if module.check_mode is False:
        if cont:
            if action == "show":
                return [False, {'container': cont}]
            elif action == "add":
                return [False, {'container': cont}]
            elif action == "delete":
                resp = module.client.api.delete_container(cont['name'],
                                                        cont['key'],
                                                        parent['name'],
                                                        parent['key'])
                if resp['data']['status'] == "success":
                    return [True, {'taskIDs': resp['data']['taskIds']},
                            {'container': cont}]
        else:
            if action == "show":
                return [False, {'container': "Not Found"}]
            elif action == "add":
                resp = module.client.api.add_container(container, parent['name'],
                                                    parent['key'])
                if resp['data']['status'] == "success":
                    return [True, {'taskIDs': resp['data']['taskIds']},
                            {'container': cont}]
            if action == "delete":
                return [False, {'container': "Not Found"}]


def create_new_containers(module, intended, facts):
    """
    Create missing container to CVP Topology.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : dict
        Facts from CVP collected by cv_facts module
    """
    count_container_creation = 0
    # Get root container of topology
    topology_root = tools_tree.get_root_container(containers_fact=facts['containers'])
    # Build ordered list of containers to create: from Tenant to leaves.
    container_intended_tree = tools_tree.tree_build_from_dict(containers=intended, root=topology_root)
    container_intended_ordered_list = tools_tree.tree_to_list(json_data=container_intended_tree, myList=list())
    # Parse ordered list of container and check if they are configured on CVP.
    # If not, then call container creation process.
    for container_name in container_intended_ordered_list:
        found = False
        # Check if container name is found in CVP Facts.
        for fact_container in facts['containers']:
            if container_name == fact_container['name']:
                found = True
                break
        # If container has not been found, we create it
        if not found:
            # module.fail_json(msg='** Create container'+container_name+' attached to '+intended[container_name]['parent_container'])
            MODULE_LOGGER.debug('sent process_container request with %s / %s', str(
                container_name), str(intended[container_name]['parent_container']))
            response = process_container(module=module,
                                         container=container_name,
                                         parent=intended[container_name]['parent_container'],
                                         action='add')
            MODULE_LOGGER.debug('sent process_container request with %s / %s and response is : %s', str(
                container_name), str(intended[container_name]['parent_container']), str(response))
            # If a container has been created, increment creation counter
            if response[0]:
                count_container_creation += 1
    # Build module message to return for creation.
    if count_container_creation > 0:
        return [True, {'containers_created': "" + str(count_container_creation) + ""}]
    return [False, {'containers_created': "0"}]


def is_empty(module, container_name, facts):
    """
    Check if container can be removed safely.

    To be removed, a container shall not have any container or
    device attached to it. Current function parses facts to see if a device or
    a container is attached. If not, we can remove container

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    container_name : str
        Name of the container to look for.
    facts : dict
        Facts from CVP collected by cv_facts module
    """
    is_empty = True
    not_empty = False
    # test if container has at least one device attached
    for device in facts['devices']:
        if device['parentContainerName'] == container_name:
            return not_empty
    return is_empty


def is_container_empty(module, container_name):
    MODULE_LOGGER.debug('get_devices_in_container %s', container_name)
    container_status = module.client.api.get_devices_in_container(container_name)
    MODULE_LOGGER.debug('* is_container_empty - get_devices_in_container %s', str(container_status))
    if container_status is not None:
        if tools.isIterable(container_status) and len(container_status) > 0:
            MODULE_LOGGER.info(
                'Found devices in container %s', str(container_name))
            return False
        MODULE_LOGGER.info(
            'No devices found in container %s', str(container_name))
        return True
    MODULE_LOGGER.debug(
        'No devices found in container %s (default behavior)', str(container_name))
    return False


def get_container_facts(container_name='Tenant', facts=None):
    """
    Get FACTS information for a container.

    Parameters
    ----------
    container_name : str, optional
        Name of the container to look for, by default 'Tenant'
    facts : dict, optional
        CVP facts information, by default None
    """
    for container in facts['containers']:
        if container['name'] == container_name:
            return container
    return None


def delete_unused_containers(module, intended, facts):
    """
    Delete containers from CVP Topology when not defined in intended.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # default_containers = ['Tenant', 'Undefined', 'root']
    count_container_deletion = 0
    container_to_delete = list()

    # Get root container for the topology
    topology_root = tools_tree.get_root_container(containers_fact=facts['containers'])

    # Build a tree of containers configured on CVP
    container_cvp_tree = tools_tree.tree_build_from_list(containers=facts['containers'], root=topology_root)
    container_cvp_ordered_list = tools_tree.tree_to_list(json_data=container_cvp_tree, myList=list())

    # Build a tree of containers expected to be configured on CVP
    container_intended_tree = tools_tree.tree_build_from_dict(containers=intended, root=topology_root)
    container_intended_ordered_list = tools_tree.tree_to_list(json_data=container_intended_tree, myList=list())

    container_to_delete = list()
    # Build a list of container configured on CVP and not on intended.
    for cvp_container in container_cvp_ordered_list:
        # Only container with no devices can be deleted.
        # If container is not empty, no reason to go further.
        if is_container_empty(module=module, container_name=cvp_container):
            # Check if a container is not present in intended topology.
            if cvp_container not in container_intended_ordered_list:
                container_to_delete.append(cvp_container)

    MODULE_LOGGER.info('List of containers to delete: %s', str(container_to_delete))

    # Read cvp_container from end. If containers are part of container_to_delete, then delete container
    for cvp_container in reversed(container_to_delete):
        # Check if container is not in intended topology and not a default container.
        if cvp_container in container_to_delete and cvp_container not in builtin_containers:
            # Get container fact for parentName
            container_fact = get_container_facts(container_name=cvp_container, facts=facts)
            # Check we have a result. Even if we should always have a match here.
            if container_fact is not None:
                MODULE_LOGGER.info('container: %s', container_fact['name'])
                response = None
                try:
                    response = process_container(module=module,
                                                 container=container_fact['name'],
                                                 parent=container_fact['parentName'],
                                                 action='delete')
                except:  # noqa E722
                    MODULE_LOGGER.error(
                        "Unexpected error: %s", str(sys.exc_info()[0]))
                    continue
                if response[0]:
                    count_container_deletion += 1
    if count_container_deletion > 0:
        return [True, {'containers_deleted': "" + str(count_container_deletion) + ""}]
    return [False, {'containers_deleted': "0"}]


def container_info(container_name, module):
    """
    Get dictionary of container info from CVP.

    Parameters
    ----------
    container_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.
    Returns
    -------
    dict: Dict of container info from CVP or exit with failure if no info for
            container is found.
    """
    container_info = module.client.api.get_container_by_name(container_name)
    if container_info is None:
        container_info = {}
        container_info['error'] = "Container with name '%s' does not exist." % container_name
    else:
        container_info['configlets'] = module.client.api.get_configlets_by_container_id(container_info['key'])
    return container_info


def device_info(device_name, module):
    """
    Get dictionary of device info from CVP.

    Parameters
    ----------
    device_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.
    Returns
    -------
    dict: Dict of device info from CVP or exit with failure if no info for
            device is found.
    """
    device_info = module.client.api.get_device_by_name(device_name)
    if not device_info:
        devices = module.client.api.get_inventory()
        for device in devices:
            if device_name in device['fqdn']:
                device_info = device
    if not device_info:
        # Debug Line ##
        # module.fail_json(msg=str('Debug - device_info: %r' %device_info))
        # Debug Line ##
        device_info['error'] = "Device with name '%s' does not exist." % device_name
    else:
        device_info['configlets'] = module.client.api.get_configlets_by_netelement_id(device_info['systemMacAddress'])['configletList']
        device_info['parentContainer'] = module.client.api.get_container_by_id(device_info['parentContainerKey'])
    return device_info


def task_info(module, taskId):
    return module.client.api.get_task_by_id(taskId)


def move_devices_to_container(module, intended, facts):
    """
    Move devices to desired containers based on topology.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # Initialize response structure
    # Result return for Ansible
    result = dict()
    # List of devices moved by this function
    moved_devices = list()  # configlets with config changes
    # Structure to save list of devices moved and number of moved
    moved = dict()
    # Number of devices moved to containers.
    moved['devices_moved'] = 0
    # List of created taskIds to pass to cv_tasks
    task_ids = list()
    # Define wether we want to save topology or not
    # Force to True as per issue115
    save_topology = True
    # Read complete intended topology to locate devices
    for container_name, container in intended.items():
        # If we have at least one device defined, then we can start process
        if 'devices' in container:
            # Extract list of device hostname
            for device in container['devices']:
                # Get CVP information for target container.
                # move_device_to_container requires to use structure sends by CVP
                container_cvpinfo = container_info(container_name=container_name,
                                                   module=module)
                # Get CVP information for device.
                # move_device_to_container requires to use structure sends by CVP
                device_cvpinfo = device_info(device_name=device, module=module)
                # Initiate a move to desired container.
                # Task is created but not executed.
                device_action = module.client.api.move_device_to_container(app_name="ansible_cv_container",
                                                                           device=device_cvpinfo,
                                                                           container=container_cvpinfo,
                                                                           create_task=save_topology)
                if device_action['data']['status'] == 'success':
                    if 'taskIds' in device_action['data']:
                        for task in device_action['data']['taskIds']:
                            task_ids.append(task)
                    moved_devices.append(device)
                    moved['devices_moved'] = moved['devices_moved'] + 1
    # Build ansible output messages.
    moved['list'] = moved_devices
    moved['taskIds'] = task_ids
    result['changed'] = True
    result['moved_devices'] = moved
    return result


def container_factinfo(container_name, facts):
    """
    Get dictionary of configlet info from CVP.

    Parameters
    ----------
    configlet_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.

    Returns
    -------
    dict: Dict of configlet info from CVP or exit with failure if no info for
            container is found.
    """
    for container in facts['containers']:
        if container['name'] == container_name:
            return container
    return None


def configlet_factinfo(configlet_name, facts):
    """
    Get dictionary of configlet info from CVP.

    Parameters
    ----------
    configlet_name : string
        Name of the container to look for on CVP side.
    module : AnsibleModule
        Ansible module to get access to cvp client.

    Returns
    -------
    dict: Dict of configlet info from CVP or exit with failure if no info for
            container is found.
    """
    for configlet in facts['configlets']:
        if configlet['name'] == configlet_name:
            return configlet
    return None


def configure_configlet_to_container(module, intended, facts):
    """
    Manage mechanism to attach and detach configlets from container.

    Addition process:
    -----------------
    - if configlet from intended match filter: configlet is attached
    - if configlet from intended does not match filter: configlet is
    ignored
    - configlet_filter = ['none'] filtering is ignored and configlet is
    attached

    Deletion process:
    -----------------
    - if configlet is not part of intended and filter is not matched: we do
    not remove it
    - if configlet is not part of intended and filter is matched: we
    detach configlet.
    - configlet_filter = ['none'], configlet is ignored and not detached

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # Initialize response structure
    #  Result return for Ansible
    result = dict()
    #  List of configlets attached by this function
    attached_configlet = list()
    #  Structure to save list of configlets attached and number of moved
    attached = dict()
    #  Number of configlets attached to containers.
    attached['configlet_attached'] = 0
    #  List of configlets detached by this function
    detached_configlet = list()
    #  Structure to save list of configlets detached and number of moved
    detached = dict()
    #  Number of configlets detached from containers.
    detached['configlet_detached'] = 0
    #  List of created taskIds to pass to cv_tasks
    task_ids = list()
    # List of configlets to attach to containers
    configlet_list_attach = list()
    # List of configlets to detach from containers.
    configlet_list_detach = list()
    # Define wether we want to save topology or not
    # Force to True as per issue115
    save_topology = True
    # Structure to save CVP result for configlet changes
    configlet_action = dict()
    # Configlet filter
    configlet_filter = module.params['configlet_filter']
    # Read complete intended topology to locate devices
    for container_name, container in intended.items():
        MODULE_LOGGER.info('work with container %s', str(container_name))
        # If we have at least one configlet defined, then we can start process
        # Get CVP information for target container.
        container_info_cvp = container_info(container_name=container_name, module=module)
        if 'configlets' in container:
            MODULE_LOGGER.debug('container has a list of containers to configure: %s', str(container['configlets']))
            # Extract list of configlet names
            for configlet in container['configlets']:
                MODULE_LOGGER.debug('running configlet %s', str(configlet))
                # We apply filter to know if we have to attach configlet.
                # If filter is set to ['none'], we consider add in any situation.
                if tools.match_filter(input=configlet, filter=configlet_filter) or ('none' in configlet_filter):
                    MODULE_LOGGER.debug('collecting information for configlet %s', str(configlet))
                    # Get CVP information for device.
                    configlet_cvpinfo = configlet_factinfo(configlet_name=configlet, facts=facts)
                    # Configlet information is saved for later deployment
                    configlet_list_attach.append(configlet_cvpinfo)
                    MODULE_LOGGER.debug('configlet_list_attach is now: %s', str(configlet_list_attach))
        # Create call to attach list of containers
        # Initiate a move to desired container.
        # Task is created but not executed.
        # Create debug output structure
        configlets_name = list()
        for configlet in configlet_list_attach:
            configlets_name.append(configlet['name'])
        # Configure new configlet to container
        if len(configlet_list_attach) > 0:
            MODULE_LOGGER.info('Apply %s to %s', str(configlets_name), str(container_info_cvp['name']))
            configlet_action = module.client.api.apply_configlets_to_container(app_name="ansible_cv_container",
                                                                               new_configlets=configlet_list_attach,
                                                                               container=container_info_cvp,
                                                                               create_task=save_topology)
            MODULE_LOGGER.debug('Get following response from cvprac for addition: %s', str(configlet_action))
            # Release list of configlet to configure (#165)
            configlet_list_attach = list()
            if 'data' in configlet_action and configlet_action['data']['status'] == 'success':
                if 'taskIds' in configlet_action['data']:
                    for task in configlet_action['data']['taskIds']:
                        task_ids.append(task)
                if len(configlet_list_attach) > 0:
                    attached_configlet.append(configlet_list_attach)
                    attached['configlet_attached'] = attached['configlet_attached'] + 1

        # Remove configlets from containers
        # def remove_configlets_from_container(self, app_name, container,del_configlets, create_task=True):
        container_info_cvp = container_factinfo(
            container_name=container_name, facts=facts)
        MODULE_LOGGER.info('get container info: %s for container %s', str(
            container_info_cvp), str(container_name))
        if container_info_cvp is not None and 'configlets' in container_info_cvp:
            for configlet in container_info_cvp['configlets']:
                # If configlet matchs filter, we just remove attachment.
                match_filter = tools.match_filter(
                    input=configlet, filter=configlet_filter, default_always='none')
                MODULE_LOGGER.info('Filter test has returned: %s - Filter is %s - input is %s', str(match_filter), str(configlet_filter), str(configlet))
                # If configlet is not in intended and does not match filter, ignore it
                # If filter is set to ['none'], we consider to NOT touch attachment in any situation.
                if (match_filter is False
                        and container_factinfo(container_name=container, facts=facts) is not None
                        and configlet not in container_factinfo(container_name=container, facts=facts)['configlets']):
                    MODULE_LOGGER.warning('configlet does not match filter (%s) and is not in intended topology (%s), skipped', str(
                        configlet_filter), str(container_info_cvp['configlets']))
                    continue
                # If configlet is not part of intended list and match filter: we remove
                container_factsinfo = container_factinfo(
                    container_name=container_name, facts=facts)
                # If there is no configlet found in facts, just skipping this section.
                if 'configlets' not in container_factsinfo:
                    MODULE_LOGGER.info('container %s has no configlets attached - skipped', str(container))
                    continue
                if match_filter and configlet not in ['configlets']:
                    MODULE_LOGGER.debug(
                        'collecting information for configlet %s', str(configlet))
                    # Get CVP information for device.
                    configlet_cvpinfo = configlet_factinfo(configlet_name=configlet, facts=facts)
                    # Configlet information is saved for later deployment
                    MODULE_LOGGER.warning(
                        'addind configlet %s to list of detach...', str(configlet))
                    configlet_list_detach.append(configlet_cvpinfo)

            # Create debug output structure
            configlets_name = list()
            for configlet in configlet_list_detach:
                configlets_name.append(configlet['name'])
            # Configure new configlet to container
            if len(configlet_list_detach) > 0:
                MODULE_LOGGER.info('Removing %s from %s', str(
                    configlets_name), str(container_info_cvp['name']))
                configlet_action = module.client.api.remove_configlets_from_container(app_name="ansible_cv_container",
                                                                                      del_configlets=configlet_list_detach,
                                                                                      container=container_info_cvp,
                                                                                      create_task=save_topology)
                MODULE_LOGGER.debug('Get following response from cvprac for deletion: %s', str(configlet_action))
                # Release list of configlet to configure (#165)
                configlet_list_detach = list()
                if 'data' in configlet_action and configlet_action['data']['status'] == 'success':
                    if 'taskIds' in configlet_action['data']:
                        for task in configlet_action['data']['taskIds']:
                            task_ids.append(task)
                    if len(configlet_list_detach) > 0:
                        detached_configlet.append(configlet_list_detach)
                        detached['configlet_attached'] = detached['configlet_list_detach'] + 1

    # Build ansible output messages.
    attached['list'] = attached_configlet
    attached['taskIds'] = task_ids
    result['changed'] = True
    result['attached_configlet'] = attached
    result['detached_configlet'] = detached
    MODULE_LOGGER.debug('configure_configlet_to_container returns %s', str(result))
    return result


def delete_topology(module, intended, facts):
    """
    Delete CVP Topology when state is set to absent.

    Parameters
    ----------
    module : AnsibleModule
        Object representing Ansible module structure with a CvpClient connection
    intended : list
        List of expected containers based on following structure:
    facts : list
        List of containers extracted from CVP using cv_facts.
    """
    # default_containers = ['Tenant', 'Undefined', 'root']
    count_container_deletion = 0
    container_to_delete = list()

    # Get root container for current topology
    topology_root = tools_tree.get_root_container(containers_fact=facts['containers'])
    # First try to get relative topology root container.
    topology_root_relative = tools_tree.locate_relative_root_container(containers_topology=intended)
    # If not found for any reason, fallback to CVP root container.
    if topology_root_relative is None:
        topology_root_relative = tools_tree.get_root_container(
            containers_fact=facts['containers'])
    MODULE_LOGGER.info('relative topology root is: %s', str(topology_root))
    # Build a tree of containers configured on CVP
    MODULE_LOGGER.info('build tree topology from facts topology')
    container_cvp_tree = tools_tree.tree_build_from_list(
        containers=facts['containers'], root=topology_root)
    container_cvp_ordered_list = tools_tree.tree_to_list(json_data=container_cvp_tree, myList=list())  # noqa # pylint: disable=unused-variable

    # Build a tree of containers expected to be deleted from CVP
    MODULE_LOGGER.info('build tree topology from intended topology')
    container_intended_tree = tools_tree.tree_build_from_dict(
        containers=intended, root=topology_root_relative)
    container_intended_ordered_list = tools_tree.tree_to_list(json_data=container_intended_tree, myList=list())

    MODULE_LOGGER.info('container_intended_ordered_list %s', container_intended_ordered_list)

    container_to_delete = list()
    # Check if containers can be deleted (i.e. no attached devices)
    for cvp_container in container_intended_ordered_list:
        # Do not run test on built-in containers
        if cvp_container not in builtin_containers:
            # Only container with no devices can be deleted.
            # If container is not empty, no reason to go further.
            if is_empty(module=module, container_name=cvp_container, facts=facts) or is_container_empty(module=module, container_name=cvp_container):
                # Check if a container is not present in intended topology.
                if cvp_container in container_intended_ordered_list:
                    container_to_delete.append(cvp_container)

    MODULE_LOGGER.debug('containers_to_delete %s', str(container_to_delete))

    for cvp_container in reversed(container_to_delete):
        MODULE_LOGGER.debug('deletion of cvp_container %s', str(cvp_container))
        # Check if container is not in intended topology and not a default container.
        if cvp_container in container_to_delete and cvp_container not in builtin_containers:
            # Get container fact for parentName
            MODULE_LOGGER.debug('get_container_facts %s', cvp_container)
            container_fact = get_container_facts(container_name=cvp_container, facts=facts)
            # Check we have a result. Even if we should always have a match here.
            if container_fact is not None:
                MODULE_LOGGER.debug('container name: %s', container_fact['name'])
                response = process_container(module=module,
                                             container=container_fact['name'],
                                             parent=container_fact['parentName'],
                                             action='delete')
                if response[0]:
                    count_container_deletion += 1
    if count_container_deletion > 0:
        return [True, {'containers_deleted': "" + str(count_container_deletion) + ""}]
    return [False, {'containers_deleted': "0"}]


def get_tasks(taskIds, module):
    """
    Collect TASK INFO from CVP.

    Parameters
    ----------
    taskIds : list
        list of tasks ID to get.
    module : AnsibleModule
        Ansible Module with connection information.

    Returns
    -------
    list
        List of Task information.
    """

    tasksList = list()
    # remove duplicate entries
    taskIds = list(set(taskIds))
    # Get task content from CVP
    for taskId in taskIds:
        tasksList.append(task_info(module=module, taskId=taskId))
    return tasksList


def main():
    """
    Main entry point for module execution.
    """
    argument_spec = dict(
        topology=dict(type='dict', required=True),          # Topology to configure on CV side.
        cvp_facts=dict(type='dict', required=True),         # Facts from cv_facts module.
        configlet_filter=dict(type='list', default='none'),  # Filter to protect configlets to be detached
        mode=dict(type='str',
                  required=False,
                  default='merge',
                  choices=['merge', 'override', 'delete'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    MODULE_LOGGER.info('starting module cv_container')
    if module.check_mode:
        MODULE_LOGGER.warning('! check_mode is enable')
        # module.exit_json(changed=True)

    if not tools_cv.HAS_CVPRAC:
        module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not tools_tree.HAS_TREELIB:
        module.fail_json(msg='treelib required for this module')

    if not schema.HAS_JSONSCHEMA:
        module.fail_json(
            msg="jsonschema is required. Please install using pip install jsonschema")

    if not schema.validate_cv_inputs(user_json=module.params['topology'], schema=schema.SCHEMA_CV_CONTAINER):
        MODULE_LOGGER.error("Invalid configlet input : %s",
                            str(module.params['configlets']))
        module.fail_json(
            msg='Container input data are not compliant with module.')

    result = dict(changed=False, data={})
    result['data']['taskIds'] = list()
    result['data']['tasks'] = list()
    deletion_process = None
    creation_process = None

    if not module.check_mode:
        module.client = tools_cv.cv_connect(module)

    # Create list of builtin containers
    create_builtin_containers(facts=module.params['cvp_facts'])
    if module.params['mode'] in ['merge', 'override']:
        # -> Start process to create new containers
        if (tools.isIterable(module.params['topology']) and module.params['topology'] is not None):
            creation_process = create_new_containers(module=module,
                                                     intended=module.params['topology'],
                                                     facts=module.params['cvp_facts'])
            if creation_process[0]:
                result['data']['changed'] = True
                result['data']['creation_result'] = creation_process[1]
            # -> Start process to move devices to targetted containers
            move_process = move_devices_to_container(module=module,
                                                     intended=module.params['topology'],
                                                     facts=module.params['cvp_facts'])
            if move_process is not None:
                result['data']['changed'] = True
                # If a list of task exists, we expose it
                if 'taskIds' in move_process['moved_devices']:
                    for taskId in move_process['moved_devices']['taskIds']:
                        result['data']['taskIds'].append(taskId)
                # move_process['moved_devices'].pop('taskIds',None)
                result['data']['moved_result'] = move_process['moved_devices']

            # -> Start process to move devices to targetted containers
            attached_process = configure_configlet_to_container(module=module,
                                                                intended=module.params['topology'],
                                                                facts=module.params['cvp_facts'])
            if attached_process is not None:
                result['data']['changed'] = True
                # If a list of task exists, we expose it
                if 'taskIds' in attached_process['attached_configlet']:
                    for taskId in attached_process['attached_configlet']['taskIds']:
                        result['data']['taskIds'].append(taskId)
                # move_process['moved_devices'].pop('taskIds',None)
                result['data']['attached_configlet'] = attached_process['attached_configlet']

    # If MODE is override we also delete containers with no device and not listed in our topology
    if module.params['mode'] == 'override':
        # -> Start process to delete unused container.
        if (tools.isIterable(module.params['topology']) and module.params['topology'] is not None):
            deletion_process = delete_unused_containers(module=module,
                                                        intended=module.params['topology'],
                                                        facts=module.params['cvp_facts'])
        else:
            deletion_process = delete_unused_containers(module=module,
                                                        intended=dict(),
                                                        facts=module.params['cvp_facts'])
        if deletion_process[0]:
            result['data']['changed'] = True
            result['data']['deletion_result'] = deletion_process[1]

    # If MODE is DELETE then we start process to delete topology
    elif module.params['mode'] == 'delete':
        # -> Start process to delete container described in topology.
        if (tools.isIterable(module.params['topology']) and module.params['topology'] is not None):
            deletion_topology_process = delete_topology(module=module,
                                                        intended=module.params['topology'],
                                                        facts=module.params['cvp_facts'])
            if deletion_topology_process[0]:
                result['data']['changed'] = True
                result['data']['deletion_result'] = deletion_topology_process[1]

    if len(result['data']['taskIds']) > 0:
        result['data']['tasks'] = get_tasks(module=module, taskIds=result['data']['taskIds'])

    # DEPRECATION: Make a copy to support old namespace.
    result['cv_container'] = result['data']

    module.exit_json(**result)


if __name__ == '__main__':
    main()
