#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# flake8: noqa: W1202
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
from ansible_collections.arista.cvp.plugins.module_utils.generic_tools import CvElement
import ansible_collections.arista.cvp.plugins.module_utils.schema_v3 as schema
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()
try:
    import jsonschema  # noqa # pylint: disable=unused-import
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

MODULE_LOGGER = logging.getLogger('arista.cvp.device_tools_v3')
MODULE_LOGGER.info('Start device_tools module execution')


# ------------------------------------------ #
# Fields name to use in classes
# ------------------------------------------ #

FIELD_FQDN = 'fqdn'
FIELD_SYSMAC = 'systemMacAddress'
FIELD_SERIAL = 'serialNumber'
FIELD_CONFIGLETS = 'configlets'
FIELD_ID = 'key'
FIELD_CONTAINER_NAME = 'containerName'
FIELD_PARENT_NAME = 'parentContainerName'
FIELD_PARENT_ID = 'parentContainerId'
# Not yet implemented
FIELD_IMAGE_BUNDLE = 'image_bundle'
UNDEFINED_CONTAINER = 'undefined_container'


class DeviceElement(object):
    """
    DeviceElement Object to represent Device Element from user inventory
    """

    def __init__(self, data: dict):
        self.__data = data
        self.__fqdn = self.__data[FIELD_FQDN] if FIELD_FQDN in self.__data else None
        self.__sysmac = self.__data[FIELD_SYSMAC] if FIELD_SYSMAC in self.__data else None
        self.__serial = self.__data[FIELD_SERIAL] if FIELD_SERIAL in self.__data else None
        self.__container = self.__data[FIELD_PARENT_NAME]
        self.__image_bundle = []
        self.__current_parent_container_id = None
        if FIELD_IMAGE_BUNDLE in self.__data:
            self.__image_bundle = data[FIELD_IMAGE_BUNDLE]
        if FIELD_SYSMAC in data:
            self.__sysmac = data[FIELD_SYSMAC]
        if FIELD_SERIAL in data:
            self.__serial = data[FIELD_SERIAL]

    @property
    def fqdn(self):
        """
        fqdn Getter for FQDN value

        Returns
        -------
        str
            FQDN configured for the device
        """
        return self.__fqdn

    @property
    def system_mac(self):
        """
        system_mac Getter for SystemMac value

        Returns
        -------
        str
            SystemMac address for the device
        """
        return self.__sysmac

    @system_mac.setter
    def system_mac(self, mac: str):
        """
        system_mac Setter for SystemMac address

        Parameters
        ----------
        mac : str
            systemMac address to configure on device
        """
        self.__sysmac = mac

    @property
    def serial_number(self):
        """
        serial_number Getter for device serial number

        Returns
        -------
        str
            Device serial number
        """
        return self.__serial

    @property
    def container(self):
        """
        container Getter for container

        Returns
        -------
        str
            Name of the container
        """
        return self.__container

    @property
    def configlets(self):
        """
        configlets Getter for list of configlets

        Returns
        -------
        list
            List of configlets name
        """
        if FIELD_CONFIGLETS in self.__data:
            return self.__data[FIELD_CONFIGLETS]
        return []

    @property
    def parent_container_id(self):
        """
        parent_container_id Getter for parent container ID

        Returns
        -------
        str
            Name of the parent Container
        """
        return self.__current_parent_container_id

    @parent_container_id.setter
    def parent_container_id(self, id):
        """
        parent_container_id Setter for parent container ID

        Parameters
        ----------
        id : str
            parent container ID to configure on device
        """
        self.__current_parent_container_id = id

    @property
    def info(self):
        """
        info Provides all information from device

        Returns
        -------
        dict
            All information related to device.
        """
        res = dict()
        res[FIELD_FQDN] = self.__fqdn
        if self.__serial is not None:
            res[FIELD_SERIAL] = self.__serial
        if self.__sysmac is not None:
            res[FIELD_SYSMAC] = self.__sysmac
            res[FIELD_ID] = self.__sysmac
        res[FIELD_PARENT_NAME] = self.__container
        if FIELD_CONFIGLETS in self.__data:
            res[FIELD_CONFIGLETS] = self.__data[FIELD_CONFIGLETS]
        else:
            res[FIELD_CONFIGLETS] = []
        # res[FIELD_PARENT_ID] = self.__current_parent_container_id
        return res


