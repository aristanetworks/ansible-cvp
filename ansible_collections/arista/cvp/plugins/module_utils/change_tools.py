#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#
# Copyright 2021 Arista Networks
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
__metaclass__ = type

import traceback
import logging
import uuid
from datetime import datetime
from typing import List
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse  # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas import v3 as schema
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import validate_json_schema
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger('arista.cvp.change_tools')
MODULE_LOGGER.info('Start change_tools module execution')

# TODO - use f-strings
# pylint: disable=consider-using-f-string


class CvChangeControlInput(object):
    def __init__(self, user_change: dict, schema=schema.SCHEMA_CV_CHANGE_CONTROL) -> None:
        self.__user_change = user_change
        self.__schema = schema

    @property
    def is_valid(self):
        """
        check_schemas Validate schemas for user's input
        """
        if not validate_json_schema(user_json=self.__user_change, schema=self.__schema):
            MODULE_LOGGER.error("Invalid change control input : \n%s", str(self.__user_change))
            return False
        return True


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
    def __init__(self):
        # Guarantee that the generated IDs are unique, for this session
        self.__keyStore = []
        # Track if a stage is meant to be series or parallel
        self.__stageMode = {}
        # Map the stage name to the generated IDs
        self.__stageMapping = {}
        # The final change control
        self.ChangeControl = {}
        self._data = {}

    def build_cc(self, data, name=None):
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
                    task_id: str
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
              - task_id: "1234"
                name: "task"
                timeout: 12000
                stage: Stage2
              - action: "Switch Healthcheck"
                name: "Switch1_health"
                arguments:
                  - name: DeviceID
                    value: <device serial number>
                stage: Stage0

              - action: "Switch Healthcheck"
                name: "Switch1_health"
                arguments:
                  - name: DeviceID
                    value: <device serial number>
                stage: Stage1b

              - action: "Switch Healthcheck"
                name: "Spine 1 Health Check"
                arguments:
                  - name: DeviceID
                    value: <device serial number>
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
        Dict:
            The Change control.
        """
        self._validate_input(data, name)

        self._create_cc_struct(self._data['name'], notes=self._data['notes'])

        for stage in self._data['stages']:
            if 'parent' in stage.keys():
                self._create_stage(stage['name'], mode=stage['mode'], parent=stage['parent'])
            else:
                self._create_stage(stage['name'], mode=stage['mode'])

        for action in self._data['activities']:
            if 'task_id' in action:
                self._create_task(action['name'], action['task_id'], action['stage'])
            else:
                self._create_action(action['name'], action['action'], action['stage'], action['arguments'])

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

    def _validate_input(self, data, name=None):
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
        data: None
         """
        defined_stages = []
        self._data = deepcopy(data)

        if 'name' not in self._data and name is None:
            name = "Change "
            timestamp = datetime.now()
            name += timestamp.strftime("%Y%m%d_%H%M%S")
            self._data['name'] = name
        elif name is not None and len(name) > 0:
            self._data['name'] = name

        if 'notes' not in self._data:
            self._data['notes'] = None

        if 'stages' not in self._data:
            self._data['stages'] = []

        if 'activities' not in self._data:
            self._data['activities'] = []

        # Build a list of all the user defined stages
        for stage in self._data['stages']:
            if 'name' in stage:
                defined_stages.append(stage['name'])
            if 'mode' not in stage:
                stage['mode'] = "series"

        # if a task/action is assigned to a stage that isn't created
        # assign it to the root stage
        for task in self._data['activities']:
            if 'stage' in task:
                if task['stage'] not in defined_stages:
                    task['stage'] = None
            if 'task_id' in task and 'name' not in task:
                task['name'] = "task"
            if 'task_id' not in task and 'name' not in task:
                task['name'] = "action_"
                task['name'] += task['action']
                task['name'] += "_"
                task['name'] += task['device']

            # Allow for optional Custom Action arguments to be passed
            if 'action' in task and 'arguments' not in task:
                task['arguments'] = None

        # if the key is provided, we are updating an existing CC
        if 'key' in self._data:
            self.__changeKey = self._data['key']
        else:
            self.__changeKey = None

        return None

    def __genID__(self):
        """
        Generates a UUID to identify each task/action and stage, and the assignment of the
        former to the latter. The UUID should be unique within the Change control.

        Parameters
        ----------
        None

        Returns
        -------
        Str:
            A str of UUID4.
        """
        while True:
            id = str(uuid.uuid4())
            if id not in self.__keyStore:
                self.__keyStore.append(id)
                return (id)
            else:
                # Keep looping until we get a unique ID
                pass

    def __attachThing(self, ownId, parent=None):
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
        if parent is None:
            parentId = self.ChangeControl['change']['rootStageId']
        else:
            parentId = self.__stageMapping[parent]

        # Depending on if it's a series or parallel stage, we need to populate the structure differently e.g. list of dicts vs list of strings
        if self.__stageMode[parentId] == 'parallel':
            if len(self.ChangeControl['change']['stages']['values'][parentId]['rows']['values']) == 0:
                self.ChangeControl['change']['stages']['values'][parentId]['rows']['values'].append({'values': [ownId]})
            else:
                self.ChangeControl['change']['stages']['values'][parentId]['rows']['values'][0]['values'].append(ownId)
        else:
            self.ChangeControl['change']['stages']['values'][parentId]['rows']['values'].append({'values': [ownId]})

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

        change['stages']['values'][change['rootStageId']] = {}
        change['stages']['values'][change['rootStageId']]['name'] = " ".join([name, "root stage"])
        change['stages']['values'][change['rootStageId']]['rows'] = {}
        change['stages']['values'][change['rootStageId']]['rows']['values'] = []

        if self.__changeKey is None:
            changeControl['key'] = {'id': str(self.__genID__())}
        else:
            changeControl['key'] = {'id': self.__changeKey}

        changeControl['change'] = change

        self.__stageMode[change['rootStageId']] = mode

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
        self.__attachThing(stageId, parent)
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

    def _create_action(self, name, action, stage, arguments=None):
        """
        Create a task within the Change Control

        Parameters
        ----------
        name: Str
           Only used internally - name associated with the action, not really required
        action: Str
            The name of the action - the is the internal action name
        stage: Str
            The name of the stage that this task is to be assigned to
        arguments: Dict
            Optional - pass custom arguments to the action
            The 'DeviceID' key (serial number) is used, by convention, for actions that are applied
            to a specific device


        Returns
        -------
        None:
            The Class ChangeControl is updated to include the new action
        """

        task = {}
        task['action'] = {}
        task['action']['name'] = action
        task['action']['args'] = {}
        task['action']['args']['values'] = {}
        task['name'] = name

        if arguments is not None:
            for entry in arguments:
                task['action']['args']['values'][entry['name']] = entry['value']

        cardId = self.__genID__()
        self.ChangeControl['change']['stages']['values'][cardId] = task
        self.__attachThing(cardId, stage)

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
            if 'name' not in entry['result']['value']['change']:
                self.__cc_index.append(('Undefined', entry['result']['value']['key']['id']))
            else:
                self.__cc_index.append((entry['result']['value']['change']['name'], entry['result']['value']['key']['id']))

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
        # cc_id = list(filter(lambda x: name in x, self.__cc_index))
        for k, v in self.__cc_index:
            if name in k:
                cc_id.append(v)
        MODULE_LOGGER.debug('%d changes found', len(cc_id))
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
            MODULE_LOGGER.debug('Using resource API call')
            cc_list = self.__cv_client.api.change_control_get_all()

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
        MODULE_LOGGER.debug('Collecting change control: %s', cc_id)
        if self.apiversion < 3.0:
            MODULE_LOGGER.debug('Using legacy API call')
            try:
                change = self.__cv_client.api.get_change_control_info(cc_id)
            except Exception:
                MODULE_LOGGER.error('Change control with id %s not found', cc_id)
                change = None
        else:
            try:
                change = self.__cv_client.api.change_control_get_one(cc_id)
            except Exception:
                MODULE_LOGGER.error('Change control with id %s not found', cc_id)
                change = None

        return change

    def module_action(self, change: dict, name: str = None, state: str = "show", change_id: List[str] = None, schedule_time: str = None):

        changed = False
        data = {}
        warnings = []

        if state == "show":
            if name is None and change_id is None:
                MODULE_LOGGER.debug('Collecting all change controls')
                self.get_all_change_controls()
                return changed, {'change_controls': self.change_controls}, warnings
            else:
                cc_list = []
                if change_id is not None:
                    for change in change_id:
                        MODULE_LOGGER.debug('Looking up change: ID: %s', change)
                        cc_list.append(self.get_change_control(change))

                else:
                    self.get_all_change_controls()
                    cc_id_list = self._find_id_by_name(name)
                    for change in cc_id_list:
                        MODULE_LOGGER.debug('Found change for search: %s with ID: %s', name, change)
                        cc_list.append(self.get_change_control(change))

                return changed, {'change_controls': cc_list}, warnings

        elif state == "remove" and self.__check_mode is False:
            MODULE_LOGGER.debug("Deleting change control")
            if change_id is not None:
                if name is not None:
                    warnings.append("Deleting CC IDs takes precedence over deleting named CCs. Only the provided CCids will be deleted")
                try:
                    self.__cv_client.api.delete_change_controls(change_id)
                    MODULE_LOGGER.debug("Successfully deleted: %s", change_id)
                    changed = True
                except Exception as e:
                    if "Forbidden" in str(e):
                        message = "Failed to delete Change Control. User is unauthorized!"
                    else:
                        message = str(e)
                    logging.error(message)
                    self.__ansible.fail_json(msg="{0}".format(message))

                return changed, {'remove': []}, warnings

            elif name is not None:
                self.get_all_change_controls()
                cc_list = self._find_id_by_name(name)
                if len(cc_list) == 0:
                    warnings.append("No matching change controls found for %s" % name)
                    return changed, {'search': name}, warnings
                elif len(cc_list) > 1:
                    warnings.append("Multiple changes (%d) found matching name: %s" % (len(cc_list), name))
                    # Should we hard fail here?
                    e = "Deleting multiple CCs by name is not supported at this time"
                    self.__ansible.fail_json(msg="{0}".format(e))
                    return changed, {'matches': cc_list}, warnings
                else:
                    try:
                        MODULE_LOGGER.debug("Trying to delete: %s", cc_list)
                        data = self.__cv_client.api.delete_change_controls(cc_list)
                        changed = True
                    except Exception as e:
                        self.__ansible.fail_json(msg="{0}".format(e))
            else:
                e = "Unable to delete change control. Change name or change_id(s) must be specified"
                self.__ansible.fail_json(msg="{0}".format(e))

        elif state == "set" and self.__check_mode is False:
            changeControl = CvpChangeControlBuilder()
            changeControl.add_known_uuid([v[1] for v in self.__cc_index])

            # Check that our generated CCID is not already in use, and if it is,
            # add the UUID to the known list, and run again
            while True:
                MODULE_LOGGER.debug("Creating change control structure")
                cc_structure = changeControl.build_cc(change, name)
                if self.get_change_control(cc_structure['key']) is not None:
                    MODULE_LOGGER.debug("Change ID: %s was already known. Adding to list and running again", cc_structure['key'])
                    changeControl.add_known_uuid(cc_structure['key'])
                else:
                    MODULE_LOGGER.debug("Change ID: %s was not found, moving to next step", cc_structure['key'])
                    break

            try:
                MODULE_LOGGER.debug("Calling on CVP to create change")
                self.__cv_client.api.change_control_create_with_custom_stages(cc_structure)
                changed = True
                data = cc_structure['key']

            except Exception as e:
                if "Forbidden" in str(e):
                    message = "Failed to create Change Control. User is unauthorized!"
                else:
                    message = str(e)
                logging.error(message)
                self.__ansible.fail_json(msg="{0}".format(message))

        elif state in ['approve', 'unapprove', 'execute', 'schedule', 'approve_and_execute', 'schedule_and_approve'] and self.__check_mode is False:
            MODULE_LOGGER.debug("Change control state: %s", state)
            if change_id is not None:
                if name is not None:
                    warnings.append(
                        "CC ID takes precedence over handling named CCs. Only the provided CCid will be handled"
                    )
                if len(change_id) > 1:
                    warnings.append(
                        "Approving/Executing multiple CC IDs at one time is not supported"
                    )
                    e = "Approve/execute of multiple CCs by name is not supported at this time"
                    self.__ansible.fail_json(msg="{0}".format(e))
                    return changed, {"matches": change_id}, warnings
                else:
                    cc_id = change_id[0]
            elif name is not None:
                self.get_all_change_controls()
                cc_list = self._find_id_by_name(name)
                if len(cc_list) == 0:
                    warnings.append("No matching change controls found for %s" % name)
                    return changed, {"search": name}, warnings
                elif len(cc_list) > 1:
                    warnings.append(
                        "Multiple changes (%d) found matching name: %s"
                        % (len(cc_list), name)
                    )
                    # Should we hard fail here?
                    e = "Executing multiple CCs by name is not supported at this time"
                    self.__ansible.fail_json(msg="{0}".format(e))
                    return changed, {"matches": cc_list}, warnings
                else:
                    cc_id = cc_list[0]
            else:
                e = "Unable to approve/execute change control. Change name or change_id(s) must be specified"
                self.__ansible.fail_json(msg="{0}".format(e))
                return changed, data, warnings

            MODULE_LOGGER.debug("Action: %s change control: %s", state, cc_id)

            # First check if the change control needs to be scheduled
            try:
                if state in ['schedule', 'schedule_and_approve']:
                    data = self.__cv_client.api.change_control_schedule(cc_id, schedule_time)
                changed = True
            except Exception as e:
                self.__ansible.fail_json(msg="{0}".format(e))

            # Next check if the change control needs to be approved/unapproved
            try:
                if state in ['unapprove', 'approve', 'approve_and_execute', 'schedule_and_approve']:
                    data = self.__cv_client.api.change_control_approve(
                        cc_id, "Initiated from Ansible Playbook", (state != 'unapprove'))

                    if data is None:
                        e = "Change control {0} id not found".format(cc_id)
                        self.__ansible.fail_json(msg="{0}".format(e))
                        return changed, {"approve": change_id}, warnings
            except CvpRequestError as e:
                # Skip this - covers the case where an approved CC is approved again
                if "Forbidden" in str(e):
                    message = "Failed to approve Change Control. User is unauthorized!"
                    self.__ansible.fail_json(msg="{0}".format(message))
                    logging.error(str(message))
                else:
                    pass
            except Exception as e:
                self.__ansible.fail_json(msg="{0}".format(e))

            # Finally check if the change control needs to be executed
            try:
                if state in ['execute', 'approve_and_execute']:
                    data = self.__cv_client.api.change_control_start(cc_id)
                changed = True
            except Exception as e:
                self.__ansible.fail_json(msg="{0}".format(e))

        return changed, data, warnings
