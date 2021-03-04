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
import re
from typing import List, Dict
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
try:
    from cvprac.cvp_client import CvpClient
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()
try:
    import difflib
    HAS_DIFFLIB = True
except ImportError:
    HAS_DIFFLIB = False

MODULE_LOGGER = logging.getLogger('arista.cvp.configlet_tools_v3')
MODULE_LOGGER.info('Start cv_container_v3 module execution')


class ConfigletInput():

    def __init__(self, user_topology: dict):
        self._topology = user_topology

    @property
    def configlets(self):
        configlets_list = list()
        for configlet_name, configlet_data in self._topology.items():
            configlets_list.append(
                {'name': configlet_name, 'config': configlet_data})
        return configlets_list


class CvConfigletTools():
    def __init__(self, cv_connection: CvpClient, ansible_module: AnsibleModule = None):
        self._cvp_client = cv_connection
        self._ansible = ansible_module
        self.WINDOWS_LINE_ENDING = '\r\n'
        self.UNIX_LINE_ENDING = '\n'

    def _str_cleanup_line_ending(self, content: str):
        """
        str_cleanup_line_ending Cleanup line ending to use UNIX style and not Windows style

        Replace line ending from WINDOWS to UNIX

        Parameters
        ----------
        content : string
            String to cleanup

        Returns
        -------
        string
            Cleaned up string.
        """
        if isinstance(content, str):
            return content.replace(self.WINDOWS_LINE_ENDING, self.UNIX_LINE_ENDING)
        return None

    def _compare(self, fromText: List[str], toText: List[str], fromName: str = 'CVP', toName: str = 'Ansible', lines: int = 10):
        """
        _compare - Compare text string in 'fromText' with 'toText' and produce
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
        fromlines = self._str_cleanup_line_ending(content=fromText).splitlines(1)
        tolines = self._str_cleanup_line_ending(content=toText).splitlines(1)
        diff = list(difflib.unified_diff(
            fromlines, tolines, fromName, toName, n=lines))
        textComp = difflib.SequenceMatcher(None, fromText, toText)
        diffRatio = textComp.ratio()
        return [diffRatio, diff]

    def is_present(self, configlet_name: str):
        """
        is_present Test if configlet exists on Cloudvision

        Parameters
        ----------
        configlet_name : str
            Configlet Name

        Returns
        -------
        bool
            True if configlet exists or False if not present
        """
        try:
            response = self._cvp_client.api.get_configlet_by_name(name=configlet_name)
        except CvpApiError:
            return False
        if response is not None:
            return True
        return False

    def get_configlet_data_cv(self, configlet_name: str):
        """
        get_configlet_data_cv Get configlet information from Cloudvision

        Parameters
        ----------
        configlet_name : str
            Configlet Name

        Returns
        -------
        dict
            Configlet information in a dict format
        """
        data = None
        try:
            data = self._cvp_client.api.get_configlet_by_name(name=configlet_name)
        except CvpApiError:
            return None
        return data

    def apply(self, configlet_list: List[Dict[str]], present: bool = True):
        """
        apply Worker to configure configlets on Cloudvision

        Parameters
        ----------
        configlet_list : List[Dict[str]]
            List of configlets to apply on Cloudvision
        present : bool, optional
            Selector to create/update or delete configlets, by default True

        Returns
        -------
        dict
            Cloudvision responses
        """
        to_create = list()
        to_update = list()
        to_delete = list()
        success_status = False
        change_status = False
        if present:
            for configlet in configlet_list:
                cv_data = self.get_configlet_data_cv(
                    configlet_name=configlet['name'])
                if self.is_present(configlet_name=configlet['name']):
                    configlet['key'] = cv_data['key']
                    configlet['diff'] = self._compare(
                        fromText=cv_data['config'], toText=configlet['config'], fromName='CVP', toName='Ansible')
                    to_update.append(configlet)
                else:
                    to_create.append(configlet)
        elif present is False:
            for configlet in configlet_list:
                cv_data = self.get_configlet_data_cv(
                    configlet_name=configlet['name'])
                if self.is_present(configlet_name=configlet['name']):
                    configlet['key'] = cv_data['key']
                    configlet['diff'] = self._compare(
                        fromText=cv_data['config'], toText=configlet['config'], fromName='CVP', toName='Ansible')
                    to_delete.append(configlet)
        ###
        # Structure Ansible Message output
        ###
        creation = dict()
        update = dict()
        delete = dict()
        if present and len(to_create) > 0:
            creation = self.create(to_create=to_create)
            if not creation['failed']:
                success_status = True
            if creation['changed']:
                change_status = True
        if present and len(to_update) > 0:
            update = self.update(to_update=to_update)
            if not update['failed']:
                success_status = True
            if update['changed']:
                change_status = True
        if not present and len(to_delete) > 0:
            delete = self.delete(to_delete=to_delete)
            if not delete['failed']:
                success_status = True
            if delete['changed']:
                change_status = True
        return {'success': success_status, 'changed': change_status, 'creation': creation, 'update': update, 'delete': delete}

    def update(self, to_update: list, note: str = 'Managed by Ansible AVD'):
        response_data = list()
        diff = ''
        flag_failed = False
        flag_changed = False
        taskIds = list()
        configlets_notes = note
        for configlet in to_update:
            if self._ansible.check_mode:
                response_data.append(
                    {configlet['name']: 'will be updated'})
                MODULE_LOGGER.info('[check mode] - Configlet %s updated on cloudvision', str(
                    configlet['name']))
                flag_changed = True
                diff += configlet['name'] + \
                    ":\n" + configlet['diff'] + "\n\n"
            else:
                try:
                    update_resp = self._cvp_client.api.update_configlet(config=configlet['config'],
                                                                        key=configlet['key'],
                                                                        name=configlet['name'],
                                                                        wait_task_ids=True)
                except Exception as error:
                    # Mark module execution with error
                    flag_failed = True
                    # Build error message to report in ansible output
                    errorMessage = re.split(':', str(error))[-1]
                    message = "Configlet %s cannot be updated - %s" % (
                        configlet['name'], errorMessage)
                    # Add logging to ansible response.
                    response_data.append({configlet['name']: message})
                    # Generate logging error message
                    MODULE_LOGGER.error('Error updating configlet %s: %s', str(
                        configlet['name']), str(error))
                else:
                    if "errorMessage" in str(update_resp):
                        # Mark module execution with error
                        flag_failed = True
                        # Build error message to report in ansible output
                        message = "Configlet %s cannot be updated - %s" % (
                            configlet['name'], update_resp['errorMessage'])
                        # Add logging to ansible response.
                        response_data.append(
                            {configlet['name']: message})
                        # Generate logging error message
                        MODULE_LOGGER.error('Error updating configlet %s: %s', str(
                            configlet['name']), str(update_resp['errorMessage']))
                    else:
                        # Inform module a changed has been done
                        flag_changed = True
                        # Add note to configlet to mark as managed by Ansible
                        self._cvp_client.api.add_note_to_configlet(
                            configlet['key'], configlets_notes)
                        # Save result for further traces.
                        response_data.append(
                            {configlet['name']: "success"})
                        # Save configlet diff
                        if 'diff' in configlet:
                            if configlet['diff'] is not None:
                                diff += configlet['name'] + ":\n" +str(configlet['diff'][1]) + "\n\n"
                        # Collect generated tasks
                        if 'taskIds' in update_resp and len(update_resp['taskIds']) > 0:
                            taskIds.append(update_resp['taskIds'])

        return {'changed': flag_changed,
                'failed': flag_failed,
                'update': response_data,
                'diff': diff,
                'taskIds': taskIds}

    def create(self, to_create, note: str = 'Managed by Ansible AVD'):
        response_data = list()
        flag_failed = False
        flag_changed = False
        configlets_notes = note

        for configlet in to_create:
            # Run section to guess changes when module runs with --check flag
            if self._ansible.check_mode:
                response_data.append(
                    {configlet['name']: "will be created"})
                MODULE_LOGGER.info('[check mode] - Configlet %s created on cloudvision', str(
                    configlet['name']))
                flag_changed = True
            else:
                try:
                    new_resp = self._cvp_client.api.add_configlet(name=configlet['name'], config=configlet['config'])
                except Exception as error:
                    # Mark module execution with error
                    flag_failed = True
                    # Build error message to report in ansible output
                    errorMessage = re.split(':', str(error))[-1]
                    message = "Configlet %s cannot be created - %s" % (
                        configlet['name'], errorMessage)
                    # Add logging to ansible response.
                    response_data.append({configlet['name']: message})
                    # Generate logging error message
                    MODULE_LOGGER.error('Error creating configlet %s: %s', str(
                        configlet['name']), str(error))
                else:
                    if "errorMessage" in str(new_resp):
                        # Mark module execution with error
                        flag_failed = True
                        # Build error message to report in ansible output
                        message = "Configlet %s cannot be created - %s" % (
                            configlet['name'], new_resp['errorMessage'])
                        # Add logging to ansible response.
                        response_data.append({configlet['name']: message})
                        # Generate logging error message
                        MODULE_LOGGER.error(
                            'Error creating configlet %s: %s', str(configlet['name']), str(new_resp))
                    else:
                        self._cvp_client.api.add_note_to_configlet(new_resp, configlets_notes)
                        flag_changed = True  # noqa # pylint: disable=unused-variable
                        response_data.append({configlet['name']: "success"})
                        MODULE_LOGGER.info('Configlet %s created on cloudvision', str(configlet['name']))

        return {'changed': flag_changed,
                'failed': flag_failed,
                'create': response_data,
                'taskIds': []}

    def delete(self, to_delete):
        response_data = list()
        flag_failed = False
        flag_changed = False
        for configlet in to_delete:
                # Run section to guess changes when module runs with --check flag
            if self._ansible.check_mode:
                response_data.append(
                    {configlet['name']: "will be created"})
                MODULE_LOGGER.info('[check mode] - Configlet %s created on cloudvision', str(
                    configlet['name']))
                flag_changed = True
            else:
                try:
                    delete_resp = self._cvp_client.api.delete_configlet(
                        name=configlet['name'], key=configlet['key'])
                except Exception as error:
                    # Mark module execution with error
                    flag_failed = True
                    # Build error message to report in ansible output
                    errorMessage = re.split(':', str(error))[-1]
                    message = "Configlet %s cannot be deleted - %s" % (
                        configlet['name'], errorMessage)
                    # Add logging to ansible response.
                    response_data.append({configlet['name']: message})
                    # Generate logging error message
                    MODULE_LOGGER.error('Error deleting configlet %s: %s', str(
                        configlet['name']), str(error))
                else:
                    if "errorMessage" in str(delete_resp):
                        # Mark module execution with error
                        flag_failed = True
                        # Build error message to report in ansible output
                        message = "Configlet %s cannot be deleted - %s" % (
                            configlet['name'], delete_resp['errorMessage'])
                        # Add logging to ansible response.
                        response_data.append({configlet['name']: message})
                        # Generate logging error message
                        MODULE_LOGGER.error(
                            'Error deleting configlet %s: %s', str(configlet['name']), str(delete_resp))
                    else:
                        flag_changed = True  # noqa # pylint: disable=unused-variable
                        response_data.append({configlet['name']: "success"})
                        MODULE_LOGGER.info('Configlet %s deleted on cloudvision', str(configlet['name']))

        return {'changed': flag_changed,
                'failed': flag_failed,
                'update': response_data,
                'taskIds': []}
