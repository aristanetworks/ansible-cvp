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
module: cv_image
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
short_description: Create or Update CloudVision Portal Devices.
description:
  -  CloudVison Portal Device configuration requires the device name,
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
    description: CVP device to add/delete the image to/from
    required: false
    default: None
  container:
    description: CVP container to add/delete image to/from 
    required: false
    default: 'Tenat'
  image:
      description: Image to apply/remove or show information about
      required: false
      default: None
  action:
    description: action to carry out on the image
                  add- place an Image in a container or device, device takes precedence
                  delete- remove an Image from a container or device
                  show- return the current Image data if available or show image
                  associated with a device or container
    required: true
    choices: 
      - 'show'
      - 'add'
      - 'delete'
    default: show
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
        device_info['Error']="Device with name '%s' does not exist." % module.params['device']
    else:
        device_info.update(module.client.api.get_net_element_info_by_device_id(device_info['systemMacAddress']))
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
        container_info['Error'] = "Container with name '%s' does not exist." % module.params['container']
    else:
        container_info['configlets'] = module.client.api.get_configlets_by_container_id(container_info['key'])
        container_info.update(module.client.api.get_container_by_id(container_info['key']))
    return container_info

def image_info(module,image):
    ''' Get dictionary of image info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of Image info from CVP or exit with failure if no
             info for device is found.
    '''
    image_info = module.client.api.get_image_bundle_by_name(image)
    if image_info == None:
        image_info = {}
        image_info['Error'] = "Image with name '%s' does not exist." %image
    return image_info

def image_action(module):
    ''' Act upon specified Image bundle based on options provided.
        - show - display contents of existing Image Bundle
        - add - update or add an existing Image Bundle to a device or Container
        - delete - delete existing an existing Image Bundle from a device or Container

    :param module: Ansible module with parameters and client connection.
    :return: Dict of information to updated results with.
    '''
    result = {'changed':False,'data':{}}    
    if module.params['image'] != 'None' or module.params['action'] == 'show':
        if module.params['image'] != 'None':
            image_details = image_info(module,module.params['image'])
            if 'error' in str(image_details).lower():
                module.fail_json(msg=str('Image %s cannot be found or has errors: %s'
                                         %(module.params['image'],image_details)))
        if module.params['action'] == 'show':
            image_details = {}
            if module.params['image'] != 'None':
                result['data'] = image_details
            elif module.params['device'] != 'None':
                device_data = device_info(module)
                if device_data['parentContainerKey'] != "undefined_container":
                    if 'bundleName' in device_data:
                        image_name = device_data['bundleName']
                        if image_name != None:
                            image_details = image_info(module,image_name)
                    if "error" in str(device_data).lower():
                        module.fail_json(msg=str('Device %s cannot be found or has errors: %s'
                                                 %(module.params['device'],device_data)))
                else:
                    module.fail_json(msg="warning: Device %s in Undefined Container" %module.params['device'])
            elif module.params['container'] != 'None':
                container_data = container_info(module)
                if 'bundleName' in str(container_data):
                    image_name = container_data['bundleName']
                    if image_name != None:
                        image_details = image_info(module,image_name)
                if "error" in str(container_data).lower():
                    module.fail_json(msg=str('Container %s cannot be found or has errors: %s'
                                             %(module.params['container'],container_data)))
            else:
                module.fail_json(msg="No Image,Container, or Device specified")
            if 'error' not in str(image_details).lower():
                result['data'] = image_details
        elif module.params['device'] != 'None':
            device_data = device_info(module)
            if "error" not in str(device_data).lower():
                if device_data['parentContainerKey'] != "undefined_container":
                    if module.params['action'] == 'add':
                        device_image = module.client.api.apply_image_to_device(image_details,device_data)
                        if device_image['data']['status']=="success":
                            result['changed']=True
                        result['data']=device_image['data']
                    elif module.params['action'] == 'delete':
                        device_image = module.client.api.remove_image_from_device(image_details,device_info(module))
                        if device_image['data']['status']=="success":
                            result['changed']=True
                        result['data']=device_image['data']
                    else:
                        module.fail_json(msg=str("Error: Invalid Option: %s" %module.params['action']))
                else:
                    module.fail_json(msg="warning: Device %s in Undefined Container" %module.params['device'])
            else:
                module.fail_json(msg=str('Device %s cannot be found or has errors: %s'
                                         %(module.params['device'],device_data)))
        elif module.params['container'] != 'None':
            container_data = container_info(module)
            if "error" not in str(container_data).lower():
                if module.params['action'] == 'add':
                    container_image = module.client.api.apply_image_to_container(image_details,container_data)
                    if container_image['data']['status']=="success":
                        result['changed']=True
                    result['data']=container_image['data']
                elif module.params['action'] == 'delete':
                    container_image = module.client.api.remove_image_from_container(image_details,container_data)
                    if container_image['data']['status']=="success":
                        result['changed']=True
                    result['data']=container_image['data']
                else:
                    module.fail_json(msg=str("Error: Invalid Option: %s" %module.params['action']))
            else:
                module.fail_json(msg=str('Container %s cannot be found or has errors: %s'
                                         %(module.params['container'],container_data)))
        else:
            module.fail_json(msg="Error no Device or Module Specified")
    else:
        module.fail_json(msg="Error no Image specified")
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
        image=dict(default='None'),
        container=dict(default='None'),
        device=dict(default='None'),
        action=dict(default='show', choices=['add','delete','show'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    result = dict(changed=False)

    module.client = connect(module)

    try:
        changed = image_action(module)
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
        result['data'] = changed['data']

    module.exit_json(**result)


if __name__ == '__main__':
    main()
