#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import traceback
import logging
import random
import string
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas import v3 as schema
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import validate_json_schema
try:
    from cvprac.cvp_client_errors import CvpRequestError
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info('Start tag_tools module execution')


class CvTagInput(object):
    def __init__(self, tags: dict, schema=schema.SCHEMA_CV_TAG):
        self.__tag = tags
        self.__schema = schema

    @property
    def is_valid(self):
        """
        check_schemas Validate schemas for user's input
        """
        if not validate_json_schema(user_json=self.__tag, schema=self.__schema):
            MODULE_LOGGER.error("Invalid tags input : \n%s", str(self.__tag))
            return False
        return True


class CvTagTools(object):
    """
    CVTagTools Class to manage CloudVision tag related tasks
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module

    def get_serial_num(self, fqdn: str):
        """
        get_serial_num Get serial number from FQDN

        Parameters
        ----------
        fqdn: str
            FQDN of the switch in CloudVision

        Returns
        -------
        str
            serial number of the switch
        """
        device_details = self.__cv_client.api.get_device_by_name(fqdn)
        if "serialNumber" in device_details.keys():
            return device_details["serialNumber"]
        device_details = self.__cv_client.api.get_device_by_name(fqdn, search_by_hostname=True)
        if "serialNumber" in device_details.keys():
            return device_details["serialNumber"]
        self.__ansible.fail_json(msg=f"Error, Device {fqdn} doesn't exists on CV. Check the hostname/fqdn")

    def tasker(self, tags: list, mode: string, auto_create: bool = True):
        """
        tasker Generic entry point to manage tag related tasks

        Parameters
        ----------
        tags: list
            List of tags to create/assign
        mode: string
            create or delete mode for tags
        auto_create: bool, optional
            auto create tags before assign, default: True
        Returns
        -------
        CvAnsibleResponse
            Data structure to pass to ansible module.

        """
        ansible_response = CvAnsibleResponse()
        tag_manager = CvManagerResult(builder_name='tags_manager')

        # create workspace
        my_date = datetime.now()
        datetime_string = my_date.strftime('%Y%m%d_%H%M%S')
        workspace_name_id = "AW_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) + datetime_string
        workspace_id = workspace_name_id

        workspace_name = workspace_name_id
        try:
            self.__cv_client.api.workspace_config(workspace_id, workspace_name)
        except CvpRequestError:
            MODULE_LOGGER.info('Workspace creation failed. User is unauthorized!')
            self.__ansible.fail_json(msg='Workspace creation failed. User is unauthorized!')

        # create tags and assign tags
        for per_device in tags:

            if mode in ('assign', 'unassign', 'delete'):
                if 'device_id' in per_device:
                    device_id = per_device['device_id']
                else:
                    device_name = per_device['device']
                    device_id = self.get_serial_num(device_name)
            tag_type = per_device.keys()
            MODULE_LOGGER.info('tag_type = %s', tag_type)
            if 'device_tags' in tag_type:
                element_type = "ELEMENT_TYPE_DEVICE"
                for dev_tags in per_device['device_tags']:
                    MODULE_LOGGER.info('dev_tags = %s', dev_tags)
                    tag_name = dev_tags['name']
                    tag_val = str(dev_tags['value'])
                    if mode == 'create':
                        MODULE_LOGGER.info('in create')
                        self.__cv_client.api.tag_config(element_type, workspace_id,
                                                        tag_name, tag_val)
                    if mode == 'delete':
                        # unassign tags first
                        self.__cv_client.api.tag_assignment_config(element_type,
                                                                   workspace_id,
                                                                   tag_name,
                                                                   tag_val,
                                                                   device_id,
                                                                   "", remove=True)
                        self.__cv_client.api.tag_config(element_type, workspace_id,
                                                        tag_name, tag_val,
                                                        remove=True)
                    if mode == 'assign' and auto_create:
                        self.__cv_client.api.tag_config(element_type, workspace_id,
                                                        tag_name, tag_val)
                        self.__cv_client.api.tag_assignment_config(element_type,
                                                                   workspace_id,
                                                                   tag_name,
                                                                   tag_val,
                                                                   device_id,
                                                                   "")
                    if mode == 'unassign':
                        self.__cv_client.api.tag_assignment_config(element_type,
                                                                   workspace_id,
                                                                   tag_name,
                                                                   tag_val,
                                                                   device_id, "",
                                                                   remove=True)

            if 'interface_tags' in tag_type:
                element_type = "ELEMENT_TYPE_INTERFACE"
                for intf_tags in per_device['interface_tags']:
                    if mode in ('assign', 'unassign', 'delete'):
                        interface_id = intf_tags['interface']
                    for tag in intf_tags['tags']:
                        tag_name = tag['name']
                        tag_val = str(tag['value'])
                        if mode == 'create':
                            self.__cv_client.api.tag_config(element_type, workspace_id,
                                                            tag_name, tag_val)
                        if mode == 'delete':
                            # unassign tags first
                            self.__cv_client.api.tag_assignment_config(element_type,
                                                                       workspace_id,
                                                                       tag_name,
                                                                       tag_val,
                                                                       device_id,
                                                                       interface_id,
                                                                       remove=True)

                            self.__cv_client.api.tag_config(element_type, workspace_id,
                                                            tag_name, tag_val,
                                                            remove=True)
                        if mode == 'assign' and auto_create:
                            self.__cv_client.api.tag_config(element_type, workspace_id,
                                                            tag_name, tag_val)
                            self.__cv_client.api.tag_assignment_config(element_type,
                                                                       workspace_id,
                                                                       tag_name,
                                                                       tag_val,
                                                                       device_id,
                                                                       interface_id)
                        if mode == 'unassign':
                            self.__cv_client.api.tag_assignment_config(element_type,
                                                                       workspace_id,
                                                                       tag_name,
                                                                       tag_val,
                                                                       device_id,
                                                                       interface_id,
                                                                       remove=True)

        # Start build
        request = 'REQUEST_START_BUILD'
        reques_id = 'b1'
        description = 'Tag management build'
        MODULE_LOGGER.info('starting build')
        self.__cv_client.api.workspace_config(workspace_id=workspace_id,
                                              display_name=workspace_name,
                                              description=description, request=request,
                                              request_id=reques_id)

        # Check workspace build status and proceed only after it finishes building
        # XXX: Handle better timeout
        b = 0
        while b == 0:
            build_id = reques_id
            try:
                request = self.__cv_client.api.workspace_build_status(workspace_id,
                                                                      build_id)
            except CvpRequestError:
                continue
            build_state = request['value']['state']
            if build_state == 'BUILD_STATE_SUCCESS':
                b = b + 1
            if build_state == 'BUILD_STATE_FAIL':
                api_result = CvApiResult(action_name='tag_' + str(workspace_id))
                api_result.changed = False
                api_result.success = False
                tag_manager.add_change(api_result)
                ansible_response.add_manager(tag_manager)
                return ansible_response
            continue

        api_result = CvApiResult(action_name='tag_' + str(workspace_id))
        api_result.changed = True
        api_result.success = True
        api_result.add_entry(f"Changes for 'tag_' + {str(workspace_id)}")

        # Submit workspace
        # XXX: Timeout after 3s and display msg to user to check status on cvp
        request = 'REQUEST_SUBMIT'
        request_id = 's1'
        MODULE_LOGGER.info('submitting build')
        self.__cv_client.api.workspace_config(workspace_id=workspace_id,
                                              display_name=workspace_name,
                                              description=description,
                                              request=request,
                                              request_id=request_id)

        tag_manager.add_change(api_result)
        ansible_response.add_manager(tag_manager)
        return ansible_response
