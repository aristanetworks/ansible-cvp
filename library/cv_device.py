#!/usr/bin/env python
#
# Copyright (c) 2019, Arista Networks AS-EMEA
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
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
short_description: Create or Update CloudVision Portal Devices.
description:
  - CloudVison Portal Device configuration requires the device name,
    and the container name to move a device into a container
  - Device configuration requires the devcie name and a list of Configlets
    and / or Configlet Builders to apply to apply to it.
  - Device configuration requires the devcie name.
  - Returns the device data and any Task IDs created during the operation
options:
  host:
    description: IP Address or hostname of the CloudVisin Server
    required: true
    default: null
  username:
    description: The username to log into Cloudvision.
    required: true
    default: null
  password:
    description: The password to log into Cloudvision.
    required: true
    default: null
  protocol:
    description: The HTTP protocol to use. Choices http or https.
    required: false
    default: https
  port:
    description: The HTTP port to use. The cvprac defaults will be used
                  if none is specified.
    required: false
    default: null
  device:
    description: CVP device to apply the configlets to
    required: true
    default: None
  container:
    description: CVP container to add/delete device to/from if CVP
                  is specified for a delete option device will be removed
                  completely from CVP.
    required: false
    default: 'Tenant'
  configlet:
      description: List of Configlet to add or remove from device
      required: false
      default: None
  action:
    description: action to carry out on the container
                  add - place a device in a container and/or add Configlets
                  delete - remove a device from a container and factory reset if Container = RESET
                           or remove Configlets if container = Parent Container for Device
                           or if Container = CVP remove from CVP
                  show - return the current device data if available
    required: true
    choices: 
      - 'show'
      - 'add'
      - 'delete'
    default: show
"""

EXAMPLES="""
# Move a device to a new container
# Container must already exist
- name: Move device to CVP container
  cv_device:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    device: "{{cvp_device}}"
    container: "{{container_name}}"
    action: add
    register: cvp_result

# Display information for device before a container's move
- name: Show device information from CVP
  tags: create, show
  cv_device:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    device: "{{cvp_device}}"
    action: show
    register: cvp_result

- name: Display cv_device add result
  tags: create, show
  debug:
    msg: "{{cvp_result}}"

# Reset device from CVP
- name: Reset device from CVP
  tags: rollback
  cv_device:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    device: "{{cvp_device}}"
    container: "RESET"
    action: delete
