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

import traceback
import logging
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger('arista.cvp.task_tools')
MODULE_LOGGER.info('Start task_tools module execution')


class CvTaskTools():
    """
    CvTaskTools Class to manage Cloudvision tasks execution
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None, check_mode: bool = False):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module
        # self.__check_mode = check_mode

    def __get_task_data(self, task_id: str):
        """
        __get_task_data Get all data for a task from Cloudvision

        Parameters
        ----------
        task_id : str
            Cloudvision Task ID to get

        Returns
        -------
        dict
            Cloudvision data about task
        """
        data: dict = None
        data = self.__cv_client.api.get_task_by_id(task_id=task_id)
        return data

    def is_actionable(self, task_data: dict):
        """
        is_actionable Test if a task is in correct state to be actionned

        Parameters
        ----------
        task_data : dict
            Task data from Cloudvision

        Returns
        -------
        bool
            True if task is actionale, False in other situations
        """
        if task_data is not None:
            return task_data.get("workOrderUserDefinedStatus") in ['Pending']
        return False

    def execute_task(self, task_id: str):
        """
        execute_task Send order to execute task on Cloudvision

        Parameters
        ----------
        task_id : str
            Task ID to execute

        Returns
        -------
        dict
            Cloudvision response
        """
        return self.__cv_client.api.execute_task(task_id)

    def cancel_task(self, task_id: str):
        """
        cancel_task Send order to cancel task on Cloudvision

        Parameters
        ----------
        task_id : str
            Task ID to cancel

        Returns
        -------
        dict
            Cloudvision response
        """
        return self.__cv_client.api.cancel_task(task_id)

    def tasker(self, taskIds_list: list, state: str = 'executed'):
        """
        tasker Generic entry point to manage a set of tasks

        Parameters
        ----------
        taskIds_list : list
            List of task IDs from user input
        state : str, optional
            How to action tasks: executed/cancelled, by default 'executed'

        Returns
        -------
        CvAnsibleResponse
            Data structure to pass to ansible module.
        """
        ansible_response = CvAnsibleResponse()
        tasker_manager = CvManagerResult(builder_name='actions_manager')
        for task_id in taskIds_list:
            api_result = CvApiResult(action_name='task_' + str(task_id))
            if self.is_actionable(task_data=self.__get_task_data(task_id)):
                if self.__ansible.check_mode is False:
                    self.__cv_client.api.add_note_to_task(task_id, "Executed by Ansible")
                    if state == "executed":
                        api_result.add_entry(self.execute_task(task_id))
                        api_result.changed = True
                        api_result.success = True
                    elif state == "cancelled":
                        api_result.add_entry(self.cancel_task(task_id))
                        api_result.changed = True
                        api_result.success = True
                else:
                    api_result.add_entry('check_mode')
                    api_result.changed = False
                    api_result.success = True
                tasker_manager.add_change(api_result)
        ansible_response.add_manager(tasker_manager)
        return ansible_response
