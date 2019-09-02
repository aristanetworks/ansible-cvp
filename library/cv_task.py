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
module: cv_task
version_added: "1.0"
author: "Hugh Adams EMEA AS Team(ha@arista.com)"
short_description: Execute or Cancel CVP Tasks.
description:
  - CloudVison Portal Task execution or cancelation requires taskID
  - add will execute the task with the ID supplied
  - delete will cancel the task with the ID supplied
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
  taskID:
    description: CVP taskID to act on
    required: false
    default: all
  action:
    description: action to carry out on the task
                  add - execute the task with taskID supplied or all pending tasks if no taskID supplied
                  delete - cancel the task with taskID supplied or all pending tasks if no taskID supplied
                  show - return the current status of a task or all tasks if no taskID supplied
    required: true
    choices: 
      - 'show'
      - 'add'
      - 'delete'
    default: show
"""

EXAMPLES="""
# Execute a task
# task must exist and be pending
- name: Execute a task
  tags: execute, show
  cv_device:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    taskID: "{{cvp_taskID}}"
    action: add
    register: cvp_result

# Display information for a task
- name: Show task information from CVP
  tags: show
  cv_device:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    taskID: "{{cvp_taskID}}"
    action: show
    register: cvp_result

- name: Display cv_task add result
  tags: create, show
  debug:
    msg: "{{cvp_result}}"

# Cancel task in CVP
# task must exist and be pending or failed
- name: Cancel a pending task
  tags: cancel
  cv_device:
    host: '{{ansible_host}}'
    username: '{{cvp_username}}'
    password: '{{cvp_password}}'
    protocol: https
    taskID: "{{cvp_taskID}}"
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

def task_info(module):
    ''' Get dictionary of task info from CVP.
    :param module: Ansible module with parameters and client connection.
    :return: Dict of task info from CVP or exit with failure if no
             info for tasks is found.
    '''
    if module.params['taskID'] == "all":
        task_info = module.client.api.get_tasks()
    else:
        task_data = module.client.api.get_task_by_id(module.params['taskID'])
        if task_data == None:
            task_info = {'total':0,'data':[task_data]}
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
        if module.params['action'] == "show":
            result['data'] = taskData['data']
        elif module.params['action'] == "add":
            if taskData['data'] == [None]:
                result['data']={'changed':False,'data':taskData,'response':'nothing found'}
            elif len (taskData['data']) == 1:
                task = taskData['data'][0]
                if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                    module.client.api.add_note_to_task(task['workOrderId'], "Executed by Ansible")
                    taskResponse = module.client.api.execute_task(task['workOrderId'])
                    if "errorMessage" in str(taskResponse):
                        result['data']={'changed':False,'data':task,'response':taskResponse['errorMessage']}
                    else:
                        result['data']={'changed':True,'data':task,'response':taskResponse['data']}
                        result['changed']=True
                else:
                    result['data']={'changed':False,'data':task,'response':'invalid task status'}
            else:
                for task in taskData['data']:
                    if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                        module.client.api.add_note_to_task(task['workOrderId'], "Executed by Ansible")
                        taskResponse = module.client.api.execute_task(task['workOrderId'])
                        if "errorMessage" in str(taskResponse):
                            taskResult.append({'changed':False,'data':task,'response':taskResponse['errorMessage']})
                        else:
                            taskResult.append({'changed':True,'data':task,'response':taskResponse['data']})
                            result['changed']=True
                result['data']=taskResult
        elif module.params['action'] == "delete":
            if taskData['data'] == [None]:
                result['data']={'changed':False,'data':taskData,'response':'nothing found'}
            elif len (taskData['data']) == 1:
                task = taskData['data'][0]
                if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                    module.client.api.add_note_to_task(task['workOrderId'], "Deleted by Ansible")
                    taskResponse = module.client.api.cancel_task(task['workOrderId'])
                    if "errorMessage" in str(taskResponse):
                        result['data']={'changed':False,'data':task,'response':taskResponse['errorMessage']}
                    else:
                        result['data']={'changed':True,'data':task,'response':taskResponse['data']}
                        result['changed']=True
                else:
                    result['data']={'changed':False,'data':task,'response':'invalid task status'}
            else:
                for task in taskData['data']:
                    if task['workOrderUserDefinedStatus'] == "Pending" or task['workOrderUserDefinedStatus'] == "Failed":
                        module.client.api.add_note_to_task(task['workOrderId'], "Deleted by Ansible")
                        taskResponse = module.client.api.execute_task(task['workOrderId'])
                        if "errorMessage" in str(taskResponse):
                            taskResult.append({'changed':False,'data':task,'response':taskResponse['errorMessage']})
                        else:
                            taskResult.append({'changed':True,'data':task,'response':taskResponse['data']})
                            result['changed']=True
                result['data']=taskResult
        else:
            ## Debug Line ##
            module.fail_json(msg=str('Debug - invalid action: %r' %module.params['action']))
            ## Debug Line ##
    else:
      errorOutput = 'No Task Found: %s' %module['params']['taskID']
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
        taskID=dict(default='all',type='str'),
        action=dict(default='show', choices=['add','delete','show'])
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    result = dict(changed=False)

    module.client = connect(module)

    try:
        changed = process_task(module)
    except CvpApiError, e:
        module.fail_json(msg=str(e))
    else:
        if changed['changed']:
            result['changed'] = True
        result['data'] = changed['data']
    module.exit_json(**result)

if __name__ == '__main__':
    main()
