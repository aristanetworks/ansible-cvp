#!/usr/bin/env python
# coding: utf-8 -*-
#
# GNU General Public License v3.0+
#
# Copyright 2019 Arista Networks AS-EMEA
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
from typing import Any
import logging
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_configlet')
MODULE_LOGGER.info('Start cv_configlet module execution')

# CONSTANT TO DEFINE DICT FIELDS
FIELD_SUCCESS = 'success'
FIELD_CHANGED = 'changed'
FIELD_TASKIDS = 'taskIds'
FIELD_COUNT = '_count'
FIELD_CHANGE_LIST = '_list'
FIELD_DIFFS = 'diff'
FIELD_DIFF = 'diff'


class CvApiResult():
    """
    CvApiResult Object Class to represent Ansible response for an API call execution.

    Helper to build a standard Ansible output for all modules in an ansible collection.
    It provides all the generic flags like success and changed
    An abstraction layer is also available to add event and count all these event and expose result in a dict format

    Example
    -------

    >>> my_change = CvApiResult(action_name='create_container')
    >>> my_change.add_event('configlet-x-attached-to-container')
    >>> my_change.success = True
    >>> print(str(my_change.results))
    {
        "name": ''configlet-x-attached-to-container',
        "success": True,
        "create_container_count": 1,
        "create_container_list": [
            'configlet-x-attached-to-container'
        ]
    }
    """

    def __init__(self, action_name: str):
        self.__success = False
        self.__changed = False
        self.__taskIds = list()
        self.__count = 0
        self.__diff = None
        self.__list_changes = list()
        self.__action_name = action_name

    @property
    def name(self):
        """
        name Getter for CvActionResult name

        Returns
        -------
        str
            Name of CvActionResult
        """
        return self.__action_name

    @name.setter
    def name(self, name):
        """
        name Setter for CvActionResult name

        Parameters
        ----------
        name : str
            Name to allocate to CvActionResult
        """
        self.__action_name = name

    @property
    def success(self):
        """
        success Getter for success flag

        Returns
        -------
        bool
            Success flag status
        """
        return self.__success

    @success.setter
    def success(self, yes: bool):
        """
        success Setter for success flag

        Parameters
        ----------
        yes : bool
            True if success, Fals if not
        """
        self.__success = yes

    @property
    def changed(self):
        """
        changed Getter for changed flag

        Returns
        -------
        bool
            Changed flag status
        """
        return self.__changed

    @changed.setter
    def changed(self, yes: bool):
        """
        changed Setter for changed flag

        Parameters
        ----------
        yes : bool
            True if changed, False if not
        """
        self.__changed = yes

    @property
    def count(self):
        """
        count Getter for number of event received

        Returns
        -------
        int
            Number of event received by CvActionResult
        """
        return self.__count

    @count.setter
    def count(self, i: int):
        """
        count Setter for number of event received

        Parameters
        ----------
        i : int
            Number of new event to register in CvActionResult object
        """
        self.__count = i

    @property
    def diff(self):
        """
        diff Getter for diff result

        Returns
        -------
        list
            List of changes computed by Ansible
        """
        return self.__diff

    @diff.setter
    def diff(self, diff: Any):
        """
        diff Setter for diff result

        Parameters
        ----------
        diff : Any
            Diff computed by Ansible
        """
        self.__diff = diff

    @property
    def list_changes(self):
        return self.__list_changes

    def add_entry(self, entry: str):
        """
        add_entry Add an event to CvActionResult object

        Adding an event create an entry in event base and increment count of event

        Parameters
        ----------
        entry : str
            Event message to store
        """
        self.__count += 1
        self.__list_changes.append(entry)

    def add_entries(self, entries: list):
        """
        add_entries Add a list of entries to instance

        Parameters
        ----------
        entries : list
            List of string to add to ApiReponse instance
        """
        self.__count += len(entries)
        self.__list_changes += entries

    @property
    def taskIds(self):
        """
        taskIds Get list of tasks created for this API response

        Returns
        -------
        list
            List of taskIds from Cloudvision
        """
        return self.__taskIds

    @taskIds.setter
    def taskIds(self, tasks: list):
        """
        taskIds Add a list of tasks to the current taskIds list.

        Parameters
        ----------
        tasks : list
            List of TaskIds coming from Cloudvision
        """
        self.__taskIds += tasks
        self.__taskIds = list(set(self.__taskIds))

    @property
    def results(self):
        """
        results Getter to provide a structured output based on a dictionary

        List following elements:
        - success flag
        - changed flag
        - number of event received
        - Task IDs received
        - List of event received

        Returns
        -------
        dict
            Dictionary with all values
        """
        result = dict()
        result[FIELD_SUCCESS] = self.__success
        result[FIELD_CHANGED] = self.__changed
        result[FIELD_TASKIDS] = self.__taskIds
        result[FIELD_DIFF] = self.__diff
        result[self.__action_name + FIELD_COUNT] = self.__count
        result[self.__action_name +
               FIELD_CHANGE_LIST] = self.__list_changes
        return result


