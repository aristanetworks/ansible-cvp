#!/usr/bin/env python
#
# Copyright (c) 2019, Arista Networks EOS+
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
DOCUMENTATION = """
---
module: cv_device
version_added: "2.2"
author: "EMEA AS (ansible-dev@arista.com)"
short_description: Provision, Reset, or Update CloudVision Portal Devices.
description:
  - CloudVison Portal Device compares the list of Devices in
  in devices against cvp-facts then adds, resets, or updates them as appropriate.
  If a device is in cvp_facts but not in devices it will be reset to factory defaults
  If a device is in devices but not in cvp_facts it will be provisioned
  If a device is in both devices and cvp_facts its configlets and imageBundles will be compared
  and updated with the version in devices if the two are different.
"""
# Required by Ansible and CVP
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cv_client import CvpClient
from ansible.module_utils.cv_client_errors import CvpLoginError, CvpApiError
import re
from time import sleep

def connect(module):
    ''' Connects to CVP device using user provided credentials from playbook.
    :param module: Ansible module with parameters and client connection.
    :return: CvpClient object with connection instantiated.
    '''
    client = CvpClient()
    try:
        client.connect([module.params['host']],
                       module.params['username'],
                       module.params['password'],
                       protocol=module.params['protocol'],
                       port=module.params['port'],
                       )
    except CvpLoginError, e:
        module.fail_json(msg=str(e))
    return client

