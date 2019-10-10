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

from cv_client import CvpClient
from cv_client_errors import CvpLoginError, CvpApiError
import yaml
import argparse
import json
import os
import inspect
import difflib
from fuzzywuzzy import fuzz # Library that uses Levenshtein Distance to calculate the differences between strings.
from time import sleep

# Disable HTTPS Insecure Cert Warnings
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Setting up some formated print outputs
import pprint
pp2 = pprint.PrettyPrinter(indent=2)
pp6 = pprint.PrettyPrinter(indent=6)    

def connect(module):
    ''' Connects to CVP device using user provided credentials from module.
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

def compare(fromText, toText, lines=10):
    """ Compare text string in 'fromText' with 'toText' and produce
        diffRatio - a score as a float in the range [0, 1] 2.0*M / T
          T is the total number of elements in both sequences,
          M is the number of matches.
          Score - 1.0 if the sequences are identical, and 0.0 if they have nothing in common.
        unified diff list
          Code	Meaning
          '- '	line unique to sequence 1
          '+ '	line unique to sequence 2
          '  '	line common to both sequences
          '? '	line not present in either input sequence
    """
    fromlines = fromText.splitlines(1)
    tolines = toText.splitlines(1)
    diff = list(difflib.unified_diff(fromlines, tolines,n=lines))
    textComp = difflib.SequenceMatcher(None, fromText, toText)
    diffRatio = round( textComp.quick_ratio()*100, 2)
    return [diffRatio,diff]

def cv_facts(module):
    ''' Connects to CVP device using user provided credentials from module.
    :param module: Ansible module with parameters and client connection.
    :return: CvpClient object with connection instantiated.
    '''
    facts = {}
    # Build required data for devices in CVP - Device Data, Config, Associated Container,
    # Associated Images, and Associated Configlets
    deviceField = {'hostname':'name','fqdn':'fqdn','complianceCode':'complianceCode',
                   'complianceIndication':'complianceIndication','version':'version',
                   'systemMacAddress':'systemMacAddress','systemMacAddress':'key',
                   'parentContainerKey':'parentContainerKey'}
    facts['devices'] = []

    # Get Inventory Data for All Devices
    inventory = module['client'].api.get_inventory()
    # Reduce device data to required fields
    for device in inventory:
        deviceFacts = {}
        for field in device.keys():
            if field in deviceField:
                deviceFacts[deviceField[field]] = device[field]
        facts['devices'].append(deviceFacts)
    
    # Work through Devices list adding device specific information 
    for device in facts['devices']:
        # Add designed config for device
        device['config'] = module['client'].api.get_device_configuration(device['key'])
        # Add parent container name
        container = module['client'].api.get_container_by_id(device['parentContainerKey'])
        device['parentContainerName']=container['name']
        # Add Device Specific Configlets
        configlets = module['client'].api.get_configlets_by_device_id(device['key'])
        device['deviceSpecificConfiglets'] = []
        for configlet in configlets:
            if int(configlet['containerCount']) == 0:
                device['deviceSpecificConfiglets'].append(configlet['name'])
        # Add ImageBundle Info
        device['imageBundle'] = ""
        deviceInfo = module['client'].api.get_net_element_info_by_device_id(device['key'])
        if "imageBundleMapper" in deviceInfo:
            # There should only be one ImageBudle but its id is not decernable
            # If the Image is applied directly to the device its type will be 'netelement'
            if len(deviceInfo['imageBundleMapper'].values()) > 0:
                if deviceInfo['imageBundleMapper'].values()[0]['type'] == 'netelement':
                    device['imageBundle'] = deviceInfo['bundleName']               

    # Build required data for configlets in CVP - Configlet Name, Config, Associated Containers,
    # Associated Devices, and Configlet Type
    configletField = {'name':'name','config':'config','type':'type','key':'key'}
    facts['configlets']=[]
    
    # Get List of all configlets
    configlets = module['client'].api.get_configlets()['data']
    # Reduce configlet data to required fields
    for configlet in configlets:
        configletFacts = {}
        for field in configlet.keys():
            if field in configletField:
                configletFacts[configletField[field]]=configlet[field]
        facts['configlets'].append(configletFacts)
    
    # Work through Configlet list adding Configlet specific information
    for configlet in facts['configlets']:
        # Add applied Devices
        configlet['devices'] = []
        applied_devices = module['client'].api.get_devices_by_configlet(configlet['name'])
        for device in applied_devices['data']:
            configlet['devices'].append(device['hostName'])
        # Add applied Containers
        configlet['containers'] = []
        applied_containers = module['client'].api.get_containers_by_configlet(configlet['name'])
        for container in applied_containers['data']:
            configlet['containers'].append(container['containerName'])

    # Build required data for containers in CVP - Container Name, parent container, Associated Configlets
    # Associated Devices, and Child Containers
    containerField = {'name':'name','parentName':'parentName','childContainerId':'childContainerKey',
                      'key':'key'}
    facts['containers'] = []

    # Get List of all Containers
    containers = module['client'].api.get_containers()['data']
    # Reduce container data to required fields
    for container in containers:
        containerFacts ={}
        for field in container.keys():
            if field in containerField:
                containerFacts[containerField[field]]=container[field]
        facts['containers'].append(containerFacts)

    # Work through Container list adding Container specific information
    for container in facts['containers']:
        # Add applied Devices
        container['devices'] = []
        applied_devices = module['client'].api.get_devices_by_container_id(container['key'])
        for device in applied_devices:
            container['devices'].append(device['fqdn'])
        # Add applied Configlets
        container['configlets'] = []
        applied_configlets = module['client'].api.get_configlets_by_container_id(container['key'])['configletList']
        for device in applied_devices:
            container['configlets'].append(configlet['name'])
        # Add applied Images
        container['imageBundle'] = ""
        applied_images = module['client'].api.get_image_bundle_by_container_id(container['key'])['imageBundleList']
        if len(applied_images) > 0:
            container['imageBundle'] = applied_images[0]['name']

    # Build required data for images in CVP - Image Name, certified, Image Components
    imageField = {'name':'name','isCertifiedImageBundle':'certifified','imageIds':'imageNames','key':'key'}
    facts['imageBundles'] = []
    
    # Get List of all Image Bundles
    imageBundles = module['client'].api.get_image_bundles()['data']
    # Reduce image data to required fields
    for imageBundle in imageBundles:
        imageBundleFacts = {}
        for field in imageBundle.keys():
            if field in imageField:
                imageBundleFacts[imageField[field]] = imageBundle[field]
        facts['imageBundles'].append(imageBundleFacts)
    
    # Build required data for tasks in CVP - work order Id, current task status, name
    # description
    tasksField = {'name':'name','workOrderId':'taskNo','workOrderState':'status',
                  'currentTaskName':'currentAction','description':'description',
                  'workOrderUserDefinedStatus':'displayedStutus','note':'note',
                  'taskStatus':'actionStatus'}
    facts['tasks'] = []

    # Get List of all Tasks
    tasks = module['client'].api.get_tasks()['data']
    # Reduce task data to required fields
    for task in tasks:
        taskFacts= {}
        for field in task.keys():
            if field in tasksField:
                taskFacts[tasksField[field]] = task[field]
        facts['tasks'].append(taskFacts)
    
    return facts

def configlet_action(module):
    ''' Compare configlets in "configlets" with configlets in "cvp_facts"
    if configlet exists in "cvp_facts" check config, if changed update
    if configlet does not exist in "cvp_facts" add to CVP
    if configlet in "cvp_facts" but not in "configlets" remove from CVP if
    not applied to a device or container.
    :param module: Ansible module with parameters and client connection.
    :return: data: dict of module actions and taskIDs
    '''
    # If any configlet changed updated 'changed' flag
    changed = False
    #Compare configlets against cvp_facts-configlets
    keep_configlet = [] # configlets with no changes
    delete_configlet = [] # configlets to delete from CVP
    deleted = []
    update_configlet = [] # configlets with config changes
    updated = []
    new_configlet = [] # configlets to add to CVP
    new = []
    taskList = [] # Tasks that have a pending status after function runs

    for configlet in module['params']['cvp_facts']['configlets']:
        # Only deal with Static configlets not Configletbuilders or
        # thier derived configlets
        if configlet['type'] == 'Static':
            if configlet['name'] in module['params']['configlets']:
                ansible_configlet = module['params']['configlets'][configlet['name']]
                configlet_compare = compare(configlet['config'],ansible_configlet)
                # compare function returns a floating point number
                if configlet_compare[0] == 100.0:
                    keep_configlet.append(configlet)
                else:
                    update_configlet.append({'data':configlet,'config':ansible_configlet})
            else:
                delete_configlet.append(configlet)
    for ansible_configlet in module['params']['configlets']:
        found = False
        for cvp_configlet in module['params']['cvp_facts']['configlets']:
            if str(ansible_configlet) == str(cvp_configlet['name']):
                found = True
        if not found:
            new_configlet.append({'name':str(ansible_configlet),'config':ansible_configlet})

    # delete any configlets as required
    if not module['check_mode']:
        if len(delete_configlet) > 0:
            for configlet in delete_configlet:
                delete_resp =  module['client'].api.delete_configlet(configlet['name'], configlet['key'])
                if "errorMessage" in str(delete_resp):
                    message = "Configlet %s cannot be delete - %s"%(configlet['name'],delete_resp['errorMessage'])
                    module.warn.add(message)
                    deleted.append({configlet['name']:message})
                else:
                    changed = True
                    deleted.append({configlet['name']:"success"})

        # Update any configlets as required
        if len(update_configlet) > 0:
            for configlet in update_configlet:
                update_resp = module['client'].api.update_configlet(configlet['config'],
                                                                    configlet['data']['key'],
                                                                    configlet['data']['name'])
                if "errorMessage" in str(update_resp):
                    message = "Configlet %s cannot be updated - %s"%(configlet['name'],update_resp['errorMessage'])
                    module.warn.add(message)
                    updated.append({configlet['data']['name']:message})
                else:
                    module['client'].api.add_note_to_configlet(configlet['data']['key'],
                                                           "## Managed by Ansible ##")
                    changed = True
                    updated.append({configlet['data']['name']:"success"})
                    
        # Add any new configlets as required
        if len(new_configlet) > 0:
            for configlet in new_configlet:
                new_resp = module['client'].api.add_configlet(configlet['name'],configlet['config'])
                if "errorMessage" in str(new_resp):
                    message = "Configlet %s cannot be created - %s"%(configlet['name'],new_resp['errorMessage'])
                    module.warn.add(message)
                    new.append({configlet['name']:message})
                else:
                    module['client'].api.add_note_to_configlet(new_resp,
                                                           "## Managed by Ansible ##")
                    changed = True
                    new.append({configlet['name']:"success"})

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
            tasks = module['client'].api.get_tasks_by_status('Pending')
            # Reduce task data to required fields
            for task in tasks:
                taskFacts= {}
                for field in task.keys():
                    if field in tasksField:
                        taskFacts[tasksField[field]] = task[field]
                taskList.append(taskFacts)
        data = {'new':new,'updated':updated,'deleted':deleted,'tasks':taskList}
    else:
        for configlet in new_configlet:
            new.append({configlet['name']:"checked"})
        for configlet in update_configlet:
            updated.append({configlet['data']['name']:"checked"})
        for configlet in delete_configlet:
            deleted.append({configlet['name']:"checked"})
        data = {'new':new,'updated':updated,'deleted':deleted,'tasks':taskList}
    return [changed,data]

def display_facts(module):
    ''' Displays the contents of the cvp_facts inside module
    used as a quick check to ensure API and calls are working correctly
    '''
    print "\n   Devices:"
    for device in module['params']['cvp_facts']['devices']:
        print "\n   Device Name - %s" %device['name']
        print "      Parent Container - %s" %device['parentContainerName']
        print "      Configlets -"
        for configlet in device['deviceSpecificConfiglets']:
            print "         %s" %configlet
        print "      Image Bundle - %s" %device['imageBundle']
    print "\n   Configlets:"
    for configlet in module['params']['cvp_facts']['configlets']:
        print "\n      Configlet Name: %s" %configlet['name']
        print "         Devices -"
        for device in configlet['devices']:
            print "            %s" %device
        print "         Containers -"
        for container in configlet['containers']:
            print "            %s" %container
    print "\n\n   Containers:"
    for container in module['params']['cvp_facts']['containers']:
        print "\n      Container Name: %s" %container['name']
        print "         Devices -"
        for device in container['devices']:
            print "            %s" %device
        print "         Configlets -"
        for configlet in container['configlets']:
            print "            %s" %configlet
        print "         Images - %s" %container['imageBundle']
    print "\n\n   Images:"
    for imageBundle in module['params']['cvp_facts']['imageBundles']:
        print "\n      Image Name: %s" %imageBundle['name']
        print "         Images -"
        for image in imageBundle['imageNames']:
            print "            %s" %image
    print "\n\n   Tasks:"
    for task in module['params']['cvp_facts']['tasks']:
        print"      %s - %s" %(task['taskNo'], task['description'])

def save_facts(module):
    ''' Saves the contents of the cvp_facts inside module as JSON files
    used as a quick method to generate input data'''

    configlets = {}
    for configlet in module['params']['cvp_facts']['configlets']:
        configlets[configlet['name']] = configlet['config']
    fileWrite("./inputConfiglets.json",configlets,'json','w')
    fileWrite("./cvpConfiglets.json",
              module['params']['cvp_facts']['configlets'],
              'json','w')
    fileWrite("./cvpDevices.json",
              module['params']['cvp_facts']['devices'],
              'json','w')
    fileWrite("./cvpContainers.json",
              module['params']['cvp_facts']['containers'],
              'json','w')
    fileWrite("./cvpImages.json",
              module['params']['cvp_facts']['imageBundles'],
              'json','w')
    fileWrite("./cvpTasks.json",
              module['params']['cvp_facts']['tasks'],
              'json','w')

class textLogger(object):
    """ Message Logging function, takes latest message and appends it to message list"""

    def __init__(self):
        self.warnings = []

    def add(self,text):
        self.warnings.append(text)

def fileWrite(filePath,data,fileType,option="c"):
    """ filePath - full directory and filename for file
        Function returns True is file is successfully written to media
        data - content to write to file
        fileType
          json - JSON object
          txt - text string
        option
          a - append
          w - overwrtite
          c - choose option based on file existance
        """
    if option.lower() == "c":
        if os.path.exists(filePath) and os.path.getsize(filePath) > 0:
            print "Appending data to file:%s" %filePath
            fileOp = "a"
        else:
            print "Creating file %s to write data to" %filePath
            fileOp = "w"
    else:
        fileOp = option.lower()
    try:
        with open(filePath, fileOp) as FH:
            if fileOp == "a":
                FH.seek(0, 2)
            if fileType.lower() == "json":
                #json.dump(json.loads(data), FH, sort_keys = True, indent = 4, ensure_ascii = True)
                json.dump(data, FH, sort_keys = True, indent = 4, ensure_ascii = True)
                result = True
            elif fileType.lower() == "txt":
                FH.writelines(data)
                result = True
            elif fileType.lower() == "yaml":
                yaml.dump(data,FH)
                result = True
            else:
                print "Invalid fileType"
                result = False
    except IOError as file_error:
        print "File Write Error: %s"%file_error
        result = False
    return result

def fileOpen(filePath,fileType):
    """ filePath - full directory and filename for file
        function returns file contents based on selection
        json - JSON object
        txt - text string
        j2 - Jinja2 Template object"""
    if os.path.exists(filePath) and os.path.getsize(filePath) > 0:
        print "Retrieving file:%s" %filePath
        with open(filePath, 'r') as FH:
            if fileType.lower() == "json":
                fileObject = json.load(FH)  
            elif fileType.lower() == "txt":
                fileObject = FH.readlines()
            elif fileType.lower() == "j2":
                fileObject = Template(FH.read())
            elif fileType.lower() == "yaml":
                fileObject = yaml.load(FH, Loader=yaml.FullLoader)
            else:
                print "Invalid fileType"
                fileObject = False
        return fileObject
    else:
        print "File does not exist or is empty: %s" %filePath
        return False


def parseArgs():
    """Gathers comand line options for the script, generates help text and performs some error checking"""
    usage = "usage: %prog [options]"
    parser = argparse.ArgumentParser(description="Test cv_client functionality")
    parser.add_argument("--username",required=True, help='Username to log into CVP')
    parser.add_argument("--password",required=True, help='Password for CVP user to login')
    parser.add_argument("--host",required=True, help='CVP Host IP or Name')
    parser.add_argument("--protocol", default='HTTPS', help='HTTP or HTTPs')
    parser.add_argument("--port", default=443 ,help='TCP port Number default 443')
    parser.add_argument("--configlets", default=[], type=list, help='List of CVP configlets, full list required')
    parser.add_argument("--check_mode", default=False, help='True/False - Test mode No changes applied')
    args = parser.parse_args()
    return (args)
    

def main():
    """ main entry point for module execution
    """
    # Create dictionary of input parameters
    module = {}
    module['warn'] = textLogger()
    module['warn'].add("Start Logging")
    module['params'] = vars(parseArgs())
    if "false" in str(module['params']['check_mode']).lower():
        module['params']['check_mode'] = False
    else:
        module['params']['check_mode'] = True
    try:
        module['check_mode'] = module['params'].pop('check_mode')
    except KeyError:
        print "check_mode not found"
    else:
        print"### check_mode: %s ###" %module['check_mode']
    # Check Connectivity to CVP
    print "### Connecting to CVP ###"
    module['client'] = connect(module)
    print "Checking Api version required: %s" %module['client'].apiVersion
    print "Checking CVP version: %s" %module['client'].api.get_cvp_info()
    print "Checking CVP facts:"
    module['params']['cvp_facts'] = cv_facts(module)

    # Output cvp_facts for sanity check
    #display_facts(module)
    # Save cvp_facts for later use
    #save_facts(module)

    # Create configlet entity
    configlets = {}
    # Load Configlets test data
    module['params']['configlets'] = fileOpen('./inputConfiglets.json','json')

    # Pass cvp_facts and configlet information to configlet_action
    # Review Results
    configlets = configlet_action(module)
    print"Modify Configlets"
    print"   change: %s" %configlets[0]
    for action in configlets[1]:
        print "   Action: %s" %action
        for actionItem in configlets[1][action]:
            print"      %s" %actionItem
    print "\nWarnings:"
    for entry in module['warn'].warnings:
        print "      %s" %entry
    

if __name__ == '__main__':
    main()
