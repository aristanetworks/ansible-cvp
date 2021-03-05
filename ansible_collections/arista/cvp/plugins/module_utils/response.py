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
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import


class CvApiResult():
    __FIELD_SUCCESS = 'success'
    __FIELD_CHANGED = 'changed'
    __FIELD_TASKIDS = 'taskIds'
    __FIELD_COUNT = '_count'
    __FIELD_CHANGE_LIST = '_list'

    def __init__(self, action_name: str):
        self.__success = False
        self.__changed = False
        self.__taskIds = list()
        self.__count = 0
        self.__list_changes = list()
        self.__action_name = action_name

    @property
    def name(self):
        return self.__action_name

    @name.setter
    def name(self, name):
        self.__action_name = name

    @property
    def success(self):
        return self.__success

    @success.setter
    def success(self, yes: bool):
        self.__success = yes

    @property
    def changed(self):
        return self.__changed

    @changed.setter
    def changed(self, yes: bool):
        self.__changed = yes

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, i: int):
        self.__count = i

    @property
    def list_changes(self):
        return self.__list_changes

    def add_entry(self, entry: str):
        self.__list_changes.append(entry)

    def add_entries(self, entries: list):
        self.__list_changes += entries

    @property
    def taskIds(self):
        return self.__taskIds

    @taskIds.setter
    def taskIds(self, tasks: list):
        self.__taskIds += tasks

    @property
    def results(self):
        result = dict()
        result[self.__FIELD_SUCCESS] = self.__success
        result[self.__FIELD_CHANGED] = self.__changed
        result[self.__FIELD_TASKIDS] = self.__taskIds
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

    def __init__(self, builder_name: str):
        self.__name = builder_name
        self.__success = False
        self.__changed = False
        self.__counter: int = 0
        self.__taskIds = list()
        self.__changes = dict()
        self.__changes[self.__name + self.__FIELD_CHANGE_LIST] = list()

    def add_change(self, change: CvApiResult):
        if change.success:
            self.__success = change.success
            self.__changed = change.changed
            self.__taskIds += change.taskIds
            self.__counter += change.count
            self.__changes[self.__name + self.__FIELD_CHANGE_LIST].append(change.name)
        # self.__changes[change.name] = {
        #     change.name: change.count, change.name + self.__FIELD_CHANGE_LIST: change.list_changes}

    @property
    def changes(self):
        # self.__changes['name'] = self.__name
        self.__changes[self.__FIELD_SUCCESS] = self.__success
        self.__changes[self.__FIELD_CHANGED] = self.__changed
        self.__changes[self.__FIELD_TASKIDS] = self.__taskIds
        self.__changes[self.__name + self.__FIELD_COUNT] = self.__counter
        return self.__changes

    @property
    def name(self):
        return self.__name
