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

    # CONSTANT TO DEFINE DICT FIELDS
    __FIELD_SUCCESS = 'success'
    __FIELD_CHANGED = 'changed'
    __FIELD_TASKIDS = 'taskIds'
    __FIELD_COUNT = '_count'
    __FIELD_CHANGE_LIST = '_list'
    __FIELD_DIFF = 'diff'

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
        self.__count += len(entries)
        self.__list_changes += entries

    @property
    def taskIds(self):
        return self.__taskIds

    @taskIds.setter
    def taskIds(self, tasks: list):
        self.__taskIds += tasks

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
        result[self.__FIELD_SUCCESS] = self.__success
        result[self.__FIELD_CHANGED] = self.__changed
        result[self.__FIELD_TASKIDS] = self.__taskIds
        result[self.__FIELD_DIFF] = self.__diff
        result[self.__action_name + self.__FIELD_COUNT] = self.__count
        result[self.__action_name +
               self.__FIELD_CHANGE_LIST] = self.__list_changes
        return result


class CvManagerResult():

    __FIELD_SUCCESS = 'success'
    __FIELD_CHANGED = 'changed'
    __FIELD_TASKIDS = 'taskIds'
    __FIELD_COUNT = '_count'
    __FIELD_CHANGE_LIST = '_list'
    __FIELD_DIFFS = 'diff'

    def __init__(self, builder_name: str):
        self.__name = builder_name
        self.__success = False
        self.__changed = False
        self.__counter: int = 0
        self.__taskIds = list()
        self.__changes = dict()
        self.__diffs = dict()
        self.__changes[self.__name + self.__FIELD_CHANGE_LIST] = list()

    def add_change(self, change: CvApiResult):
        MODULE_LOGGER.debug('receive add_change with %s', str(change.results))
        if change.success:
            self.__success = change.success
            self.__changed = change.changed
            self.__taskIds += change.taskIds
            self.__counter += change.count
            self.__changes[self.__name + self.__FIELD_CHANGE_LIST].append(change.name)
            if change.diff is not None:
                self.__diffs[change.name] = change.diff
        # self.__changes[change.name] = {
        #     change.name: change.count, change.name + self.__FIELD_CHANGE_LIST: change.list_changes}

    @property
    def changes(self):
        # self.__changes['name'] = self.__name
        # self.changes[self.__FIELD_DIFFS] = self.__diffs
        self.__changes[self.__FIELD_SUCCESS] = self.__success
        self.__changes[self.__FIELD_CHANGED] = self.__changed
        self.__changes[self.__FIELD_TASKIDS] = self.__taskIds
        self.__changes[self.__FIELD_DIFFS] = self.__diffs
        self.__changes[self.__name + self.__FIELD_COUNT] = self.__counter
        return self.__changes

    @property
    def name(self):
        return self.__name