class DeviceInventory(object):
    """
    DeviceInventory Local User defined inventory
    """

    def __init__(self, data: list, schema=schema.SCHEMA_CV_DEVICE, search_method: str = FIELD_FQDN):
        self.__inventory = list()
        self.__data = data
        self.__schema = schema
        self.search_method = search_method
        for entry in data:
            if FIELD_FQDN in entry:
                self.__inventory.append(DeviceElement(data=entry))

    @property
    def is_valid(self):
        """
        check_schemas Validate schemas for user's input
        """
        if not schema.validate_cv_inputs(user_json=self.__data, schema=self.__schema):
            MODULE_LOGGER.error(
                "Invalid configlet input : \n%s", str(self.__data))
            return False
        return True

    @property
    def devices(self):
        """
        devices Getter to list all devices in inventory

        Returns
        -------
        list:
            A list of DeviceElement
        """
        return self.__inventory

    def get_device(self, device_string: str, search_method: str = FIELD_FQDN):
        """
        get_device Extract device from inventory

        Parameters
        ----------
        device_string : str
            Data to lookup device from inventory. Can be FQDN or sysMac field
        search_method : str, optional
            Field to search for device, by default fqdn

        Returns
        -------
        DeviceElement
            Data structure with device information.
        """
        # Lookup using systemMacAddress
        if self.search_method is FIELD_SYSMAC or search_method is FIELD_SYSMAC:
            for device in self.__inventory:
                if device.system_mac == device_string:
                    return device
        # Cover search by fqdn or any unsupported options
        else:
            for device in self.__inventory:
                if device.fqdn == device_string:
                    return device
        return None


