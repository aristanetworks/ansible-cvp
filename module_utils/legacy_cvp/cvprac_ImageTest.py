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

import re
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError
import argparse
import json

# Checking some Enviromental Variables
#import sys
#print '\n'.join(sys.path)
#import imp
#print "cvprac is here %s" %str(imp.find_module('cvprac'))


# Disable HTTPS Insecure Cert Warnings
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def connect(module):
    ''' Connects to CVP device using user provided credentials from playbook.
    :param module: Ansible module with parameters and client connection.
    :return: CvpClient object with connection instantiated.
    '''
    client = CvpClient()
    try:
        client.connect([module['params']['host']],
                       module['params']['username'],
                       module['params']['password'],
                       protocol=module['params']['protocol'],
                       port=module['params']['port'],
                       )
    except CvpLoginError, e:
        module['fail']=str(e)
    return client

def device_info(module):
    ''' Get dictionary of device info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of device info from CVP or exit with failure if no
             info for device is found.
    '''
    device_info = module['client'].api.get_device_by_name(module['params']['device'])
    if not device_info:
            devices = module['client'].api.get_inventory()
            for device in devices:
              if module['params']['device'] in device['fqdn']:
                device_info = device
    if not device_info:
        device_info['Error']="Device with name '%s' does not exist." % module['params']['device']
    else:
        device_info.update(module['client'].api.get_net_element_info_by_device_id(device_info['systemMacAddress']))
        device_info['configlets'] = module['client'].api.get_configlets_by_netelement_id(device_info['systemMacAddress'])['configletList']
        device_info['parentContainer'] = module['client'].api.get_container_by_id(device_info['parentContainerKey'])
    return device_info

def container_info(module):
    ''' Get dictionary of container info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of container info from CVP or exit with failure if no
             info for device is found.
    '''
    container_info = module['client'].api.get_container_by_name(module['params']['container'])
    if container_info == None:
        container_info = {}
        container_info['Error'] = "Container with name '%s' does not exist." % module['params']['container']
    else:
        container_info['configlets'] = module['client'].api.get_configlets_by_container_id(container_info['key'])
        container_info.update(module['client'].api.get_container_by_id(container_info['key']))
    return container_info

def image_info(module,image):
    ''' Get dictionary of image info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of Image info from CVP or exit with failure if no
             info for device is found.
    '''
    image_info = module['client'].api.get_image_bundle_by_name(image)
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
    if module['params']['image'] != 'None' or module['params']['action'] == 'show':
        if module['params']['action'] == 'show':
            image_details = {}
            if module['params']['image'] != 'None':
                ## Debug Print
                print "## Debug - Image Show"
                image_details = image_info(module,module['params']['image'])
                if 'error' not in str(image_details).lower():
                    result['data'] = image_details
                else:
                    ## Debug Print
                    print "## Debug - Image_Error: %s" %image_details['Error']
                    result['Error'] = image_details['Error']
            elif module['params']['device'] != 'None':
                ## Debug Print
                print "## Debug - Device Image Show"
                device_data = device_info(module)
                if 'bundleName' in device_data:
                    image_name = device_data['bundleName']
                    ## Debug Print
                    print "Debug - bundleName: %s" %image_name
                    if image_name != None:
                        image_details = image_info(module,image_name)
                else:
                    image_details={"Error":"Show Device Image not supported"}
                    result['Error'] = "Show Device Image not supported"
                if "error" in str(device_data).lower():
                    result['Error'] = device_data['Error']
            elif module['params']['container'] != 'None':
                ## Debug Print
                print "## Debug - Container Image Show"
                container_data = container_info(module)
                print "## Container Key: %s" %container_data['key']
                if 'bundleName' in str(container_data):
                    image_name = container_data['bundleName']
                    print "## Debug Container bundleName: %s" %image_name
                    if image_name != None:
                        image_details = image_info(module,image_name)
                if "error" in str(container_data).lower():
                    result['Error'] = container_data['Error']
            else:
                ## Debug Print
                print "Error: No Imgae Found"
                result['Error']='No Image Found'
            if 'error' not in str(image_details).lower():
                result['data'] = image_details
        elif module['params']['device'] != 'None':
            device_data = device_info(module)
            if device_data['parentContainerKey'] != "undefined_container":
                if module['params']['action'] == 'add':
                    device_image = module['client'].api.apply_image_to_device(image_info(module),device_data)
                    if device_image['data']['status']=="success":
                        result['changed']=True
                    result['data']=device_image['data']
                elif module['params']['action'] == 'delete':
                    device_image = module['client'].api.remove_image_from_device(image_info(module),device_info(module))
                    if device_image['data']['status']=="success":
                        result['changed']=True
                    result['data']=device_image['data']
                else:
                    result['Error']="Warning : Invalid Option: %s" %module['params']['action']
                    ## Debug Print
                    print "Error:Invalid Option: %s" %module['params']['action']
            else:
                result['data']={}
                result['Error']="warning: Device %s in Undefined Container" %module['params']['device']
        elif module['params']['container'] != 'None':
            if module['params']['action'] == 'add':
                container_image = module['client'].api.apply_image_to_container(image_info(module),container_info(module))
                if container_image['data']['status']=="success":
                    result['changed']=True
                result['data']=container_image['data']
            elif module['params']['action'] == 'delete':
                container_image = module['client'].api.remove_image_from_container(image_info(module),container_info(module))
                if container_image['data']['status']=="success":
                    result['changed']=True
                result['data']=container_image['data']
            else:
                result['Error']="warning : Invalid Option: %s" %module['params']['action']
                ## Debug Print
                print "Error:Invalid Option: %s" %module['params']['action']
        else:
            print "Error no Device or Module Specified"
    else:
        print "Error no Image specified"
    return result

def parseArgs():
    """Gathers comand line options for the script, generates help text and performs some error checking"""
    usage = "usage: %prog [options]"
    parser = argparse.ArgumentParser(description="Create a configlet in CVP CVP")
    parser.add_argument("--username",required=True, help='Username to log into CVP')
    parser.add_argument("--password",required=True, help='Password for CVP user to login')
    parser.add_argument("--host",required=True, help='CVP Host IP or Name')
    parser.add_argument("--protocol", default='HTTPS', help='HTTP or HTTPs')
    parser.add_argument("--port", default=443 ,help='TCP port Number default 443')
    parser.add_argument("--image", default='None' ,help='Image Bundle to use')
    parser.add_argument("--container",default='None', help='Container to add configlet to')
    parser.add_argument("--device", default='None', help='Device to add configlet to')
    parser.add_argument("--action",required=True, default='show', choices=['show', 'add', 'delete'],help='show,add,delete')
    args = parser.parse_args()
    return (args)
    

def main():
    """ main entry point for module execution
    """

    module = {}
    #module['params'] = parseArgs()
    module['params'] = vars(parseArgs())
    result = dict(changed=False)
    print "### Connecting to CVP ###"
    module['client'] = connect(module)

    # Pass config and module params to image_action to act on
    print "### Processing Image Bundle ###"
    result = image_action(module)
    # Check if the Image is applied to a device or container
    # Device will take priority of Container
    if result['changed']:
        print "Tasks Created: %s" %result['data']['taskIds']
    elif module['params']['action'] == 'show':
        print "Show Data"
    else:
        print "Image not Applied"

    # Check Results of configlet_action and act accordingly
    print "\nModule Result:"
    print(result)
    print "\nModule Data:"
    print(module)


if __name__ == '__main__':
    main()