"""

from ansible.module_utils.basic import AnsibleModule
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError


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

def device_info(module):
    ''' Get dictionary of device info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of device info from CVP or exit with failure if no
             info for device is found.
    '''
    device_info = module.client.api.get_device_by_name(module.params['device'])
    if not device_info:
            devices = module.client.api.get_inventory()
            for device in devices:
              if module.params['device'] in device['fqdn']:
                device_info = device
    if not device_info:
        ## Debug Line ##
        module.fail_json(msg=str('Debug - device_info: %r' %device_info))
        ## Debug Line ##
        device_info['error']="Device with name '%s' does not exist." % module.params['device']
    else:
        device_info['configlets'] = module.client.api.get_configlets_by_netelement_id(device_info['systemMacAddress'])['configletList']
        device_info['parentContainer'] = module.client.api.get_container_by_id(device_info['parentContainerKey'])
    return device_info

def container_info(module):
    ''' Get dictionary of container info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of container info from CVP or exit with failure if no
             info for device is found.
    '''
    container_info = module.client.api.get_container_by_name(module.params['container'])
    if container_info == None:
        container_info = {}
        container_info['error'] = "Container with name '%s' does not exist." % module.params['container']
    else:
        container_info['configlets'] = module.client.api.get_configlets_by_container_id(container_info['key'])
    return container_info

def process_device(module):
    '''Ensure device exists then process it
       add - add to container and apply device specific Configlets
             add can move device from one container to another
       delete - if container is CVP remove from CVP - GUI Remove Option
                if container is Device Parent - factory reset device to Undefined
       show - show current device config and data'''
    result={'changed':False,'data':{},'config':{}}
    # Check that device exist in CVP
    deviceData = False
    reconcile = False
    #devices = module.client.api.get_inventory()
    #for device in devices:
    #  if module.params['device'] in device['fqdn']:
    #    deviceData = device
    #    deviceData['parentContainer'] = module.client.api.get_container_by_id(device['parentContainerKey'])
    deviceData = device_info(module)
    if "error" not in deviceData.keys():
        # Collect Required Configlets to apply to device
        if 'none' not in str(module.params['configlet']).lower():
            configletData = []
            for configlet in module.params['configlet']:
                temp_configlet = module.client.api.get_configlet_by_name(configlet)
                # Add configlet to list if there are no errors
                if "error" not in str(temp_configlet):
                    configletData.append(temp_configlet)
                else:
                    module.fail_json(msg=str('Fetch Configlet details %s failed: %s'
                                             %(configlet, temp_configlet)))
        else:
            configletData = "None"
        # Used for existing config on a valid device
        existing_config = 'None'
        # Work out where switch is in provisoning hierachy and act accordingly
        # New device found in ZTP mode
        if deviceData['parentContainerKey'] == "undefined_container":
            # New Device found with existing config (not ZTP boot mode)
            if deviceData['ztpMode'] == False:
                existing_config = module.client.api.get_device_configuration(deviceData['systemMacAddress'])
            if module.params['action'] == "add":
                # FIX Issue #10: deploy_device is testing if configlet is not None
                # current implemetation uses a string instead of python None type.
                # Add a new test to emulate None.
                if configletData != 'None':
                    device_action = module.client.api.deploy_device(device=deviceData, container=module.params['container'],configlets=configletData)
                else:
                    device_action = module.client.api.deploy_device(device=deviceData, container=module.params['container'])
                if "error" not in device_action:
                    result['changed'] = True
                    reconcile = True
                    result['data']=device_action['data']
                    result['config']['current'] = existing_config
                else:
                    result['data']=device_action
            elif module.params['action'] == "delete":
                result['data'] = ["Error: Device in Undefined Container",deviceData]
                module.fail_json(msg=str('Delete Device %s failed: Device In Undefined'
                                         %deviceData['fqdn']))
            elif module.params['action'] == "show":
                result['data'] = deviceData
                result['config']['current']=existing_config
                reconcile = True
            else:
                result['data'] = {"error":"Unsupported Option"}
        # Existing Device Found
        elif deviceData['parentContainerKey'] != 'undefined_container':
            existing_config = module.client.api.get_device_configuration(deviceData['systemMacAddress'])
            if module.params['action'] == "add":
                # Add device to container
                target_container = module.client.api.get_container_by_name(module.params['container'])
                if ("error" not in str(target_container)) and ("None" not in str(target_container)):
                    device_action = module.client.api.move_device_to_container("Ansible", deviceData,
                                                             target_container,
                                                             create_task=True)
                    if "error" not in device_action:
                        result['changed']= True
                        reconcile = True
                        result['data']=device_action['data']
                        result['config']['current'] = existing_config
                    else:
                        result['data']=device_action
                    # Add Configlets to device
                    if configletData != 'None':
                        device_addConfiglets = module.client.api.apply_configlets_to_device("Ansible",
                                                                                               deviceData,
                                                                                               configletData,
                                                                                               create_task=True)
                        if "error" not in device_addConfiglets:
                            result['changed']= True
                            reconcile = True
                            result['config']['current'] = existing_config
                            # Add tasks to result data if they are not there already
                            if 'taskIds' in str(result['data']):
                                for taskId in device_addConfiglets['data']['taskIds']:
                                    if taskId not in result['data']['taskIds']:
                                        result['data']['taskIds'].append(taskId)
                            else:
                                result['data'].update(device_addConfiglets)
                        else:
                            result['data'].update(device_addConfiglets)
                else:
                    result['data']={'targetContainer_Returned':target_container}
                    result['config']['current'] = existing_config
            elif module.params['action'] == "delete":
                # Check Container remove configlets and / or remove device from container
                # if container is CVP remove from CVP, if container is Device Parent factory reset device
                if module.params['container'] == "CVP":
                    device_action = module.client.api.delete_device(deviceData['systemMacAddress'])
                    if "error" not in str(device_action).lower():
                        result['changed']= True
                        result['data']=device_action['data']
                        result['config']['current'] = existing_config
                    else:
                        result['data']=device_action
                elif module.params['container'] == "RESET":
                    device_action = module.client.api.reset_device("Ansible",deviceData)
                    if "error" not in str(device_action).lower():
                        result['changed'] = False
                        result['data'] = device_action['data']
                        result['config']['current'] = existing_config
                elif module.params['container'] == deviceData['parentContainer']['name']:
                    if configletData != 'None':
                        device_action = module.client.api.remove_configlets_from_device("Ansible",deviceData,
                                                                                           configletData,
                                                                                           create_task=True)
                    else:
                        device_action = {'data':"error - No Valid Configlets to remove"}
                    if "error" not in str(device_action).lower():
                        result['changed'] = False
                        result['data'] = device_action['data']
                        result['config']['current'] = existing_config
                else:
                    result['data'] = deviceData
                    module.fail_json(msg=str('Delete Device %s failed: Device in %s'
                                             %(deviceData['fqdn'],
                                               deviceData['parentContainer']['name'])))
            elif module.params['action'] == "show":
                reconcile = True
                result['data'] = deviceData
                result['config']['current']=existing_config
            else:
                errorOutput = 'Invalid Option: %s'%module.params['action']
                result['data'] = {'error':errorOutput}
        if reconcile:
            temp_reconcile = module.client.api.get_device_reconcile_config(deviceData['systemMacAddress'])
            if "config" in temp_reconcile:
                result['config']['reconcile'] = temp_reconcile['config']
            else:
                result['config']['reconcile'] = temp_reconcile
        else:
            result['config']['reconcile'] = ""
    # No Device Found
    else:
      errorOutput = 'No Device Found: %s' %module.params['device']
      result['data']={'error':errorOutput}
    return result

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        host=dict(required=True),
        port=dict(type='int', default=None),
        protocol=dict(default='https', choices=['http', 'https']),
        username=dict(required=True),
        password=dict(required=True, no_log=True),
        device=dict(required=True),
        container=dict(default='None'),
        configlet=dict(type='list', default='None'),
        action=dict(default='show', choices=['add','delete','show'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    result = dict(changed=False)

    module.client = connect(module)

    try:
        changed = process_device(module)
    except CvpApiError, e:
        module.fail_json(msg=str(e))
    else:
        if changed['changed']:
            result['changed'] = True
            if 'taskIds' in str(changed['data']):
                result['taskIDs'] = changed['data']['taskIds']
            elif 'taskIdList' in str(changed['data']):
                result['taskIDs'] = changed['data']['taskIdList']
            else:
                result['taskIDs'] = 'None'
            result['config'] = changed['config']
        else:
            result['data'] = changed['data']

    module.exit_json(**result)


if __name__ == '__main__':
    main()
