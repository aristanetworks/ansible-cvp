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
import time
from jinja2 import meta
import jinja2
import yaml
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError
import argparse
import json

# Checking some Enviromental Variables
#import sys
#print '\n'.join(sys.path)
import imp
print "cvprac is here %s" %str(imp.find_module('cvprac'))

# Setting up some formated print outputs
import pprint
pp2 = pprint.PrettyPrinter(indent=2)
pp4 = pprint.PrettyPrinter(indent=4)

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
        device_info['warning']="Device with name '%s' does not exist." % module['params']['device']
    else:
        device_info['configlets'] = module['client'].api.get_configlets_by_netelement_id(device_info['systemMacAddress'])['configletList']
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
        container_info['warning'] = "Container with name '%s' does not exist." % module['params']['container']
    else:
        container_info['configlets'] = module['client'].api.get_configlets_by_container_id(container_info['key'])
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
    devices = module['client'].api.get_inventory()
    deviceData = False
    reconcile = False
    for device in devices:
      if module['params']['device'] in device['fqdn']:
        deviceData = device
        deviceData['parentContainer'] = module['client'].api.get_container_by_id(device['parentContainerKey'])
        # Debug Print
        print "## Debug: Parent Container - %s ##" %deviceData['parentContainer']
    if deviceData:
        # Collect Required Configlets to apply to device
        if module['params']['configlet'] != 'None':
            configletData = []
            for configlet in module['params']['configlet']:
                temp_configlet = module['client'].api.get_configlet_by_name(configlet)
                # Add configlet to list if there are no errors
                if "error" not in str(temp_configlet):
                    configletData.append(temp_configlet)
                else:
                    print'Fetch Configlet details %s failed: %s'%(configlet, temp_configlet)
        else:
            configletData = "None"
        # Debug Print
        print "## Debug ConfigletData: %r" %configletData
        # Used for existing config on a valid device
        existing_config = 'None'
        # Work out where switch is in provisoning hierachy and act accordingly
        # New device found in ZTP mode
        if deviceData['parentContainerKey'] == "undefined_container":
            # Debug Print
            print "## Debug: New Device ##"
            # New Device found with existing config (not ZTP boot mode)
            if deviceData['ztpMode'] == False:
                existing_config = module['client'].api.get_device_configuration(deviceData['systemMacAddress'])
            if module['params']['action'] == "add":
                device_action = module['client'].api.deploy_device(deviceData,
                                                                module['params']['container'],
                                                                configletData,
                                                                module['params']['image'])
                if "error" not in device_action:
                    result['changed'] = True
                    reconcile = True
                    result['data']=device_action['data']
                    result['config']['current'] = existing_config
                else:
                    result['data']=device_action
            elif module['params']['action'] == "delete":
                result['data'] = ["Error: Device in Undefined Container",deviceData]
                print'Delete Device %s failed: Device In Undefined'%deviceData['fqdn']
            elif module['params']['action'] == "show":
                result['data'] = deviceData
                result['config']['current']=existing_config
                reconcile = True
            else:
                result['data'] = {"error":"Unsupported Option"}
        # Existing Device Found
        elif deviceData['parentContainerKey'] != 'undefined_container':
            # Debug Print
            print "## Debug: Existing Device ##"
            print "## Parent Container: %s ##" %deviceData['parentContainer']['name']
            print "## Target Container: %s ##" %module['params']['container']
            existing_config = module['client'].api.get_device_configuration(deviceData['systemMacAddress'])
            if module['params']['action'] == "add":
                # Add device to container
                target_container = module['client'].api.get_container_by_name(module['params']['container'])
                print "## Debug Container Data - %r" %target_container
                if ("error" not in str(target_container)) and ("None" not in str(target_container)):
                    print "## Debug Moving Existing Device"
                    device_action = module['client'].api.move_device_to_container("Ansible", deviceData,
                                                             target_container,
                                                             create_task=True)
                    
                    if "error" not in device_action:
                        print "## Debug Deivce Moved"
                        result['changed']= True
                        reconcile = True
                        result['data']=device_action['data']
                        result['config']['current'] = existing_config
                    else:
                        print "## Debug - %r" %device_action
                        result['data']=device_action
                    # Add Configlets to device
                    if configletData != 'None':
                        device_addConfiglets = module['client'].api.apply_configlets_to_device("Ansible",
                                                                                               deviceData,
                                                                                               configletData,
                                                                                               create_task=True)
                        if "error" not in device_addConfiglets:
                            # Debug Print
                            print "## Debug device_addConfiglets: %r" %device_addConfiglets
                            print "## Debug Deivce Configlets Added"
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
                            print "## Debug - %r" %device_addConfiglets
                            result['data'].update(device_addConfiglets)
                else:
                    print "## Debug - %r" %target_container
                    result['data']=target_container
                    result['config']['current'] = existing_config
            elif module['params']['action'] == "delete":
                # Check Container remove configlets and / or remove device from container
                # if container is CVP remove from CVP, if container is Device Parent factory reset device
                if module['params']['container'] == "CVP":
                    # Debug Print
                    print "## Debug: Existing Device - Action Delete/Remove from CVP ##"
                    device_action = module['client'].api.delete_device(deviceData['systemMacAddress'])
                    if "error" not in str(device_action).lower():
                        result['changed']= True
                        result['data']=device_action['data']
                        result['config']['current'] = existing_config
                    else:
                        result['data']=device_action
                elif module['params']['container'] == "RESET":
                    # Debug Print
                    print "## Debug: Existing Device - Action Delete/Reset ##"
                    device_action = module['client'].api.reset_device("Ansible",deviceData)
                    if "error" not in str(device_action).lower():
                        result['changed'] = False
                        result['data'] = device_action['data']
                        result['config']['current'] = existing_config
                elif module['params']['container'] == deviceData['parentContainer']['name']:
                    # Debug Print
                    print "## Debug: Existing Device - Action Delete Configlets ##"
                    if configletData != 'None':
                        device_action = module['client'].api.remove_configlets_from_device("Ansible",deviceData,
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
                    print 'Delete Device %s failed: Device in %s'%(deviceData['fqdn'],deviceData['parentContainer']['name'])
            elif module['params']['action'] == "show":
                reconcile = True
                result['data'] = deviceData
                result['config']['current']=existing_config
            else:
                errorOutput = 'Invalid Option: %s'%module['params']['action']
                result['data'] = {'error':errorOutput}
        if reconcile:
            temp_reconcile = module['client'].api.get_device_reconcile_config(deviceData['systemMacAddress'])
            if "config" in temp_reconcile:
                result['config']['reconcile'] = temp_reconcile['config']
            else:
                result['config']['reconcile'] = temp_reconcile
        else:
            result['config']['reconcile'] = ""
    # No Device Found
    else:
      errorOutput = 'No Device Found: %s' %module['params']['device']
      result['data']={'error':errorOutput}
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
    parser.add_argument("--configlet",default='None', help='Configlet List to apply to Device')
    parser.add_argument("--container",default='Tenant', help='Container with Device in')
    parser.add_argument("--device", default='None', help='Target Device')
    parser.add_argument("--image", default=None, help='Image to apply directly to Device')
    parser.add_argument("--action",required=True, default='show', choices=['show', 'add', 'delete'],help='show,add,delete')
    args = parser.parse_args()
    return (args)


def main():
    """ main entry point for module execution
    """

    module = {}
    #module['params'] = parseArgs()
    module['params'] = vars(parseArgs())
    if "," in module['params']['configlet']:
        module['params']['configlet'] = re.split(',',module['params']['configlet'])
    else:
        module['params']['configlet'] = [module['params']['configlet']]
    result = dict(changed=False)
    print "### Connecting to CVP ###"
    module['client'] = connect(module)

    # Pass module params to process_device to act on device
    print "### Processing Device ###"
    result = process_device(module)

    # Check Results of device_action and act accordingly
    if result['changed']:
        pass

    print "\nModule Result:"
    pp4.pprint(result)
    print "\nModule Data:"
    pp4.pprint(module)


if __name__ == '__main__':
    main()