class CvManagerResult():
    """
    CvManagerResult Object class to represent all activities run by a module for a set of activities

    It is used to concentrate inputs for a subset of actions of a module like move device or attach configlet

    Example
    -------
    >>> my_change = CvApiResult(action_name='create_container')
    >>> my_change.add_event('configlet-x-attached-to-container')
    >>> my_change.success = True
    >>>
    >>> my_manager = CvManagerResult(builder_name = 'TEST_BUILDER')
    >>> my_manager.add_change(change = my_change)
    >>> my_manager.changes
    {
        "TEST_BUILDER_list": [
            "create_container"
        ],
        "success": "True",
        "changed": "False",
        "taskIds": [],
        "diff": {},
        "TEST_BUILDER_count": 3
    }

    """
    def __init__(self, builder_name: str, default_success: bool = False):
        self.__name = builder_name
        self.__success = default_success
        self.__changed = False
        self.__counter: int = 0
        self.__taskIds = list()
        self.__changes = dict()
        self.__diffs = dict()
        self.__changes[self.__name + FIELD_CHANGE_LIST] = list()

    def add_change(self, change: CvApiResult):
        """
        add_change Add a CvApiResult change to current instance

        Register t a CvApiResult to your current CvManagerResult instance.
        This addition will automatically extract data and increment number of events

        Parameters
        ----------
        change : CvApiResult
            Change to add to our manager
        """
        MODULE_LOGGER.debug('receive add_change with %s', str(change.results))
        if change.success:
            if change.success:
                self.__success = change.success
            if self.__changed is not True:
                self.__changed = change.changed
            self.__taskIds += change.taskIds
            self.__counter += change.count
            self.__changes[self.__name + FIELD_CHANGE_LIST].append(change.name)
            if change.diff is not None:
                self.__diffs[change.name] = change.diff

    @property
    def changed(self):
        """
        changed Expose flag changed of instance

        Used to report if at least one of the registered actions has changed content during execution

        Returns
        -------
        bool
            True or False
        """
        return self.__changed

    @property
    def success(self):
        """
        success Expose flag success of instance

        Used to report if all entries of the registered actions has succeeded during execution

        Returns
        -------
        bool
            True or False
        """
        return self.__success

    @property
    def changes(self):
        """
        changes Expose instance data into a dict manner.

        Expose all data into a dict manner that can be consume to build report

        Example
        -------
        >>> my_manager = CvManagerResult(builder_name = 'TEST_BUILDER')
        >>> my_manager.add_change(change = my_change)
        >>> my_manager.changes
        {
            "TEST_BUILDER_list": [
                "create_container"
            ],
            "success": "True",
            "changed": "False",
            "taskIds": [],
            "diff": {},
            "TEST_BUILDER_count": 3
        }

        Returns
        -------
        dict
            Manager data
        """
        self.__changes[FIELD_SUCCESS] = self.__success
        self.__changes[FIELD_CHANGED] = self.__changed
        self.__changes[FIELD_TASKIDS] = self.__taskIds
        self.__changes[FIELD_DIFFS] = self.__diffs
        self.__changes[self.__name + FIELD_COUNT] = self.__counter
        return self.__changes

    @property
    def name(self):
        """
        name Name of the CvApiManager instance

        Returns
        -------
        str
            Name of the manager
        """
        return self.__name


class CvAnsibleResponse():
    """
    CvAnsibleResponse Ansible Output Manager for ansible output

    Provide a single method to build a consistent module output
    format across the collection.

    Example:
    $ ansible-playbook ....
    ok: [cv_server] =>
      msg:
          changed: true
          data:
          changed: true
          configlets_attached:
              changed: true
              configlets_attached_count: 2
              configlets_attached_list:
              - CV-ANSIBLE-EOS01_configlet_attached
              diff: {}
              success: true
              taskIds:
              - '444'
          devices_deployed:
              changed: false
              devices_deployed_count: 0
              devices_deployed_list: []
              diff: {}
              success: false
              taskIds: []
          devices_moved:
              changed: false
              devices_moved_count: 0
              devices_moved_list: []
              diff: {}
              success: false
              taskIds: []
          success: false
          failed: false
    """
    def __init__(self):
        self.success = False
        self.changed = False
        self.data = dict()
        self.taskIds = list()

    def add_manager(self, api_manager: CvManagerResult):
        """
        add_manager Register a CvManagerResult entry in Ansible

        Parameters
        ----------
        api_manager : CvManagerResult
            Api Manager with information to display by Ansible
        """
        self.data[api_manager.name] = api_manager.changes
        if api_manager.success:
            self.success = api_manager.success
        if self.changed is False:
            self.changed = api_manager.changed
        for task in api_manager.changes[FIELD_TASKIDS]:
            self.taskIds.append(task)
        self.taskIds = list(set(self.taskIds))

    @property
    def content(self):
        """
        content Expose Ansible Output manager content

        Getter to provide ansible output

        Returns
        -------
        dict
            All information for Ansible
        """
        self.data[FIELD_SUCCESS] = self.success
        self.data[FIELD_CHANGED] = self.changed
        self.data[FIELD_TASKIDS] = self.taskIds
        return self.data