class CvDeviceTools(object):
    """
    CvDeviceTools Object to operate Device operation on Cloudvision
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None, search_by: str = FIELD_FQDN, check_mode: bool = False):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module
        self.__search_by = search_by
        self.__configlets_and_mappers_cache = None
        self.__check_mode = check_mode

    # ------------------------------------------ #
    # Getters & Setters
    # ------------------------------------------ #

    @property
    def search_by(self):
        """
        search_by Getter to expose search mechanism

        Returns
        -------
        str
            Field name used for search
        """
        return self.__search_by

    @search_by.setter
    def search_by(self, mode: str):
        """
        search_by Setter to configure how object are search

        Parameters
        ----------
        mode : str
            Field name to use for search
        """
        self.__search_by = mode

    # ------------------------------------------ #
    # Private functions
    # ------------------------------------------ #

    def __get_device(self, search_value: str, search_by: str = FIELD_FQDN):
        """
        __get_device Method to get data from Cloudvision

        Search on cloudvision information related to given device.

        Parameters
        ----------
        search_value : str
            Device content to look for (FQDN or SYSMAC)
        search_by : str, optional
            Field to use to search information, by default FQDN

        Returns
        -------
        dict
            Information returns by Cloudvision
        """
        cv_data: dict = dict()
        if search_by == FIELD_FQDN:
            cv_data = self.__cv_client.api.get_device_by_name(fqdn=search_value)
        if search_by == FIELD_SYSMAC:
            cv_data = self.__cv_client.api.get_device_by_mac(device_mac=search_value)
        return cv_data

    def __get_configlet_info(self, configlet_name: str):
        """
        __get_configlet_info Provides mechanism to get information about a configlet.

        Extract information from CV configlet mapper and save as a cache in instance.

        Parameters
        ----------
        configlet_name : str
            Name of the configlet

        Returns
        -------
        dict
            Configlet data
        """
        if self.__configlets_and_mappers_cache is None:
            self.__configlets_and_mappers_cache = self.__cv_client.api.get_configlets_and_mappers()
        for configlet in self.__configlets_and_mappers_cache['data']['configlets']:
            if configlet_name == configlet['name']:
                return configlet
        return None

    # ------------------------------------------ #
    # Get CV data functions
    # ------------------------------------------ #

    def get_device_facts(self, device_lookup: str):
        """
        get_device_facts Public method to get device information from Cloudvision

        Parameters
        ----------
        device_lookup : str
            Name of the device to look for

        Returns
        -------
        dict
            Data from Cloudvision
        """
        data = self.__get_device(
            search_value=device_lookup, search_by=self.__search_by)
        return data

    def get_device_id(self, device_lookup: str):
        """
        get_device_id Retrieve device ID from Cloudvision

        Parameters
        ----------
        device_lookup : str
            Name of the device

        Returns
        -------
        str
            Device ID
        """
        data = self.get_device_facts(device_lookup=device_lookup)
        if data is not None:
            return data[FIELD_SYSMAC]
        return None

    def get_device_configlets(self, device_lookup: str):
        """
        get_device_configlets Retrieve configlets attached to a device

        Parameters
        ----------
        device_lookup : str
            Name of the device

        Returns
        -------
        list
            List of CvElement with KEY and NAME of every configlet.
        """
        if self.__search_by == FIELD_FQDN:
            configlet_list = list()
            # get_configlets_by_device_id
            try:
                device_id = self.get_device_id(device_lookup=device_lookup)
            except CvpApiError:
                MODULE_LOGGER.error('Error getting device ID from cloudvision')
            else:
                if device_id is None:
                    MODULE_LOGGER.error('Error cannot get device ID from Cloudvision')
                configlets_data = self.__cv_client.api.get_configlets_by_device_id(
                    mac=device_id)
                for configlet in configlets_data:
                    configlet_list.append(CvElement(cv_data=configlet))
                return configlet_list
        return None

    def get_device_container(self, device_lookup: str):
        """
        get_device_container Retrieve container where device is attached.

        Parameters
        ----------
        device_lookup : str
            Device name to look for

        Returns
        -------
        dict
            A dict with key and name
        """
        cv_data = self.get_device_facts(device_lookup=device_lookup)
        if cv_data is not None:
            return {FIELD_PARENT_ID: cv_data[FIELD_PARENT_ID], FIELD_PARENT_NAME: cv_data[FIELD_CONTAINER_NAME]}
        return None

    def get_container_info(self, container_name: str):
        """
        get_container_info Retrieve container information from Cloudvision

        Parameters
        ----------
        container_name : str
            Name of the container

        Returns
        -------
        dict
            Data from Cloudvision
        """
        try:
            resp = self.__cv_client.api.get_container_by_name(name=str(container_name))
        except CvpApiError:
            MODULE_LOGGER.debug(
                'Error getting container ID from Cloudvision')
        else:
            return resp
        return None

    def get_container_current(self, device_mac: str):
        """
        get_container_current Retrieve name of current container where device is attached to

        Parameters
        ----------
        device_mac : str
            Mac address of the device to lokk for container

        Returns
        -------
        dict
            A dict with key and name
        """
        container_id = self.__cv_client.api.get_device_by_mac(device_mac=device_mac)
        if FIELD_PARENT_ID in container_id:
            return {'name': container_id[FIELD_CONTAINER_NAME], 'key': container_id[FIELD_PARENT_ID]}
        else:
            return None

    def refresh_systemMacAddress(self, user_inventory: DeviceInventory):
        """
        refresh_systemMacAddress Get System Mac Address from Cloudvision to update missing information

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user and that need to be refreshed

        Returns
        -------
        DeviceInventory
            Updated device inventory
        """
        device: DeviceElement = None
        user_result: list = list()
        for device in user_inventory.devices:
            if device.system_mac is None and device.fqdn is not None:
                system_mac = self.get_device_facts(
                    device_lookup=device.fqdn)[FIELD_SYSMAC]
                MODULE_LOGGER.debug(
                    'Get sysmac %s for device %s', str(device.fqdn), str(system_mac))
                device.system_mac = system_mac
                user_result.append(device.info)
        MODULE_LOGGER.warning('Update list is: %s', str(user_result))
        return DeviceInventory(data=user_result)

    def check_device_exist(self, user_inventory: DeviceInventory, search_mode):
        """
        check_device_exist Check if the devices specified in the user_inventory exist in CVP.

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user
        search_mode : str
            Search method to get device information from Cloudvision
        Returns
        -------
        list
            List of devices not present in CVP
        """
        MODULE_LOGGER.debug('Check if all the devices specified exist in CVP')
        device_not_present: list = list()
        for device in user_inventory.devices:
            if self.__search_by == FIELD_FQDN or search_mode == FIELD_FQDN:
                if self.is_device_exist(device.fqdn) == False:
                    device_not_present.append(device.fqdn)
                    MODULE_LOGGER.error('Device not present in CVP but in the user_inventory: %s', device.fqdn)

            elif self.__search_by == FIELD_SYSMAC:
                if self.is_device_exist(device.system_mac) == False:
                    device_not_present.append(device.system_mac)
                    MODULE_LOGGER.error('Device not present in CVP but in the user_inventory: %s', device.system_mac)
        return device_not_present

    # ------------------------------------------ #
    # Workers function
    # ------------------------------------------ #

    def manager(self, user_inventory: DeviceInventory, search_mode: str = FIELD_FQDN, state: str = 'present', apply_mode: str = 'loose'):
        """
        manager Main entry point to support all device

        Entry point to start following actions:
        - Deploy devices
        - Move deployed devices to container
        - Attach configlets to devices

        Parameters
        ----------
        user_inventory : DeviceInventory
            User defined inventory from Ansible input
        search_mode : str, optional
            Search method to get device information from Cloudvision, by default FQDN
        state : str, optional
            Define the desired state of the device (present, absent or factory_reset)
        apply_mode: str, optional
            Define how manager will apply configlets to device: loose (only attach listed configlet) or strict (attach listed configlet, remove others)

        Returns
        -------
        dict
            All Ansible output formated using CvAnsibleResponse
        """
        response = CvAnsibleResponse()

        cv_remove = CvManagerResult(builder_name='devices_removed')
        cv_deploy = CvManagerResult(builder_name='devices_deployed')
        cv_move = CvManagerResult(builder_name='devices_moved')
        cv_configlets_attach = CvManagerResult(builder_name='configlets_attached')
        cv_configlets_detach = CvManagerResult(builder_name='configlets_detached')

        # Check if the devices defined exist in CVP
        list_non_existing_devices = self.check_device_exist(user_inventory=user_inventory, search_mode=search_mode)
        if list_non_existing_devices is not None and len(list_non_existing_devices) > 0:
            error_message = 'Error - the following devices do not exist in CVP {} but are defined in the playbook. \
            \nMake sure that the devices are provisioned and defined with the full fqdn name (including the domain name) if needed.'.format(str(list_non_existing_devices))
            MODULE_LOGGER.error(error_message)
            self.__ansible.fail_json(msg=error_message)


        # Need to collect all missing device systemMacAddress
        # deploy needs to locate devices by mac-address
        if self.__search_by == FIELD_FQDN or search_mode == FIELD_FQDN:
            user_inventory = self.refresh_systemMacAddress(user_inventory=user_inventory)

        if state == 'absent':
            action_result = self.remove_device(user_inventory=user_inventory)
            ## TODO: Add action result in add_change as below.
            if action_result is not None:
                for update in action_result:
                    cv_remove.add_change(change=update)

        elif state == 'factory_reset':
            action_result = self.factory_reset_device(user_inventory=user_inventory)
            if action_result is not None:
                for update in action_result:
                    cv_remove.add_change(change=update)
            # MODULE_LOGGER.error('Module factory reset not yet implemented')
            # self.__ansible.fail_json(msg='State==factory_reset is not yet supported!')

        # State is present
        else: 
            action_result = self.deploy_device(user_inventory=user_inventory)
            if action_result is not None:
                for update in action_result:
                    cv_deploy.add_change(change=update)

            action_result = self.move_device(user_inventory=user_inventory)
            if action_result is not None:
                for update in action_result:
                    cv_move.add_change(change=update)

            action_result = self.apply_configlets(user_inventory=user_inventory)
            if action_result is not None:
                for update in action_result:
                    cv_configlets_attach.add_change(change=update)

            if apply_mode == 'strict':
                action_result = self.detach_configlets(
                    user_inventory=user_inventory)
                if action_result is not None:
                    for update in action_result:
                        cv_configlets_detach.add_change(change=update)

        response.add_manager(cv_remove)
        response.add_manager(cv_move)
        response.add_manager(cv_deploy)
        response.add_manager(cv_configlets_attach)
        response.add_manager(cv_configlets_detach)

        return response.content

    def factory_reset_device(self, user_inventory: DeviceInventory):
        """
        factory_reset_device Entry point to factory_reset a device.

        Execute API calls to factory reset the device

        Parameters
        ----------
        user_inventory : DeviceInventory
            Ansible inventory to configure on Cloudvision

        Returns
        -------
        list
            List of CvApiResult for all API calls
        """
        results = list()
        for device in user_inventory.devices:
            result_data = CvApiResult(action_name='reset_device_{}'.format(device.fqdn))
            if device.system_mac is not None:
                try:
                    container_current = self.get_container_current(device_mac=device.system_mac)
                    
                    # Factory reset from the undefined container is not supported
                    if container_current['key'] == UNDEFINED_CONTAINER:
                        msg = "Unable to factory_reset the device [{}] - Factory reset a device under the undefined_container is not supported.  \
                            \nPlease move first the device to a container.".format(device.fqdn)
                        MODULE_LOGGER.error(msg)
                        self.__ansible.fail_json(msg=msg)

                    msg = "Device Reset: " + device.fqdn
                    data = {'data': [{'info': msg,
                          'infoPreview': msg,
                          'action': 'reset',
                          'nodeType': 'netelement',
                          'nodeId': device.system_mac,
                          'toId': UNDEFINED_CONTAINER,
                          'fromId': container_current['key'],
                          'nodeName': device.fqdn,
                          'fromName': container_current['name'],
                          'toIdType': 'container'}]}
                    MODULE_LOGGER.debug("data: " + str(data))
                    
                    resp1 = self.__cv_client.api._add_temp_action(data=data)
                    MODULE_LOGGER.debug("Resp1: " + str(resp1))
                    resp2 = self.__cv_client.api._save_topology_v2([])
                    MODULE_LOGGER.debug("Resp2: " + str(resp2))

                except CvpApiError:
                    error_message = 'Error deleting device {}'.format(device.fqdn)
                    MODULE_LOGGER.error(error_message)
                    self.__ansible.fail_json(msg=error_message)
                else: 
                    result_data.changed = True
                    result_data.success = True
                    result_data.add_entry('factory_reset-{}'.format(device.fqdn))
                    result_data.taskIds = resp2['data']['taskIds']
                    results.append(result_data)
            else: 
                MODULE_LOGGER.error("Unable to factory_reset device  " + device.fqdn + " - No mac address found for this device.")
        return results

    def remove_device(self, user_inventory: DeviceInventory):
        """
        remove_device Entry point to remove device from the provisioning page

        Execute API calls to remove devices from the provisioning page

        Parameters
        ----------
        user_inventory : DeviceInventory
            Ansible inventory to configure on Cloudvision

        Returns
        -------
        list
            List of CvApiResult for all API calls
        """
        results = list()
        for device in user_inventory.devices:
            result_data = CvApiResult(action_name='remove_device_{}'.format(device.fqdn))
            if device.system_mac is not None:
                try:
                    resp = self.__cv_client.api.delete_device(device_mac=device.system_mac)
                except CvpApiError:
                    error_message = 'Error deleting device {}'.format(device.fqdn)
                    MODULE_LOGGER.error(error_message)
                    self.__ansible.fail_json(msg=error_message)
                else: 
                    result_data.changed = True
                    result_data.success = True
                    result_data.add_entry('remove-{}'.format(device.fqdn))
                    results.append(result_data)
            else: 
                MODULE_LOGGER.error("Unable to delete device  " + device.fqdn + " - No mac address found for this device.")
        return results

    def move_device(self, user_inventory: DeviceInventory):
        """
        move_device Entry point to move device from one container to another container

        Execute API calls to move a device from a container to another one.
        This method is not defined to support onboarding process

        Parameters
        ----------
        user_inventory : DeviceInventory
            Ansible inventory to configure on Cloudvision

        Returns
        -------
        list
            List of CvApiResult for all API calls
        """
        results = list()
        for device in user_inventory.devices:
            result_data = CvApiResult(
                action_name='{}_to_{}'.format(device.fqdn, *device.container))
            if device.system_mac is not None:
                new_container_info = self.get_container_info(container_name=device.container)
                if new_container_info is None:
                    error_message = 'The target container \'{}\' for the device \'{}\' does not exist on CVP.'.format(device.container, device.fqdn)
                    MODULE_LOGGER.error(error_message)
                    self.__ansible.fail_json(msg=error_message)
                current_container_info = self.get_container_current(device_mac=device.system_mac)
                MODULE_LOGGER.debug("Current container is: " + current_container_info['name'])
                # Move devices when they are not in undefined container
                if (current_container_info is not None
                    and current_container_info['name'] != UNDEFINED_CONTAINER
                        and current_container_info['name'] != device.container):
                    if self.__check_mode:
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = ['unsupported_in_check_mode']
                    else:
                        try:
                            resp = self.__cv_client.api.move_device_to_container(app_name='CvDeviceTools.move_device',
                                                                                 device=device.info,
                                                                                 container=new_container_info,
                                                                                 create_task=True)
                        except CvpApiError:
                            error_message = 'Error to move device {} to container {}'.format(device.fqdn, *device.container)
                            MODULE_LOGGER.error(error_message)
                            self.__ansible.fail_json(msg=error_message)
                        else:
                            if resp['data']['status'] == 'success':
                                result_data.changed = True
                                result_data.success = True
                                result_data.taskIds = resp['data']['taskIds']

                    result_data.add_entry('{}-{}'.format(device.fqdn, *device.container))
            results.append(result_data)
        return results

    def apply_configlets(self, user_inventory: DeviceInventory):
        """
        apply_configlets Entry point to a list of configlets to device

        Execute API calls to attach configlets to device
        This method is not defined to support onboarding process

        Parameters
        ----------
        user_inventory : DeviceInventory
            Ansible inventory to configure on Cloudvision

        Returns
        -------
        list
            List of CvApiResult for all API calls
        """
        results = list()
        for device in user_inventory.devices:
            result_data = CvApiResult(
                action_name=device.fqdn + '_configlet_attached')
            current_container_info = self.get_container_current(
                device_mac=device.system_mac)
            if (device.configlets is not None
                    and current_container_info['name'] != UNDEFINED_CONTAINER):
                # get configlet information from CV
                configlets_info = list()
                configlets_attached = self.get_device_configlets(
                    device_lookup=device.fqdn)
                MODULE_LOGGER.debug('Attached configlets for device %s : %s', str(device.fqdn), str(configlets_attached))
                # For each configlet not in the list, add to list of configlets to remove
                for configlet in device.configlets:
                    if configlet not in [x.name for x in configlets_attached]:
                        new_configlet = self.__get_configlet_info(configlet_name=configlet)
                        if new_configlet is None:
                            error_message = "The configlet \'{}\' defined to be applied on the device \'{}\' does not exist on the CVP server.".format(str(configlet), str(device.fqdn))
                            MODULE_LOGGER.error(error_message)
                            self.__ansible.fail_json(msg=error_message)
                        else:
                            configlets_info.append(new_configlet)
                # get device facts from CV
                device_facts = dict()
                if self.__search_by == FIELD_FQDN:
                    device_facts = self.__cv_client.api.get_device_by_name(
                        fqdn=device.fqdn)
                # Attach configlets to device
                if len(configlets_info) > 0:
                    try:
                        resp = self.__cv_client.api.apply_configlets_to_device(app_name='CvDeviceTools.apply_configlets',
                                                                               dev=device_facts,
                                                                               new_configlets=configlets_info,
                                                                               create_task=True)
                    except CvpApiError:
                        MODULE_LOGGER.error('Error applying configlets to device')
                        self.__ansible.fail_json(msg='Error applying configlets to device')
                    else:
                        if resp['data']['status'] == 'success':
                            result_data.changed = True
                            result_data.success = True
                            result_data.taskIds = resp['data']['taskIds']
                            result_data.add_entry('{} adds {}'.format(
                                device.fqdn, *device.configlets))
                    result_data.add_entry('{} to {}'.format(device.fqdn, *device.container))
                else:
                    result_data.name = result_data.name + ' - nothing attached'
                results.append(result_data)
        return results

    def detach_configlets(self, user_inventory: DeviceInventory):
        results = list()
        for device in user_inventory.devices:
            result_data = CvApiResult(
                action_name=device.fqdn + '_configlet_removed')
            # FIXME: Should we ignore devices listed with no configlets ?
            if device.configlets is not None:
                device_facts = dict()
                if self.__search_by == FIELD_FQDN:
                    device_facts = self.__cv_client.api.get_device_by_name(
                        fqdn=device.fqdn)
                configlets_to_remove = list()
                # get list of configured configlets
                configlets_attached = self.get_device_configlets(device_lookup=device.fqdn)
                # Pour chaque configlet not in the list, add to list of configlets to remove
                for configlet in configlets_attached:
                    if configlet.name not in device.configlets:
                        MODULE_LOGGER.info('Configlet %s is added to detach list', str(configlet.name))
                        result_data.name = result_data.name + ' - ' + configlet.name
                        configlets_to_remove.append(configlet.data)
                # Detach configlets to device
                if len(configlets_to_remove) > 0:
                    try:
                        resp = self.__cv_client.api.remove_configlets_from_device(app_name='CvDeviceTools.detach_configlets',
                                                                                  dev=device_facts,
                                                                                  del_configlets=configlets_to_remove,
                                                                                  create_task=True)
                    except CvpApiError as catch_error:
                        MODULE_LOGGER.error('Error applying configlets to device: %s', str(catch_error))
                        self.__ansible.fail_json(msg='Error detaching configlets from device ' + device.fqdn + ': ' + catch_error)
                    else:
                        if resp['data']['status'] == 'success':
                            result_data.changed = True
                            result_data.success = True
                            result_data.taskIds = resp['data']['taskIds']
                            result_data.add_entry('{} removes {}'.format(
                                device.fqdn, *device.configlets))
                else:
                    result_data.name = result_data.name + ' - nothing detached'
                results.append(result_data)
        return results

    def remove_configlets(self, user_inventory: DeviceInventory):
        """
        remove_configlets UNSUPPORTED and NOT TESTED YET
        """
        results = list()
        for device in user_inventory.devices:
            result_data = CvApiResult(action_name=device.fqdn + '_configlet_removed')
            if device.configlets is not None:
                # get configlet information from CV
                configlets_info = list()
                for configlet in device.configlets:
                    configlets_info.append(
                        self.__get_configlet_info(configlet_name=configlet))
                # get device facts from CV
                device_facts = dict()
                if self.__search_by == FIELD_FQDN:
                    device_facts = self.__cv_client.api.get_device_by_name(
                        fqdn=device.fqdn)
                # Attach configlets to device
                try:
                    resp = self.__cv_client.api.remove_configlets_from_device(app_name='CvDeviceTools.remove_configlets',
                                                                              dev=device_facts,
                                                                              del_configlets=configlets_info,
                                                                              create_task=True)
                except CvpApiError:
                    MODULE_LOGGER.error('Error removing configlets to device')
                    self.__ansible.fail_json(msg='Error removing configlets to device')
                else:
                    if resp['data']['status'] == 'success':
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = resp['data']['taskIds']
                        result_data.add_entry('{} removes {}'.format(
                            device.fqdn, *device.configlets))
            results.append(result_data)
        return results

    def deploy_device(self, user_inventory: DeviceInventory):
        """
        deploy_device Entry point to deploy a device in ZTP mode

        Execute API calls to move a device from undefined to a container and
        attached configlets to this device as well.
        This method is defined to ONLY support onboarding process

        Parameters
        ----------
        user_inventory : DeviceInventory
            Ansible inventory to configure on Cloudvision

        Returns
        -------
        list
            List of CvApiResult for all API calls
        """
        results = list()
        for device in user_inventory.devices:
            result_data = CvApiResult(action_name=device.fqdn + '_deployed')
            if device.system_mac is not None:
                configlets_info = list()
                for configlet in device.configlets:
                    new_configlet = self.__get_configlet_info(configlet_name=configlet)
                    if new_configlet is None:
                        error_message = "The configlet \'{}\' defined to be applied on the device \'{}\' does not exist on the CVP server.".format(str(configlet), str(device.fqdn))
                        MODULE_LOGGER.error(error_message)
                        self.__ansible.fail_json(msg=error_message)
                    else:
                        configlets_info.append(new_configlet)
                # Move devices when they are not in undefined container
                current_container_info = self.get_container_current(
                    device_mac=device.system_mac)
                MODULE_LOGGER.debug('Device {} is currently under {}'.format(
                    device.fqdn, *current_container_info['name']))
                device_info = self.get_device_facts(device_lookup=device.fqdn)
                if (current_container_info['name'] == 'Undefined'):
                    if self.__check_mode:
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = ['unsupported_in_check_mode']
                    else:
                        ## Check if the target container exists
                        target_container_info = self.get_container_info(container_name=device.container)
                        if target_container_info is None:
                            error_message = 'The target container \'{}\' for the device \'{}\' does not exist on CVP.'.format(device.container, device.fqdn)
                            MODULE_LOGGER.error(error_message)
                            self.__ansible.fail_json(msg=error_message)
                        try:
                            MODULE_LOGGER.debug('Ansible is going to deploy device %s in container %s with configlets %s',
                                                str(device.fqdn),
                                                str(device.container),
                                                str(configlets_info))
                            resp = self.__cv_client.api.deploy_device(app_name='CvDeviceTools.deploy',
                                                                      device=device_info,
                                                                      container=device.container,
                                                                      configlets=configlets_info,
                                                                      create_task=True)
                        except CvpApiError as error:
                            self.__ansible.fail_json(msg='Error to deploy device {} to container {}'.format(
                                device.fqdn, *device.container))
                            MODULE_LOGGER.critical('Error deploying device {} : {}'.format(device.fqdn, *error))
                        else:
                            if resp['data']['status'] == 'success':
                                result_data.changed = True
                                result_data.success = True
                                result_data.taskIds = resp['data']['taskIds']

                    result_data.add_entry('{} deployed to {}'.format(
                        device.fqdn, *device.container))
            results.append(result_data)
        return results

    # ------------------------------------------ #
    # Helpers function
    # ------------------------------------------ #

    def list_devices_to_move(self, inventory: DeviceInventory):
        """
        list_devices_to_move UNSUPPORTED and NOT TESTED YET
        """
        devices_to_move = list()
        for device in inventory.devices:
            if self.__search_by == FIELD_FQDN:
                if self.is_in_container(device_lookup=device.fqdn,
                                        container_name=device.container) is False:
                    devices_to_move.append(device)
            if self.__search_by == FIELD_SYSMAC:
                if self.is_in_container(device_lookup=device.system_mac,
                                        container_name=device.container) is False:
                    devices_to_move.append(device)
        return devices_to_move

    # ------------------------------------------ #
    # Boolean functions
    # ------------------------------------------ #

    def is_in_container(self, device_lookup: str, container_name: str):
        """
        is_in_container Test on Cloudvision if a device is in container

        Parameters
        ----------
        device_lookup : str
            Device name
        container_name : str
            Container name

        Returns
        -------
        bool
            True if in container False in other situations
        """
        data = self.__get_device(search_value=device_lookup, search_by=self.__search_by)
        if data is not None and FIELD_PARENT_ID in data:
            container_data = self.get_container_info(container_name=container_name)
            if container_data is not None:
                if container_data['key'] == data[FIELD_PARENT_ID]:
                    return True
        return False

    def is_device_exist(self, device_lookup: str):
        """
        is_device_exist Test if a device exists in Cloudvision

        Parameters
        ----------
        device_lookup : str
            Device name

        Returns
        -------
        bool
            True if device available in Cloudvision, False by default
        """
        data = self.__get_device(
            search_value=device_lookup, search_by=self.__search_by)
        if data is not None and len(data) > 0:
            return True
        return False

    def has_correct_id(self, device: DeviceElement):
        """
        has_correct_id Test and compare device ID (SYSMAC) between inventory and Cloudvision

        Parameters
        ----------
        device : DeviceElement
            Device information

        Returns
        -------
        bool
            True if both inventory and CV has same sysmac for given hostname.
        """
        device_id_cv: str = None
        # Get ID with correct search method
        device_id_cv = self.get_device_id(device_lookup=device.fqdn)
        if device_id_cv == device.system_mac:
            return True
        return False
