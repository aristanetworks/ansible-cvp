#!/usr/bin/env python
# coding: utf-8 -*-
#
# GNU General Public License v3.0+
#
# Copyright 2021 Arista Networks AS-EMEA
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

from __future__ import (absolute_import, division, print_function)
import string
__metaclass__ = type

import traceback
import logging
import random
import string
from datetime import datetime
from typing import List
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse  # noqa # pylint: disable=unused-import
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger('arista.cvp.change_tools')
MODULE_LOGGER.info('Start change_tools module execution')



class CvpChangeControlBuilder:
    """
    CvpChangeControlBuilder Class to the generation of a CVP Change control.
    
    Methods
    -------
    build_cc(data)
        Returns the Change Control datastructure.
    add_known_uuid(list(str))
        Provide a list of UUIDs already in use to the class, to prevent collisions.
    """
    def __init__( self ):
        # Guarantee that the generated IDs are unique, for this session
        self.__keySize = 12
        self.__keyStore = []
        # Track if a stage is meant to be series or parallel
        self.__stageMode = {}
        # Map the stage name to the generated IDs
        self.__stageMapping = {}
        # The final change control
        self.ChangeControl = {}
        

        
    def build_cc(self, data, name = None):
        """
        Build the change control data structure

        Parameters
        ----------
        data: dict
            The dict consists of the following keys and data types;
            name: str
               The name of the change control
            activities: list
               A list of tasks or actions to be executed. Each entry is a dict consisting of;
                    action (if performing a Change Control action): str
                        The name of the Change Control Action e.g. what you select from the drop down menu in the GUI
                    task_id: int
                        The Task / Work Order Id for the task to be executed
                    timeout: int
                        The timeout value to be used for task completion 
                    name: str
                        A name for the card/action - not required or used outside of datastructures
                    device: str
                        Name of the device that this action is to be performed on
                    stage: str
                        The name of the stage to assign the action to 
            stages: list
               A list of stages, with their name, mode and parent stage defined;
                    name: str
                        The name of the stage
                    mode: str (series | parallel)
                        Defines if tasks/actions within that stage should be performed in series or parallel.
                        Series is the default
                    parent: str
                        The name of the parent stage to assign this stage to
                        
        Example data
        ------------
        Sample data passed to method::
          - name: TestCC123
            notes: Test change 
            activities:
              - task_id: 1234
                name: "task"
                timeout: 12000
                stage: Stage2
              - action: "Switch Healthcheck"
                name: "Switch1_health"
                device: DC1-Leaf1a
                stage: Stage0
    
              - action: "Switch Healthcheck"
                name: "Switch1_health"
                device: switch1
                stage: Stage1b
    
              - action: "Switch Healthcheck"
                name: "Spine 1 Health Check"
                device: DC1-SPINE1
                stage: Stage1b
            stages:
              - name: Stage0
                mode: parallel
    
              - name: Stage1
                mode: parallel
    
              - name: Stage1b
                mode: parallel
                parent: Stage1
    
              - name: Stage2
                mode: series  
        

        Returns
        -------
        Str:
            A random string, of length __keySize, guaranteed to be unique within the class instance.
        """        
        data = self._validate_input(data, name)
        self._create_cc_struct( data['name'], notes=data['notes'] )
        
        for stage in data['stages']:
            if 'parent' in stage.keys():
                self._create_stage(stage['name'],mode=stage['mode'],parent=stage['parent'])
            else:
                self._create_stage(stage['name'],mode=stage['mode'])


        for action in data['activities']:
            if 'task_id' in action:
                self._create_task(action['name'], action['task_id'], action['stage'])
            else:
                self._create_action(action['name'], action['action'], action['stage'], action['device'])

        return self.ChangeControl



    def add_known_uuid(self, existing_id):
        """
        Update our list of UUIDs with other known ones, to prevent ID collussions

        Parameters
        ----------
        existing_id: list (str)
            List of strings, representing UUIDs already in use

        Returns
        -------
        None
        """
        for entry in existing_id:
            if entry not in self.__keyStore:
                self.__keyStore.append(entry)

        return None

    def _validate_input( self, data, name = None ):
        """
        Sanitize the incoming data structure

        Parameters
        ----------
        data: dict
            Provided data structure defining the Change
        name: str
            The name of the CC, coming from the module call

        Returns
        -------
        data: dict
            Sanitized version of the input
        """
        defined_stages = []
        
        if 'name' not in data and name is None:
            name = "Change "
            timestamp = datetime.now()
            name += timestamp.strftime("%Y%m%d_%H%M%S")
            data['name'] = name
        elif name is not None and len(name) > 0:
            data['name'] = name
        
        
        if 'notes' not in data:
            data['notes'] = None
            
        if 'stages' not in data:
            data['stages'] = []
        
        if 'activities' not in data:
            data['activities'] = []
        
        # Build a list of all the user defined stages
        for stage in data['stages']:
            if 'name' in stage:
                defined_stages.append(stage['name'])
            if 'mode' not in stage:
                stage['mode'] = "series"

        # if a task/action is assigned to a stage that isn't created
        # assign it to the root stage
        for task in data['activities']:
            if 'stage' in task:
                if task['stage'] not in defined_stages:
                    task['stage'] = None
            if 'task_id' in task and 'name' not in task:
                task['name'] = "task"

        # if the key is provided, we are updating an existing CC
        if 'key' in data:
            self.__changeKey = data['key']
        
        return data            
        
    def __genID__( self ):
        """
        Generates a UUID to identify each task/action and stage, and the assignment of the 
        former to the latter. The UUID should be unique within the Change control.

        Parameters
        ----------
        __keySize: int
            The number of ascii_letters to include in the ID.

        Returns
        -------
        Str:
            A random string, of length __keySize, guaranteed to be unique within the class instance.
        """
        while True:
            id = ''.join( random.choices( string.ascii_letters, k=self.__keySize ) )
            if id not in self.__keyStore:
                self.__keyStore.append(id)
                return(id)
            else:
                # Keep looping until we get a unique ID
                pass
            
        
    def __attachThing( self, ownId, parent=None ):
        """
        Assign a task/action to a stage within the Change Control

        Parameters
        ----------
        oneId: Str
            The UUID assigned to this task or action
        parent: Str
            The UUID of the stage the task/action is to be assigned to.
            By default everything will be assigned to the root stage unless otherwise specified

        Returns
        -------
        None:
            The Class ChangeControl is updated to reflect the updated attachment.
        """
        # If we don't have a parent, we are attached to the Root Stage
        if parent == None:
            parentId = self.ChangeControl['change']['rootStageId']
        else:
            parentId = self.__stageMapping[parent]
        
        # Depending on if it's a series or parallel stage, we need to populate the structure differently e.g. list of dicts vs list of strings
        if self.__stageMode[parentId] == 'parallel':
            if len(self.ChangeControl['change']['stages']['values'][parentId]['rows']['values']) == 0:
                self.ChangeControl['change']['stages']['values'][parentId]['rows']['values'].append( {'values': [ ownId ] } )
            else:
                self.ChangeControl['change']['stages']['values'][parentId]['rows']['values'][0]['values'].append(ownId)

        else:
            self.ChangeControl['change']['stages']['values'][parentId]['rows']['values'].append( {'values': [ ownId ] } )
        
        return None
            


    def _create_cc_struct(self, name, mode='series', notes=None):
        """
        Create the Change Control starting structure

        Parameters
        ----------
        Name: Str
            The name of the CC 
        mode: Str: series/parallel
            For now, the mode of the root stage is always series - the API does not let a CC to be created
            with the root stage as parallel, even when it has multiple stages/tasks/actions assigned to it.
            
            The GUI allows the root stage to be changed to parallel, but only after it's created.
            
            Our workaround is to always have a "hidden" root stage, always series, and we assign the 
            defined root/Stage 0 to that - the child stages can be series or parallel on creation.
        notes: Str
            Any notes to be added to the CC, default is "Created by Ansible-CVP".

        Returns
        -------
        None:
            The Class ChangeControl is updated to reflect the updated attachment
        """
        changeControl = {}
        change = {}
        change['name'] = name
        if notes is not None:
            change['notes'] = notes
        else:
            change['notes'] = "Created by Ansible-CVP"
        change['stages'] = {}
        change['stages']['values'] = {}
        change['rootStageId'] = self.__genID__()
        self.__stageMapping[name] = change['rootStageId']
        
        change['stages']['values'][ change['rootStageId'] ] = {}
        change['stages']['values'][ change['rootStageId'] ]['name'] = " ".join([name, "root stage"])
        change['stages']['values'][ change['rootStageId'] ]['rows'] = {}
        change['stages']['values'][ change['rootStageId'] ]['rows']['values'] = []
        
        # We could in theory have a collision here, as the key is basically the Change Control ID
        # and since we don't know all the CC IDs, there is a non-0 possibility of this occurring
        changeControl['key'] = { 'id': str(self.__genID__()) }
        changeControl['change'] = change
        
        self.__stageMode[ change['rootStageId'] ] = mode
       
        self.ChangeControl = changeControl
        
        return None


    def _create_stage(self, name, mode='series', parent=None):
        """
        Create a stage within the Change Control

        Parameters
        ----------
        name: Str
            The name of the stage - this should be unique
        mode: Str (series | parallel)
            The mode defines if tasks/actions within the stage will be executed in series
            or in parallel
        parent: Str
            The UUID of the parent stage that this stage is to be assigned to.
            By default will be assigned to the root stage

        Returns
        -------
        None:
            The Class ChangeControl is updated to include the new stage
        """
        stageId = self.__genID__()
        self.__stageMode[stageId] = mode
        self.__stageMapping[name] = stageId
        self.__attachThing(stageId,parent)
        stage = {}
        stage['name'] = name
        stage['rows'] = {}
        stage['rows']['values'] = []
        
        self.ChangeControl['change']['stages']['values'][stageId] = stage
        
        return None
        
 
        
    def _create_task(self, name, taskID, stage=None, timeout=3000):
        """
        Create a task within the Change Control

        Parameters
        ----------
        name: Str
            The name of the task - by default this is "task"
        taskID: Str 
            The task/workorderID of the task to be executed
        stage: Str
            The name of the stage that this task is to be assigned to
        timeout: Int
            The timeout value for task completion in X units

        Returns
        -------
        None:
            The Class ChangeControl is updated to include the new task
        """
        task = {}
        task['action'] = {}
        task['action']['name'] = 'task'
        task['action']['args'] = {}
        task['action']['args']['values'] = {}
        task['action']['args']['values']['TaskID'] = taskID
        task['action']['timeout'] = timeout
        task['name'] = name
        
        cardID = self.__genID__()
        self.ChangeControl['change']['stages']['values'][cardID] = task
        self.__attachThing(cardID, stage)
        
        return None
        

    def _create_action(self, name, action, stage, deviceID):
        """
        Create a task within the Change Control

        Parameters
        ----------
        name: Str
            The name of the action - by default this is "task"
        taskID: Str 
            The task/workorderID of the task to be executed
        stage: Str
            The name of the stage that this task is to be assigned to
        timeout: Int
            The timeout value for task completion in X units

        Returns
        -------
        None:
            The Class ChangeControl is updated to include the new task
        """
        
        task = {}
        task['action'] = {}
        task['action']['name'] = action
        task['action']['args'] = {}
        task['action']['args']['values'] = {}
        task['action']['args']['values']['DeviceID'] = deviceID
        task['name'] = name
        
        cardID = self.__genID__()
        self.ChangeControl['change']['stages']['values'][cardID] = task
        self.__attachThing(cardID, stage)
        
        return None





