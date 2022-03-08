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
from typing import List
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas import v3 as schema
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import validate_json_schema
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
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
try:
    import hashlib
    HAS_HASHLIB = True
except ImportError:
    HAS_HASHLIB = False

MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info('Start cv_container_v3 module execution')


class ConfigletInput(object):

    def __init__(self, user_topology: dict, schema=schema.SCHEMA_CV_CONFIGLET):
        self.__topology = user_topology
        self.__schema = schema

    @property
    def is_valid(self):
        """
        check_schemas Validate schemas for user's input
        """
        if not validate_json_schema(user_json=self.__topology, schema=self.__schema):
            MODULE_LOGGER.error("Invalid configlet input : \n%s", str(self.__topology))
            return False
        return True

    @property
    def configlets(self):
        configlets_list = list()
        for configlet_name, configlet_data in self.__topology.items():
            configlets_list.append(
                {'name': configlet_name, 'config': configlet_data})
        return configlets_list


class CvConfigletTools(object):
    def __init__(self, cv_connection, ansible_module: AnsibleModule = None):
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
            a boolean to indicate if there is a diff between them, along with
            a unified diff list.
            Boolean - False if the sequences are identical, True if they are not.
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
        # Calculate and compare hash values to produce the boolean.
        fromHash = hashlib.sha1(fromText.encode()).hexdigest()
        toHash = hashlib.sha1(toText.encode()).hexdigest()
        if fromHash == toHash:
            cfglet_changed = False
        else:
            cfglet_changed = True
        return [cfglet_changed, diff]

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

    def apply(self, configlet_list: list, present: bool = True, note: str = 'Managed by Ansible AVD'):
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
        to_create = []
        to_update = []
        to_delete = []
        for configlet in configlet_list:
            cv_data = self.get_configlet_data_cv(
                configlet_name=configlet[Api.generic.NAME])
            if present:
                if self.is_present(configlet_name=configlet[Api.generic.NAME]):
                    configlet[Api.generic.KEY] = cv_data[Api.generic.KEY]
                    configlet['diff'] = self._compare(
                        fromText=cv_data[Api.generic.CONFIG], toText=configlet[Api.generic.CONFIG], fromName='CVP', toName='Ansible')
                    configlet['notediff'] = self._compare(
                        fromText=cv_data['note'], toText=note, fromName='CVP', toName='Ansible')
                    MODULE_LOGGER.debug("configlet note diff: %s", str(configlet['notediff']))
                    if (configlet['diff'][0]) is True or (configlet['notediff'][0] is True):
                        to_update.append(configlet)

                else:
                    to_create.append(configlet)
            elif self.is_present(configlet_name=configlet[Api.generic.NAME]):
                configlet[Api.generic.KEY] = cv_data[Api.generic.KEY]
                configlet['diff'] = self._compare(
                    fromText=cv_data[Api.generic.CONFIG], toText=configlet[Api.generic.CONFIG], fromName='CVP', toName='Ansible')
                to_delete.append(configlet)
        ###
        # Structure Ansible Message output
        ###
        updated_configlets = CvManagerResult(builder_name='configlets_updated')
        created_configlets = CvManagerResult(builder_name='configlets_created')
        deleted_configlets = CvManagerResult(builder_name='configlets_deleted')
        update = {}
        delete = {}
        if present and to_create:
            creation = self.create(to_create=to_create, note=note)
            for entry in creation:
                MODULE_LOGGER.debug(
                    'configlet created: %s', str(entry.results))
                created_configlets.add_change(entry)
        if present and to_update:
            update = self.update(to_update=to_update, note=note)
            for entry in update:
                MODULE_LOGGER.debug(
                    'configlet updated: %s', str(entry.results))
                updated_configlets.add_change(entry)
        if not present and to_delete:
            delete = self.delete(to_delete=to_delete)
            for entry in delete:
                MODULE_LOGGER.debug(
                    'configlet deleted: %s', str(entry.results))
                deleted_configlets.add_change(entry)
        response = CvAnsibleResponse()
        response.add_manager(created_configlets)
        response.add_manager(updated_configlets)
        response.add_manager(deleted_configlets)
        MODULE_LOGGER.info('Configlet change result is: %s', str(response.content))
        return response

    def update(self, to_update: list, note: str = 'Managed by Ansible AVD'):
        """
        update Function to update a list of configlets on Cloudvision server

        Update all configlets available in to_update list.
        to_update list shall contain a list of dict with:
        - configlet name
        - configlet id
        - configlet content

        Example
        -------
        >>> update = self.update(to_update=to_update)
        >>> print(update.result)
        [
            {
                'success': True,
                'changed': True,
                'taskIds': [],
                '01TRAINING-alias_count': 1,
                '01TRAINING-alias_list': ['configlet updated']
            }
        ]

        Parameters
        ----------
        to_update : list
            List of configlets to udpate
        note : str, optional
            Note to add to configlet on Cloudvision, by default 'Managed by Ansible AVD'

        Returns
        -------
        list
            List of CvApiResult instances
        """
        response_data = list()
        configlets_notes = note
        for configlet in to_update:
            change_response = CvApiResult(action_name=configlet[Api.generic.NAME])
            if self._ansible.check_mode:
                change_response.add_entry('[check mode] to be updated')
                MODULE_LOGGER.info('[check mode] - Configlet %s updated on cloudvision', str(
                    configlet[Api.generic.NAME]))
                change_response.success = True
                if 'diff' in configlet:
                    change_response.diff = configlet['diff']
                else:
                    change_response.diff = 'unset'
            else:
                try:
                    update_resp = self._cvp_client.api.update_configlet(config=configlet[Api.generic.CONFIG],
                                                                        key=configlet[Api.generic.KEY],
                                                                        name=configlet[Api.generic.NAME],
                                                                        wait_task_ids=True)
                except Exception as error:
                    # Mark module execution with error
                    # Build error message to report in ansible output
                    errorMessage = re.split(':', str(error))[-1]
                    message = "Configlet %s cannot be updated - %s" % (
                        configlet[Api.generic.NAME], errorMessage)
                    # Add logging to ansible response.
                    change_response.add_entry(message)
                    # Generate logging error message
                    MODULE_LOGGER.error('Error updating configlet %s: %s', str(
                        configlet[Api.generic.NAME]), str(error))
                    self._ansible.fail_json(msg=message)
                else:
                    if "errorMessage" in str(update_resp):
                        # Mark module execution with error
                        # Build error message to report in ansible output
                        message = "Configlet %s cannot be updated - %s" % (
                            configlet[Api.generic.NAME], update_resp['errorMessage'])
                        # Add logging to ansible response.
                        change_response.add_entry(message)
                        # Generate logging error message
                        MODULE_LOGGER.error('Error updating configlet %s: %s', str(
                            configlet[Api.generic.NAME]), str(update_resp['errorMessage']))
                        self._ansible.fail_json(msg=message)
                    else:
                        # Inform module a changed has been done
                        change_response.changed = False
                        change_response.success = True
                        # Add note to configlet to mark as managed by Ansible
                        self._cvp_client.api.add_note_to_configlet(
                            configlet[Api.generic.KEY], configlets_notes)
                        # Save configlet diff
                        change_response.add_entry('configlet updated')
                        if 'diff' in configlet:
                            # Change changed flag if diff is True
                            if configlet['diff'] is not None and configlet['diff'][0] is True:
                                change_response.diff = configlet['diff']
                                change_response.changed = True
                                MODULE_LOGGER.info(
                                    'Found diff in configlet %s.', str(configlet[Api.generic.NAME]))
                        if 'notediff' in configlet:
                            if configlet['notediff'] is not None and configlet['notediff'][0] is True:
                                change_response.diff = configlet['notediff']
                                change_response.changed = True
                                MODULE_LOGGER.info(
                                    'Found diff in configlet note of configlet %s.', str(configlet[Api.generic.NAME]))
                        # Collect generated tasks
                        if 'taskIds' in update_resp and len(update_resp['taskIds']) > 0:
                            change_response.taskIds = update_resp['taskIds']
                        MODULE_LOGGER.info(
                            'Configlet %s updated on cloudvision', str(configlet[Api.generic.NAME]))
            response_data.append(change_response)
        return response_data

    def create(self, to_create, note: str = 'Managed by Ansible AVD'):
        """
        create Function to create a list of configlets on Cloudvision server

        Create all configlets listed in to_create list.
        to_create list shall contain a list of dict with:
        - configlet name
        - configlet content

        Example
        -------
        >>> create = self.create(to_create=to_create)
        >>> print(update.result)
        [
            {
                'success': True,
                'changed': True,
                'taskIds': [],
                '01TRAINING-alias_count': 1,
                '01TRAINING-alias_list': ['configlet created']
            }
        ]

        Parameters
        ----------
        to_create : list
            List of configlets to create
        note : str, optional
            Note to add to configlet on Cloudvision, by default 'Managed by Ansible AVD'

        Returns
        -------
        list
            List of CvApiResult instances
        """
        response_data = list()
        configlets_notes = note

        for configlet in to_create:
            # Run section to guess changes when module runs with --check flag
            change_response = CvApiResult(action_name=configlet[Api.generic.NAME])
            if self._ansible.check_mode:
                change_response.add_entry('[check mode] to be created')
                MODULE_LOGGER.info('[check mode] - Configlet %s created on cloudvision', str(
                    configlet[Api.generic.NAME]))
                change_response.success = True
            else:
                try:
                    new_resp = self._cvp_client.api.add_configlet(name=configlet[Api.generic.NAME], config=configlet[Api.generic.CONFIG])
                except Exception as error:
                    # Mark module execution with error
                    # Build error message to report in ansible output
                    errorMessage = re.split(':', str(error))[-1]
                    message = "Configlet %s cannot be created - %s" % (
                        configlet[Api.generic.NAME], errorMessage)
                    # Add logging to ansible response.
                    change_response.add_entry(message)
                    # Generate logging error message
                    MODULE_LOGGER.error('Error creating configlet %s: %s', str(
                        configlet[Api.generic.NAME]), str(error))
                    self._ansible.fail_json(msg=message)
                else:
                    if "errorMessage" in str(new_resp):
                        # Mark module execution with error
                        change_response.success = False
                        # Build error message to report in ansible output
                        message = "Configlet %s cannot be created - %s" % (
                            configlet[Api.generic.NAME], new_resp['errorMessage'])
                        # Add logging to ansible response.
                        change_response.add_entry(message)
                        # Generate logging error message
                        MODULE_LOGGER.error(
                            'Error creating configlet %s: %s', str(configlet[Api.generic.NAME]), str(new_resp))
                        self._ansible.fail_json(msg=message)
                    else:
                        self._cvp_client.api.add_note_to_configlet(new_resp, configlets_notes)
                        change_response.add_entry('configlet created')
                        change_response.changed = True
                        change_response.success = True
                        MODULE_LOGGER.info('Configlet %s created on cloudvision', str(configlet[Api.generic.NAME]))
            response_data.append(change_response)
        return response_data

    def delete(self, to_delete):
        """
        delete Function to delete a list of configlets on Cloudvision server

        Delete all configlets listed in to_create list.
        to_create list shall contain a list of dict with:
        - configlet name
        - configlet key

        Example
        -------
        >>> delete = self.delete(to_delete=to_delete)
        >>> print(update.result)
        [
            {
                'success': True,
                'changed': True,
                'taskIds': [],
                '01TRAINING-alias_count': 1,
                '01TRAINING-alias_list': ['configlet deleted']
            }
        ]

        Parameters
        ----------
        to_create : list
            List of configlets to delete

        Returns
        -------
        list
            List of CvApiResult instances
        """
        response_data = []
        for configlet in to_delete:
            change_response = CvApiResult(action_name=configlet[Api.generic.NAME])
            # Run section to guess changes when module runs with --check flag
            if self._ansible.check_mode:
                change_response.add_entry('[check mode] to be deleted')
                MODULE_LOGGER.info('[check mode] - Configlet %s created on cloudvision', str(
                    configlet[Api.generic.NAME]))
            else:
                try:
                    delete_resp = self._cvp_client.api.delete_configlet(
                        name=configlet[Api.generic.NAME], key=configlet[Api.generic.KEY])
                except Exception as error:
                    # Mark module execution with error
                    # Build error message to report in ansible output
                    errorMessage = re.split(':', str(error))[-1]
                    message = "Configlet %s cannot be deleted - %s" % (
                        configlet[Api.generic.NAME], errorMessage)
                    # Add logging to ansible response.
                    change_response.add_entry(message)
                    # Generate logging error message
                    MODULE_LOGGER.error('Error deleting configlet %s: %s', str(
                        configlet[Api.generic.NAME]), str(error))
                    self._ansible.fail_json(msg=message)
                else:
                    if "errorMessage" in str(delete_resp):
                        # Mark module execution with error
                        # Build error message to report in ansible output
                        message = "Configlet %s cannot be deleted - %s" % (
                            configlet[Api.generic.NAME], delete_resp['errorMessage'])
                        # Add logging to ansible response.
                        change_response.add_entry(message)
                        # Generate logging error message
                        MODULE_LOGGER.error(
                            'Error deleting configlet %s: %s', str(configlet[Api.generic.NAME]), str(delete_resp))
                        self._ansible.fail_json(msg=message)
                    else:
                        change_response.add_entry('configlet deleted')
                        change_response.changed = True
                        change_response.success = True  # noqa # pylint: disable=unused-variable
                        MODULE_LOGGER.info('Configlet %s deleted on cloudvision', str(configlet[Api.generic.NAME]))
            response_data.append(change_response)
        return response_data