def device_action(module):
    ''' Compare devices in "devices" with devices in "cvp_facts"
    if device exists in "cvp_facts" check images and configlets, if changed update
    if device does not exist in "cvp_facts" add to CVP
    if configlet in "cvp_facts" but not in "configlets" remove from CVP if
    not applied to a device or container.
    :param module: Ansible module with parameters and client connection.
    :return: data: dict of module actions and taskIDs
    '''
    # If any configlet changed updated 'changed' flag
    changed = False
    #Compare configlets against cvp_facts-configlets
    unchanged_device = [] # devices with no changes
    reset_device = [] # devices to factory reset
    reset = []
    update_device = [] # devices with configlet or image changes
    updated = []
    new_device = [] # devices to add to CVP requires container ID from cv_facts
    new = []
    newTasks = [] # Task Ids that have been identified during device actions
    taskList = [] # Tasks that have a pending status after function runs

    # Check for existing devices
    for cvp_device in module.params['cvp_facts']['devices']:
        # Include only devices that match filter elements, "all" will
        # include all devices.
        if re.search(r"\ball\b", str(module.params['device_filter'])) or (
            any(element in cvp_device['name'] for element in module.params['device_filter'])):
            # Check to see if devcie is to be deleted (not in ansible list)
            if cvp_device['name'] in module.params['devices']:
                # Make sure the device is not in the Undefined container
                if "undefined_container" != str(cvp_device['parentContainerKey']):
                    ansible_device = module.params['devices'][cvp_device['name']]
                    # Check assigned configlets
                    device_update = False
                    add_configlets = []
                    remove_configlets = []
                    for configlet in cvp_device['deviceSpecificConfiglets']:
                        if configlet not in ansible_device['configlets']:
                            remove_configlets.append(configlet)
                            device_update = True
                    for configlet in ansible_device['configlets']:
                        if configlet not in cvp_device['deviceSpecificConfiglets']:
                            add_configlets.append(configlet)
                            device_update = True
                    # Check assigned images
                    add_imageBundle = ''
                    remove_imageBundle = ''
                    if 'imageBundle' in ansible_device and str(cvp_device['imageBundle']) != str(ansible_device['imageBundle']):
                        if str(ansible_device['imageBundle']) != "":
                            add_imageBundle = str(ansible_device['imageBundle'])
                            device_update = True
                        else:
                            remove_imageBundle = str(cvp_device['imageBundle'])
                            device_update = True
                    if device_update:
                        update_device.append({'name':cvp_device['name'],
                                              'configlets':[add_configlets,remove_configlets],
                                              'imageBundle':[add_imageBundle,remove_imageBundle],
                                              'device':cvp_device})
            # If device not in ansible list and not excluded by filter reset it
            else:
                # Assume device has already been reset if its in the Undefined container
                if cvp_device['parentContainerKey'] != 'undefined_container':
                    reset_device.append(cvp_device)
                else:
                    message = "Device %s cannot be reset - Already in Undefined container"%cvp_device['name']
                    reset.append({cvp_device['name']:'No_Reset-No_Tasks'})

    # Check for new devices
    # Device will be in the CVP Inventory and also in the Undefined container
    # Non provisioned device (telemetry only) will not be in a container
    for ansible_name in module.params['devices']:
        cvp_device_found = False
        ansible_device = module.params['devices'][ansible_name]
        # Include only devices that match filter elements, "all" will
        # include all devices.
        if re.search(r"\ball\b", str(module.params['device_filter'])) or (
            any(element in ansible_device['name'] for element in module.params['device_filter'])):
            # Check to see if devcie is to be added (not in CVP list)
            for s_device in module.params['cvp_facts']['devices']:
                if str(ansible_device['name']) == str(s_device['name']):
                    cvp_device_found = True
                    cvp_device = s_device
                    break
            # If the device is in CVP check which container it is in only devices in "Undefined"
            # can be provisioned, the rest should be handled by cv_container
            if cvp_device_found:
                # Make sure the new device is in the Undefined container
                if "undefined_container" == str(cvp_device['parentContainerKey']):
                    # Get destination container details from CVP facts
                    for dest_container in module.params['cvp_facts']['containers']:
                        if dest_container['name'] == ansible_device['parentContainerName']:
                            # Create New device update to add configlets and imageBundles
                            if len(ansible_device['configlets']) > 0:
                                ansible_configlets = ansible_device['configlets']
                            else:
                                ansible_configlets =[]
                            if len(ansible_device['imageBundle']) > 0:
                                ansible_imageBundle = ansible_device['imageBundle']
                            else:
                                ansible_imageBundle =[]
                            # Create new device details
                            new_device.append({'cvp_device':cvp_device,'container':dest_container,
                                               'ansible_device':ansible_device,
                                               'configlets':ansible_configlets,
                                               'imageBundle':ansible_imageBundle})
                            break
                elif "" == str(cvp_device['parentContainerKey']):
                    message = "Device %s cannot be provisioned - Telemetry Only"%ansible_device['name']
                    new.append({ansible_device['name']:message})
            else:
                message = "Device %s cannot be provisioned - Not in CVP Inventory"%(ansible_device['name'])
                new.append({ansible_device['name']:message})
    # Action Devices as required
    # If Ansible check_modde is True then skip any actions and return predicted outcome
    if not module.check_mode:
        if len(reset_device) > 0:
            print "\nReset Devices:"
            # Factory Reseting Devices and returning them to Undefined container
            for device in reset_device:
                print"   %s" %device['name']
                try:
                    device_action = module.client.api.reset_device("Ansible",device)
                except Exception as error:
                    errorMessage = str(error)
                    message = "Device %s cannot be reset - %s"%(device['name'],errorMessage)
                    reset.append({device['name']:message})
                else:
                    if "errorMessage" in str(device_action):
                        message = "Device %s cannot be Reset - %s"%(device['name'],device_action['errorMessage'])
                        reset.append({device['name']:message})
                    else:
                        changed = True
                        if 'taskIds' in device_action.keys():
                            for taskId in device_action['taskIds']:
                                newTasks.append(taskId)
                            reset.append({device['name']:'Reset-%s'%device_action['tasksIds']})
                        else:
                            reset.append({device['name']:'Reset-No_Tasks'})
        if len(new_device) > 0:
            # Provision (move from Undefined, add Configlets and Images) new Devices
            # new_device schema ([cvp_device,dest_container,ansible_device])
            for device in new_device:
                add_configlets = []
                add_imageBundle = {}
                if device['cvp_device']['parentContainerKey'] == 'undefined_container':
                    if len(device['configlets']) > 0:
                        for add_configlet in device['configlets']:
                            for configlet in module.params['cvp_facts']['configlets']:
                                if add_configlet == configlet['name']:
                                    add_configlets.append({'name':add_configlet,'key':configlet['key']})
                    if len(device['imageBundle']) > 0:
                        for imageBundle in module.params['cvp_facts']['imageBundles']:
                            if str(device['imageBundle']) == str(imageBundle['name']):
                                add_imageBundle = {'name':imageBundle['name'],'key':imageBundle['key']}
                                break
                    try:
                        new_device_action = module.client.api.provision_device('Ansible',device['cvp_device'],
                                                                                  device['container'],
                                                                                  add_configlets,
                                                                                  add_imageBundle)
                    except Exception as error:
                        errorMessage = str(error)
                        message = "New device %s cannot be added - Exception: %s"%(device['cvp_device']['name'],
                                                                                   errorMessage)
                        new.append({device['cvp_device']['name']:message})
                    else:
                        if "errorMessage" in str(new_device_action):
                            message = "New device %s cannot be added - Error: %s"%(device['cvp_device']['name'],
                                                                                   new_device_action['errorMessage'])
                            new.append({device['cvp_device']['name']:message})
                        else:
                            changed = True
                            if 'taskIds' in str(new_device_action):
                                for taskId in new_device_action['data']['taskIds']:
                                    newTasks.append(taskId)
                                new.append({device['cvp_device']['name']:"New_Device-%s"
                                            %new_device_action['data']['taskIds']})
                            else:
                                new.append({device['cvp_device']['name']:"New_Device-No_Specific_Tasks"})
        if len(update_device) > 0:
            # Update Configlets and ImageBundles for Devices
            # Data passed in update_device
            #{'name':cvp_device['name'],'configlets':[add_configlets,remove_configlets],
            # 'imageBundle':[add_imageBundle,remove_imageBundle],'device':cvp_device})
            for device in update_device:
                add_configlets = []
                del_configlets = []
                add_imageBundle = {}
                del_imageBundle = {}
                update_configlets = False
                update_imageBundle = False
                # Update Configlets
                if len(device['configlets'][0]) > 0:
                    update_configlets = True
                    for add_configlet in device['configlets'][0]:
                        for configlet in module.params['cvp_facts']['configlets']:
                            if add_configlet == configlet['name']:
                                add_configlets.append({'name':add_configlet,'key':configlet['key']})
                if len(device['configlets'][1]) > 0:
                    update_configlets = True
                    for del_configlet in device['configlets'][1]:
                        for configlet in module.params['cvp_facts']['configlets']:
                            if del_configlet == configlet['name']:
                                del_configlets.append({'name':del_configlet,'key':configlet['key']})
                if update_configlets:
                    try:
                        device_action = module.client.api.update_configlets_on_device('Ansible',
                                                                                      device['device'],
                                                                                      add_configlets,
                                                                                      del_configlets)
                    except Exception as error:
                        errorMessage = str(error)
                        message = "Device %s Configlets cannot be updated - %s"%(device['name'],errorMessage)
                        updated.append({device['name']:message})
                    else:
                        if "errorMessage" in str(device_action):
                            message = "Device %s Configlets cannot be Updated - %s"%(device['name'],device_action['errorMessage'])
                            updated.append({device['name']:message})
                        else:
                            changed = True
                            if 'taskIds' in str(device_action):
                                for taskId in device_action['data']['taskIds']:
                                    newTasks.append(taskId)
                                updated.append({device['name']:"Configlets-%s" %device_action['data']['taskIds']})
                            else:
                                updated.append({device['name']:"Configlets-No_Specific_Tasks"})

                # Update ImageBundles
                # There can only be one ImageBundle per device so accept only the first entry in list
                if len(device['imageBundle'][0]) > 0:
                    update_imageBundle = True
                    for imageBundle in module.params['cvp_facts']['imageBundles']:
                        if str(device['imageBundle'][0]) == str(imageBundle['name']):
                            add_imageBundle = {'name':imageBundle['name'],'key':imageBundle['key']}
                            break
                if len(device['imageBundle'][1]) > 0:
                    update_imageBundle = True
                    for imageBundle in module.params['cvp_facts']['imageBundles']:
                        if str(device['imageBundle'][1]) == str(imageBundle['name']):
                            del_imageBundle = {'name':imageBundle['name'],'key':imageBundle['key']}
                            break
                # Apply imageBundle updates to device if required
                if update_imageBundle:
                    try:
                        device_action = module.client.api.update_imageBundle_on_device('Ansible',
                                                                                      device['device'],
                                                                                      add_imageBundle,
                                                                                      del_imageBundle)
                    except Exception as error:
                        errorMessage = str(error)
                        message = "Device %s imageBundle cannot be updated - Exception: %s"%(device['name'],errorMessage)
                        updated.append({device['name']:message})
                    else:
                        if "errorMessage" in str(device_action):
                            message = "Device %s imageBundle cannot be updated - Error: %s"%(device['name'],device_action['errorMessage'])
                            updated.append({device['name']:message})
                        else:
                            changed = True
                            if 'taskIds' in str(device_action):
                                for taskId in device_action['data']['taskIds']:
                                    newTasks.append(taskId)
                                updated.append({device['name']:"imageBundle-%s"%device_actions['data']['taskIds']})
                            else:
                                updated.append({device['name']:"imageBundle-No_Specific_Tasks"})

        # Get any Pending Tasks in CVP
        if changed:
            # Allow CVP to generate Tasks
            sleep(10)
            # Build required data for tasks in CVP - work order Id, current task status, name
            # description
            tasksField = {'name':'name','workOrderId':'taskNo','workOrderState':'status',
                          'currentTaskName':'currentAction','description':'description',
                          'workOrderUserDefinedStatus':'displayedStutus','note':'note',
                          'taskStatus':'actionStatus'}
            tasks = module.client.api.get_tasks_by_status('Pending')
            # if tasks IDs were created for device actions then return only those.
            createdTasks = []
            if len(newTasks) > 0:
                for taskId in newTasks:
                    for task in tasks:
                        if taskId == task['workOrderId']:
                            createdTasks.append(task)
            else:
                createdTasks = tasks
            # Reduce task data to required fields
            for task in createdTasks:
                taskFacts= {}
                for field in task.keys():
                    if field in tasksField:
                        taskFacts[tasksField[field]] = task[field]
                taskList.append(taskFacts)
        data = {'new':new,'updated':updated,'reset':reset,'tasks':taskList}
    else:
        # Only display action results as Ansible check_mode is active
        for device in new_device:
            new.append({device[0]['name']:"checked"})
        for device in update_device:
            updated.append({device['name']:"checked",
                            'configlets':device['configlets'],
                            'imageBundle':device['imageBundle']})
        for device in reset_device:
            reset.append({device['name']:"checked"})
        data = {'new':new,'updated':updated,'reset':reset,'tasks':taskList}
    return [changed,data]


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        host=dict(required=True),
        port=dict(type='int', default=None),
        protocol=dict(default='https', choices=['http', 'https']),
        username=dict(required=True),
        password=dict(required=True),
        devices=dict(type='dict',required=True),
        cvp_facts=dict(type='dict',required=True),
        device_filter=dict(type='list', default='none')
        )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    result = dict(changed=False,data={})
    messages = dict(issues=False)
    # Connect to CVP instance
    module.client = connect(module)

    # Pass module params to configlet_action to act on configlet
    result['changed'],result['data'] = device_action(module)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