class CvChangeControlTools():
    """
    CvImageTools Class to manage Cloudvision Change Controls
    """
    def __init__(self, cv_connection, ansible_module: AnsibleModule = None, check_mode: bool = False):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module
        self.__check_mode = check_mode
        # A list of tuples ("Change Control Name", "Change control ID")
        self.__cc_index = []
        self.cvp_version = self.__cv_client.api.get_cvp_info()['version']
        self.apiversion = self.__cv_client.apiversion
        
    def __index_cc__(self):
        """
        Index the known Change Controls, creating an internal list of tuples
        ( Change Control Name, Change Control ID )

        Parameters
        ----------
        None: 
            Provided data structure defining the Change
            
        Returns
        -------
        None: 
            
        """
        MODULE_LOGGER.debug('Indexing Change Controls')
        self.__cc_index.clear()
        
        for entry in self.change_controls['data']:
            self.__cc_index.append( (entry['result']['value']['change']['name'], entry['result']['value']['key']['id']) )

        return None
            
    def _find_id_by_name(self, name):
        """
        Find the ID of a change control, by name

        Parameters
        ----------
        name: str
            The name of the CC

        Returns
        -------
        cc_id: list
            A list of matching change control IDs
        """
        cc_id = []
        cc_id = list( filter(lambda x:name in x, self.__cc_index) )
        MODULE_LOGGER.debug('%d changes found' % len(cc_id))
        return cc_id
    
     
            
        
    def get_all_change_controls(self):
        """
        Get all change controls on CVP

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        cc_list = []
        MODULE_LOGGER.debug('Collecting Change controls')
        
        if self.apiversion < 3.0:
            MODULE_LOGGER.debug('Trying legacy API call')
            cc_list = self.__cv_client.api.get_change_controls()
        
        else:
            # Rewrite on cvprac > 1.0.7
            MODULE_LOGGER.debug('Using resource API call')
            cc_list = self.__cv_client.get('/api/resources/changecontrol/v1/ChangeControl/all')

        if len(cc_list) > 0:
            self.change_controls = cc_list
            self.__index_cc__()
            return True

        return None

    
    def get_change_control(self, cc_id):
        """
        Get a specific change control

        Parameters
        ----------
        cc_id: str
            The UUID of the Change Control in question

        Returns
        -------
        change: dict
            A dict describing the request change control
        """
        MODULE_LOGGER.debug('Collecting change control: %s' % cc_id)
        if self.apiversion < 3.0:
            MODULE_LOGGER.debug('Using legacy API call')
            change = self.__cv_client.api.get_change_control_info(cc_id)
        else:
            # Rewrite on cvprac > 1.0.7
            params = 'key.id={}'.format(cc_id)
            cc_url = '/api/resources/changecontrol/v1/ChangeControl?' + params
            change = self.__cv_client.get(cc_url)
            
        return change
    
        
    
    
    def module_action(self, change:dict, name:str = None, state:str = "get", change_id:List[str] = None ):
        
        changed = False
        data = dict()
        warnings = list()
        
        MODULE_LOGGER.debug('Collecting all change controls')
        self.get_all_change_controls()
        
        if state == "get":

            if name is None:
                return changed, {'change_controls': self.change_controls}, warnings
            else:
                cc_list = []
                cc_id_list = self._find_id_by_name(name)
                for change in cc_id_list:
                    MODULE_LOGGER.debug('Looking up change: %s with ID: %s' % (change[0],change[1]) )
                    cc_list.append(self.get_change_control(change[1]) )

                # Revisit this - should be the full CC I guess
                return changed, {'change_controls:': cc_list  }, warnings

            
            
        elif state == "remove":
            MODULE_LOGGER.debug("Deleting change control")
            if change_id is not None:
                if name is not None:
                    warnings.append("Deleting CC IDs takes precedence over deleting named CCs. Only the provided CCids will be deleted")
                try:
                    changes = self.__cv_client.api.delete_change_controls(change_id)
                    MODULE_LOGGER.debug("Response to delete request was: %s" % changes)
                    if len(changes) > 0:
                        changed = True
                    else:
                        warnings.append('No changes made in delete request')
                except Exception as e:
                    self.__ansible.fail_json(msg="{0}".format(e))
                    
                return changed,{'remove':changes}, warnings
            
            elif name is not None:
                cc_list = self._find_id_by_name(name)
                if len(cc_list) == 0:
                    warnings.append("No matching change controls found for %s" % name)
                    return changed, {'search': name}, warnings
                elif len(cc_list) > 1:
                    warnings.append("Multiple changes (%d) found matching name: %s" % (len(cc_list),name ) )
                    # Should we hard fail here?
                    e = "Deleting multiple CCs by name is not supported at this time"
                    self.__ansible.fail_json(msg="{0}".format(e))
                    return changed, {'matches': cc_list}, warnings
                else:
                    try:
                        changes = self.__cv_client.api.delete_change_controls(change_id)
                        if len(changes) > 0:
                            changed = True
                        else:
                            warnings.append('No changes made in delete request')
                    except Exception as e:
                        self.__ansible.fail_json(msg="{0}".format(e))
            else:
                e = "Unable to delete change control. Change name or change_id(s) must be specified"
                self.__ansible.fail_json(msg="{0}".format(e))
                    
        elif state == "set":
            changeControl = CvpChangeControlBuilder()
            changeControl.add_known_uuid( [ v[1] for v in self.__cc_index ] )
            cc_structure = changeControl.build_cc(change, name)
            
            try:
                data = self.__cv_client.post('/api/resources/changecontrol/v1/ChangeControlConfig',data=cc_structure )
                changed = True
                
            except Exception as e:
                self.__ansible.fail_json(msg="{0}".format(e))            
            
        
        return changed, data, warnings