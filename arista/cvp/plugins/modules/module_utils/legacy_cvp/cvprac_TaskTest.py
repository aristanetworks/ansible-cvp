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

import re
import time
from ansible.module_utils.basic import AnsibleModule
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError, CvpApiError
import argparse
import json

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

def task_info(module):
    ''' Get dictionary of task info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of task info from CVP or exit with failure if no
             info for tasks is found.
    '''
    if module['params']['taskID'] == "all":
        ## Debug Line ##
        print "   Fetch all Tasks"
        ## Debug Line ##
        task_info = module['client'].api.get_tasks()
    else:
        ## Debug Line ##
        print "   Fetch Task %s" %module['params']['taskID']
        ## Debug Line ##
        task_data = module['client'].api.get_task_by_id(module['params']['taskID'])
        if task_data == None:
            task_info = {'total':0,'data':[task_data]}
            ## Debug Line ##
            print"   Debug - Task with name '%s' does not exist." % module['params']['taskID']
            ## Debug Line ##
        else:
            task_info = {'total':1,'data':[task_data]}
    return task_info

def process_task(module):
    '''Ensure task(s) exists then process
       add - execute the task(s) required
       delete - cancel the task(s) required
       show - show current task(s)'''
    result={'changed':False,'data':{}}
    # Check that tasks exist in CVP
    taskData = False
    taskData = task_info(module)
    taskResult = []
    if "error" not in taskData.keys():
        if module['params']['action'] == "show":
            result['data'] = taskData['data']
        elif module['params']['action'] == "add":
            if taskData['data'] == [None]:
                result['data']={'changed':False,'data':taskData,'response':'nothing found'}
            elif len (taskData['data']) == 1:
                task = taskData['data'][0]
                if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                    ## Debug Line ##
                    print'Debug - Executing task: %s - %s' %(task['workOrderId'],task['description'])
                    ## Debug Line ##
                    module['client'].api.add_note_to_task(task['workOrderId'], "Executed by Ansible")
                    taskResponse = module['client'].api.execute_task(task['workOrderId'])
                    if "errorMessage" in str(taskResponse):
                        result['data']={'changed':False,'data':task,'response':taskResponse['errorMessage']}
                    else:
                        result['data']={'changed':True,'data':task,'response':taskResponse['data']}
                        result['changed']=True
                    ## Debug Line ##
                    print'Add task: %s - %s' %(task['workOrderId'],taskResponse)
                    ## Debug Line ##
                else:
                    result['data']={'changed':False,'data':task,'response':'invalid task status'}
            else:
                for task in taskData['data']:
                    if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                        ## Debug Line ##
                        print'Debug - Executing task: %s - %s' %(task['workOrderId'],task['description'])
                        ## Debug Line ##
                        module['client'].api.add_note_to_task(task['workOrderId'], "Executed by Ansible")
                        taskResponse = module['client'].api.execute_task(task['workOrderId'])
                        if "errorMessage" in str(taskResponse):
                            taskResult.append({'changed':False,'data':task,'response':taskResponse['errorMessage']})
                        else:
                            taskResult.append({'changed':True,'data':task,'response':taskResponse['data']})
                            result['changed']=True
                        ## Debug Line ##
                        print'Add task: %s - %s' %(task['workOrderId'],taskResponse)
                        ## Debug Line ##
                result['data']=taskResult
        elif module['params']['action'] == "delete":
            if taskData['data'] == [None]:
                result['data']={'changed':False,'data':taskData,'response':'nothing found'}
            elif len (taskData['data']) == 1:
                task = taskData['data'][0]
                if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                    ## Debug Line ##
                    print'Debug - Canceling task: %s - %s' %(task['workOrderId'],task['description'])
                    ## Debug Line ##
                    module['client'].api.add_note_to_task(task['workOrderId'], "Deleted by Ansible")
                    taskResponse = module['client'].api.cancel_task(task['workOrderId'])
                    if "errorMessage" in str(taskResponse):
                        result['data']={'changed':False,'data':task,'response':taskResponse['errorMessage']}
                    else:
                        result['data']={'changed':True,'data':task,'response':taskResponse['data']}
                        result['changed']=True
                    ## Debug Line ##
                    print'Delete task: %s - %s' %(task['workOrderId'],taskResponse)
                    ## Debug Line ##
                else:
                    result['data']={'changed':False,'data':task,'response':'invalid task status'}
            else:
                for task in taskData['data']:
                    if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                        ## Debug Line ##
                        print'Debug - Canceling task: %s - %s' %(task['workOrderId'],task['description'])
                        ## Debug Line ##
                        module['client'].api.add_note_to_task(task['workOrderId'], "Deleted by Ansible")
                        taskResponse = module['client'].api.execute_task(task['workOrderId'])
                        if "errorMessage" in str(taskResponse):
                            taskResult.append({'changed':False,'data':task,'response':taskResponse['errorMessage']})
                        else:
                            taskResult.append({'changed':True,'data':task,'response':taskResponse['data']})
                            result['changed']=True
                        ## Debug Line ##
                        print'Delete task: %s - %s' %(task['workOrderId'],taskResponse)
                        ## Debug Line ##
                result['data']=taskResult
        else:
            ## Debug Line ##
            print'Debug - invalid action: %r' %module['params']['action']
            ## Debug Line ##
    else:
      errorOutput = 'No Task Found: %s' %module['params']['taskID']
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
    parser.add_argument("--taskID",default='all', help='Task ID or "all" for complete list')
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

    # Pass module params to process_device to act on device
    print "### Processing Task ###"
    result = process_task(module)

    # Check Results of device_action and act accordingly
    if result['changed']:
        pass

    print "\nModule Result:"
    pp4.pprint(result)
    print "\nModule Data:"
    pp4.pprint(module)


if __name__ == '__main__':
    main()
