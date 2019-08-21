#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from ansible.module_utils.basic import AnsibleModule
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError

import re
import time
from jinja2 import meta
import jinja2
import yaml


ANSIBLE_METADATA = {'metadata_version': '0.0.1.dev0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: cv_configlet
short_description: Create or Update CloudVision Portal Configlet.
description:
  - CloudVison Portal Configlet configuration requires the configlet name,
    container or device to apply to, and configuration to be applied
  - Returns the configlet data and any Task IDs created during the operation
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
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
    description: The HTTP port to use. The cvprac defaults will be used if none is specified.
    required: false
    default: null
  container:
    description: CVP container to apply the configlet to if no device is specified
    required:  false
    default:  None
  device:
    description:  CVP device to apply configlet to overides contianer association
    required:  false
    default:  None
  parent:
    description:  Name of the Parent container for the container specified
        Used to configure target container and double check container configuration
    required:  false
    default:  'Tenant'
  configletName:
    description:  If associated with a device the configlet name will 
      be 'device_configletName' if configletName has been provided otherwise 
      it will be 'device_template' if none of the above have been provided it 
      will be 'configletName' if that was not provided a default name of 'Ansible_Test' will be used
    required: false
    default:  None
  template:
    description:  Jinja2 Template used to create configlet configuration block
    required:  true
    default:  null
  data:
    description:  location of data file to use with Jinja2 template
    required:  true
    default:  null
  action:
    description: action to carry out on configlet
                    add - create the configlet and add it to container or device
                    delete - remove from container or device, if configlet has
                            has no other associations then delete it
                    show - return the current configuration in the configlet
                        and the new configuration if generated
    required:  true
    choices:  
      - 'show'
      - 'add'
      - 'delete'
    default:  show
"""

EXAMPLES = r'''
# Create configlet attached to container
- name: Create a configlet on CVP.
  cv_configlet:
    host: '{{cvp_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    container: "{{container_name}}"
    parent: "{{container_parent}}"
    configletName: "{{configlet_name}}"
    template: "{{configlet_template}}"
    data: "{{configlet_data}}"

# Show configlet attached to container
- name: Show configlet configured on CVP.
  cv_configlet:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    container: "{{container_name}}"
    parent: "{{container_parent}}"
    configletName: "{{configlet_name}}"
    action: show
    register: cvp_result

- name: Display cv_configlet show result
  debug:
    msg: "{{cvp_result}}"

# Delete configlet attached to container
- name: Delete a configlet on CVP.
  cv_configlet:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    container: "{{container_name}}"
    parent: "{{container_parent}}"
    configletName: "{{configlet_name}}"
    configletConfig: ""
    action: delete
'''

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
        device_info['warning']="Device with name '%s' does not exist." % module.params['device']
    else:
        device_info['configlets'] = module.client.api.get_configlets_by_netelement_id(device_info['systemMacAddress'])['configletList']
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
        container_info['warning'] = "Container with name '%s' does not exist." % module.params['container']
    else:
        container_info['configlets'] = module.client.api.get_configlets_by_container_id(container_info['key'])
    return container_info

def process_configlet(module, configlet):
    ''' Check the current status of a configlet.
    Returns a list of associated containers / devices
    Returns None if the configlet has no associations.
    If action = add apply configlet to device or container
                if device specified only apply to device
    If action = delete removes configlet from device or container
    param module: Ansible module with parameters and client connection.
    configlet: Name of Configlet to process
    return: Dict of action taken, containers/devices affected and counts of same
    '''

    result = {}
    # Find out if configlet is associated with any containers or devices
    configlet_info = module.client.api.get_configlet_by_name(configlet)
    result['start_container_count']= configlet_info["containerCount"]
    result['start_device_count'] = configlet_info["netElementCount"]

    # Get details of container
    if module.params['container'] != 'None':
        container_data = container_info(module)
        if 'Warning' in container_data:
            result['data']=container_data
            container_data = "None"
        container_list = module.client.api.get_applied_containers(configlet)['data']
        # Remove configlet from container if action = delete
        if module.params['action'] == "delete":
            for container in container_list:
                if module.params['container'] in container['containerName']:
                    if configlet_info["containerCount"] > 0 and module.params['device'] == 'None':
                        # Remove configlet from spcified container in module params
                        # If none specified then do not remove configlet
                        # If a device is specified in module params then do not remove configlet
                        result['action'] = 'delete_from_container'
                        if container_data != "None":
                            result['data'] = module.client.api.remove_configlets_from_container("Ansible",
                                                                                                container_data, [configlet_info])
                        else:
                            result['data'] = {'error':'container not found %s' %module.params['container']}
        if module.params['action'] == "add":
            if module.params['device'] == 'None':
                # Add configlet to spcified container in module params
                # If none specified then do not add configlet
                # If a device is specified in module params then do not add configlet
                result['action'] = 'add_to_container'
                if container_data != "None":
                    result['data'] = module.client.api.apply_configlets_to_container("Ansible",
                                                                                     container_data, [configlet_info])
                else:
                    result['data'] = {'error':'container not found %s' %module.params['container']}

    # Get details of device
    # Remove configlet from specified device in module params
    # If none specified then do not remove configlet
    if module.params['device'] != 'None':
        device_data = device_info(module)
        if "Warning" in device_data:
            result['data']=device_data
            device_data = "None"
        # Remove configlet from device if action = delete
        if module.params['action'] == "delete":
            device_list = module.client.api.get_applied_devices(configlet)['data']
            for device in device_list:
                # If configlet applied to device then delete it.
                if module.params['device'] in device['hostName']:
                    if configlet_info["netElementCount"] > 0 and device_data != "None":
                        result['action'] = 'delete_from_device'
                        result['data'] = module.client.api.remove_configlets_from_device("Ansible",
                                                                                            device_data, [configlet_info])
        # Add configlet to device if action = add
        if module.params['action'] == "add" and device_data != "None":
            result['action'] = 'add_to_device'
            result['data'] = module.client.api.apply_configlets_to_device("Ansible", device_data,
                                                                             [configlet_info],create_task=True)
    # Check to see if any containers or devices have been added or removed
    configlet_info = module.client.api.get_configlet_by_name(configlet)
    result['end_container_count']= configlet_info["containerCount"]
    result['end_device_count'] = configlet_info["netElementCount"]
    # Added
    if result['end_container_count'] > result['start_container_count']:
        result['added_container'] = container_data['name']
    else:
        result['added_container'] = False
    if result['end_device_count'] > result['start_device_count']:
        result['added_device'] = device_data['fqdn']
    else:
        result['added_device'] = False
    # Removed
    if result['end_container_count'] < result['start_container_count']:
        result['removed_container'] = container_data['name']
    else:
        result['removed_container'] = False
    if result['end_device_count'] < result['start_device_count']:
        result['removed_device'] = device_data['fqdn']
    else:
        result['removed_device'] = False
    return result


def process_container(module, container, parent):
    ''' Check for existence of a Container and its parent in CVP.
    Returns True if the Containerand Parent exist
    Creates Container if Parent exists but Container doesn't and
    Returns True
    Returns False if the Parent container does not exist and dose not
    create the Container specified.
    '''
    containers = module.client.api.get_containers()

    # Ensure the parent exists
    parent = next((item for item in containers['data'] if
                   item['name'] == parent), None)
    if not parent:
        module.fail_json(msg=str('Parent container does not exist.'))

    cont = next((item for item in containers['data'] if
                 item['name'] == container), None)
    if not cont:
        module.client.api.add_container(container, parent['name'],
                                        parent['key'])
        return True
    return False

def config_from_template(module):
    ''' Load the Jinja template and apply user provided parameters in necessary
        places. Fail if template is not found. Fail if rendered template does
        not reference the correct port. Fail if the template requires a VLAN
        but the user did not provide one with the port_vlan parameter.

    :param module: Ansible module with parameters and client connection.
    :return: String of Jinja template rendered with parameters or exit with
             failure.
    '''
    template = False
    if module.params['template']:
        template_loader = jinja2.FileSystemLoader('./templates')
        env = jinja2.Environment(loader=template_loader,
                                 undefined=jinja2.DebugUndefined)
        template = env.get_template(module.params['template'])
        if not template:
            module.fail_json(msg=str('Could not find template - %s'
                                     % module.params['template']))

        templateData = {}
        try:
            with open(module.params['data']) as handle:
                templateData["data"] = yaml.safe_load(handle)
        except Exception as e:
            print('Could not load data file: {0}'.format(e))
        
        templateData["device"] = module.params['device']
        templateData["container"] = module.params['container']
        temp_source = env.loader.get_source(env, module.params['template'])[0]
        parsed_content = env.parse(temp_source)
        temp_vars = list(meta.find_undeclared_variables(parsed_content))
        for var in temp_vars:
            if str(var) not in templateData["data"]:
                module.fail_json(msg=str('Template %s requires %s value - %s.'
                                         %(module.params['template'],var,yaml.dump(templateData["data"]))))
        try:
            template = template.render(templateData["data"])
            return template
        except Exception as templateError:
            module.fail_json(msg=str('Template - %s: does not render correctly: %s'
                                   %(module.params['template'],templateError)))
    else:
        module.fail_json(msg=str('Template - required but not provided'))
    return template

def configlet_action(module):
    ''' Act upon specified Configlet based on options provided.
        - show - display contents of existing config let
        - add - update or add new configlet to CVP
        - delete - delete existing configlet

    :param module: Ansible module with parameters and client connection.
    :return: Dict of information to updated results with.

    The configlet will be named as follows:
        If associated with a device the configlet name will be
        device_configletName if configletName has been provided
        otherwise it will be device_template
        if none of the above have been provided it will be configletName
        if that was not provided a default name of Ansible_Test will be used
    '''
    result = dict()
    result['configletAction']=module.params['action']
    changed = False
    configlet_found = False
    existing_config = 'None'
    # Create Configlet Name
    if module.params['device'] != 'None' and module.params['configletName'] != 'None':
        configlet_name = str(module.params['device'])+'_'+str(module.params['configletName'])
    elif module.params['device'] != 'None' and module.params['template'] != 'None':
        configlet_name = str(module.params['device'])+'_'+str(re.split('\.',module.params['template'])[0])
    elif module.params['configletName'] != 'None':
        configlet_name = str(module.params['configletName'])
    else:
        configlet_name = "Ansible_Temp"
    result['configletName'] = configlet_name
    # Find Configlet in CVP if it exists
    configlet_list = module.client.api.get_configlets()['data']
    for configlet in configlet_list:
        if str(configlet['name']) == str(configlet_name):
            configlet_data = module.client.api.get_configlet_by_name(configlet_name)
            existing_config = configlet_data['config']
            configlet_found = True

    # Create New config if required
    if module.params['template'] != 'None' and module.params['data'] != 'None':
        config = config_from_template(module)
    elif module.params['configletConfig'] != 'None':
        config = str(module.params['configletConfig'])
    elif module.params['action'] == 'show':
        config = "! show action - no config required"
    else:
        module.fail_json(msg=str('Config Assignment failed: Missing configletConfig or template'))

    # Return current config if found and action was show
    if module.params['action'] == 'show':
        if configlet_found:
            result['currentConfigBlock'] = existing_config
            result['newConfigBlock'] = "No Config - show only existing"
        else:
            result['currentConfigBlock'] = "No Config - Configlet Not Found"
            result['newConfigBlock'] = "No Config - show only existing"

    # Amend or Create Configlet/Config if action was add
    elif module.params['action'] == 'add':
        if configlet_found:
            result['currentConfigBlock'] = existing_config
            result['newConfigBlock'] = config
            resp = module.client.api.update_configlet(config, configlet_data['key'],
                                                      configlet_data['name'])
            module.client.api.add_note_to_configlet(configlet_data['key'],
                                                    "## Managed by Ansible ##")
            result.update(process_configlet(module, configlet_name))
            changed = True
        else:
            result['currentConfigBlock'] = "New Configlet - No Config to return"
            result['newConfigBlock'] = config
            resp = module.client.api.add_configlet(configlet_name,config)
            module.client.api.add_note_to_configlet(resp,
                                                    "## Managed by Ansible ##")
            result.update(process_configlet(module, configlet_name))
            changed = True

    # Delete Configlet if it exists
    elif module.params['action'] == 'delete':
        if configlet_found:
            result['currentConfigBlock'] = existing_config
            result['newConfigBlock'] = "No Config - Configlet Deleted"
            result.update(process_configlet(module, configlet_name))
            if result['end_container_count'] > 0 or result['end_device_count'] > 0:
                changed = False
                result['newConfigBlock'] = config
            else:
                resp =  module.client.api.delete_configlet(configlet_data['name'], configlet_data['key'])
                changed = True
                result['newConfigBlock'] = "No Config - Configlet Deleted"
        else:
            result['currentConfigBlock'] = "No Config - Configlet Not Found"
            result['newConfigBlock'] = "No Config - Configlet Not Found"
    else:
        result['currentConfigBlock'] = "No Config - Invalid action"
        result['newConfigBlock'] = "No Config - Invalid action"

    # Return Results from operations
    return [changed,result]


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        host=dict(required=True),
        port=dict(type='int', default=None),
        protocol=dict(default='https', choices=['http', 'https']),
        username=dict(required=True),
        password=dict(required=True, no_log=True),
        container=dict(default='None'),
        device=dict(default='None'),
        parent=dict(default='Tenant'),
        configletName=dict(default='None'),
        configletConfig=dict(default='None'),
        template=dict(default='None'),
        data=dict(default='None'),
        action=dict(default='show', choices=['show', 'add', 'delete'])
        )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)
    result = dict(changed=False)
    messages = dict(issues=False)
    module.client = connect(module)
    # Before Starting check for existing tasks

    # Pass config and module params to configlet_action to act on configlet
    result['changed'],result['configlet_data'] = configlet_action(module)

    # Check if the configlet is applied to a device or container
    # Device will take priority of Container
    configlet_type = "None"
    if module.params['device'] != "None":
        device_data = device_info(module)
        if 'warning' not in device_data:
            configletList = []
            for configlet in device_data['configlets']:
                configletList.append(configlet['name'])
            for configlet in device_data['configlets']:
                # Check if Configlet is applied to Device
                if configlet['name'] == result['configlet_data']['configletName']:
                    configlet_type = "device"
    if module.params['container'] != "None" and module.params['device'] == "None":
        container_data = container_info(module)
        if 'warning' not in container_data:
            configletList = []
            for configlet in container_data['configlets']['configletList']:
                configletList.append(configlet['name'])
            for configlet in container_data['configlets']['configletList']:
                # Check if Configlet is applied to Container
                if configlet['name'] == result['configlet_data']['configletName']:
                    configlet_type = "container"
    result['configlet_data']['configletType'] = configlet_type

    module.exit_json(**result)


if __name__ == '__main__':
    main()
