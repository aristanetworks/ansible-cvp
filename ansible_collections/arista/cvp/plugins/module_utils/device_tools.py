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
FIELD_HOSTNAME = 'hostname'
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
        if FIELD_HOSTNAME in data:
            self.__hostname = data[FIELD_HOSTNAME]
        elif FIELD_FQDN in data:
            self.__hostname = data[FIELD_FQDN].split('.')[0]
        else:
            self.__hostname = None

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

    @fqdn.setter
    def fqdn(self, fqdn: str):
        """
        fqdn Setter for fqdn

        Parameters
        ----------
        fqdn : str
            fqdn to configure on device
        """
        self.__fqdn = fqdn

    @property
    def hostname(self):
        """
        hostname Getter for Hostname value

        Returns
        -------
        str
            HOSTNAME configured for the device
        """
        return self.__hostname

    @fqdn.setter
    def hostname(self, hostname: str):
        """
        hostname Setter for hostname

        Parameters
        ----------
        hostname : str
            hostname to configure on device
        """
        self.__hostname = hostname

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
        res[FIELD_HOSTNAME] = self.__hostname
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
            # if FIELD_FQDN in entry:
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
    # Updated as per issue #365 to set default search with hostname field
    def __init__(self, cv_connection, ansible_module: AnsibleModule = None, search_by: str = FIELD_HOSTNAME, check_mode: bool = False):
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

    @property
    def check_mode(self):
        """
        check_mode Getter to expose search mechanism

        Returns
        -------
        str
            Field name used for search
        """
        return self.__check_mode

    @check_mode.setter
    def check_mode(self, mode: str):
        self.__check_mode = mode

    # ------------------------------------------ #
    # Private functions
    # ------------------------------------------ #

    # Updated as per issue #365 to set default search with hostname field
    def __get_device(self, search_value: str, search_by: str = FIELD_HOSTNAME):
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
        MODULE_LOGGER.debug('Looking for device using %s as search_by', str(search_by))
        if search_by == FIELD_FQDN:
            cv_data = self.__cv_client.api.get_device_by_name(fqdn=search_value, search_by_hostname=False)
        elif search_by == FIELD_HOSTNAME:
            cv_data = self.__cv_client.api.get_device_by_name(fqdn=search_value, search_by_hostname=True)
        elif search_by == FIELD_SYSMAC:
            cv_data = self.__cv_client.api.get_device_by_mac(device_mac=search_value)
        elif search_by == FIELD_SERIAL:
            cv_data = self.__cv_client.api.get_device_by_serial(device_serial=search_value)
        MODULE_LOGGER.debug('Got following data for %s using %s: %s', str(search_value), str(search_by), str(cv_data))
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

    def __get_reordered_configlets_list(self, configlet_applied_to_device_list, configlet_playbook_list):
        """
        __get_reordered_configlets_list Provides mechanism to reoder the configlet lists.

        Extract information from CV configlet mapper and save as a cache in instance.

        Parameters
        ----------
        configlet_applied_to_device_list : list
            List of the configlet currently attached to the device
        configlet_playbook_list: list
            List of the configlet specified in the playbook in the correct order
        Returns
        -------
        list
            List of configlet in the correct order
        """
        new_configlets_list = list()
        for configlet in configlet_playbook_list:
            new_configlet = self.__get_configlet_info(configlet_name=configlet)
            if new_configlet is None:
                error_message = "The configlet \'%s\' defined to be applied on the device does not exist on CVP.", str(configlet)
                MODULE_LOGGER.error(error_message)
                self.__ansible.fail_json(msg=error_message)

            # If the configlet is not applied, add it to the new list
            if configlet not in [x.name for x in configlet_applied_to_device_list]:
                new_configlets_list.append(new_configlet)

            # If the confilet is already applied, remove it from the main list and add it to the end of the new list
            else:
                MODULE_LOGGER.debug("Removing the configlet %s from the current configlet list and adding it to the new list.", str(configlet))
                for x in configlet_applied_to_device_list:
                    if x.name == configlet:
                        configlet_applied_to_device_list.remove(x)
                        new_configlets_list.append(new_configlet)
        configlets_attached_get_configlet_info = [self.__get_configlet_info(configlet_name=x.name) for x in configlet_applied_to_device_list]
        # Joining the 2 new list (configlets already present + new configlet in right order)
        return configlets_attached_get_configlet_info + new_configlets_list



    def __get_configlet_list_inherited_from_container(self, device: DeviceElement):
        """
        __get_configlet_list_inherited_from_container Provides way to get the full list of configlets applied to the parent containers of the device.

        Will be useful in order to avoid removing the inherited configlets while detaching configlets (for example, when using strict mode).

        Parameters
        ----------
        device : DeviceElement
            device on which we would like to return the full list of configlets
        Returns
        -------
        list
            List of configlet
        """
        MODULE_LOGGER.debug("Getting list of inherited configlet for device {}".format(device.hostname))
        
        # List of inherited configlet from all the parent containers
        inherited_configlet_list = list()
        
        current_container = self.get_container_info(device.container)
        # While loop in order to retrieve the lists of configlets applied to all the parents container
        # Loop continue until the current container is the root container
        # TODO: The following loop will be triggered for every device. Maybe it makes sense to create some sort of cache in order to avoid 
        # doing unecessary API call to CVP.
        while current_container['root'] is not True:
            MODULE_LOGGER.debug("current_container: {}".format(current_container))
            # Get list of configlet for current container and add them to the list
            current_container_configlets_info = self.__cv_client.api.get_configlets_by_container_id(current_container['key'])
            inherited_configlet_list += [x['name'] for x in current_container_configlets_info['configletList']]
            
            # Get parent container name
            parent_container_name = self.__cv_client.api.get_container_by_id(current_container['key'])['parentName']
            
            current_container = self.get_container_info(parent_container_name)
            
    
        # Adding any potential configlet applied to the root container
        current_container_configlets_info = self.__cv_client.api.get_configlets_by_container_id(current_container['key'])
        MODULE_LOGGER.debug("Root container info: {}".format(current_container_configlets_info))
        inherited_configlet_list += [x['name'] for x in current_container_configlets_info['configletList']]

        MODULE_LOGGER.debug("Container inherited configlet list is: {}".format(inherited_configlet_list))        
        return inherited_configlet_list
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
        if self.__search_by in [FIELD_FQDN, FIELD_SERIAL, FIELD_HOSTNAME]:
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
        MODULE_LOGGER.debug("Get container for device %s", str(device_mac))
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
        MODULE_LOGGER.info('Inventory to refresh is %s', str(user_inventory.devices))
        for device in user_inventory.devices:
            MODULE_LOGGER.info('Lookup is based on %s field', str(self.__search_by))
            MODULE_LOGGER.debug('Found device %s to refresh data', str(device.info))
            if device.system_mac is None:
                system_mac = self.get_device_facts(
                    device_lookup=device.info[self.__search_by])[FIELD_SYSMAC]
                MODULE_LOGGER.debug(
                    'Get sysmac %s for device %s', str(device.fqdn), str(system_mac))
                device.system_mac = system_mac

            if device.system_mac is not None:
                user_result.append(device.info)

        MODULE_LOGGER.warning('Update list is: %s', str(user_result))
        return DeviceInventory(data=user_result)

    def refresh_fqdn(self, user_inventory: DeviceInventory):
        """
        refresh_fqdn Get FQDN from Cloudvision to update missing information

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
        MODULE_LOGGER.info('Inventory to refresh is %s', str(user_inventory.devices))
        for device in user_inventory.devices:
            MODULE_LOGGER.debug('Found device %s to refresh data', str(device.info))
            if device.system_mac is not None and self.__search_by == FIELD_SYSMAC:
                fqdn = self.get_device_facts(
                    device_lookup=device.system_mac)[FIELD_FQDN]
                MODULE_LOGGER.debug(
                    'Get fqdn %s for device %s', str(fqdn), str(device.system_mac))
                device.fqdn = fqdn
                user_result.append(device.info)
            elif device.serial_number is not None and self.__search_by == FIELD_SERIAL:
                fqdn = self.get_device_facts(
                    device_lookup=device.serial_number)[FIELD_FQDN]
                MODULE_LOGGER.debug(
                    'Get fqdn %s for device %s', str(fqdn), str(device.serial_number))
                device.fqdn = fqdn
                user_result.append(device.info)
            else:
                MODULE_LOGGER.debug('Skipping following device: %s', device.info)

        MODULE_LOGGER.warning('Update list is: %s', str(user_result))
        return DeviceInventory(data=user_result)

    def check_device_exist(self, user_inventory: DeviceInventory, search_mode: str = FIELD_FQDN):
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
            if self.__search_by == FIELD_HOSTNAME or search_mode == FIELD_HOSTNAME:
                if self.is_device_exist(device.fqdn, search_mode=FIELD_HOSTNAME) is False:
                    device_not_present.append(device.fqdn)
                    MODULE_LOGGER.error('Device not present in CVP but in the user_inventory: %s', device.fqdn)

            elif self.__search_by == FIELD_FQDN or search_mode == FIELD_FQDN:
                if self.is_device_exist(device.fqdn, search_mode=FIELD_FQDN) is False:
                    device_not_present.append(device.fqdn)
                    MODULE_LOGGER.error('Device not present in CVP but in the user_inventory: %s', device.fqdn)

            elif self.__search_by == FIELD_SYSMAC:
                if self.is_device_exist(device.system_mac) is False:
                    device_not_present.append(device.system_mac, search_mode=FIELD_SYSMAC)
                    MODULE_LOGGER.error('Device not present in CVP but in the user_inventory: %s', device.system_mac)
            elif search_mode == FIELD_SERIAL:
                if self.is_device_exist(device.serial_number, search_mode=FIELD_SERIAL) is False:
                    device_not_present.append(device.serial_number)
                    MODULE_LOGGER.error('Device not present in CVP but in the user_inventory: %s', device.serial_number)
        return device_not_present

    # ------------------------------------------ #
    # Workers function
    # ------------------------------------------ #

    def manager(self, user_inventory: DeviceInventory, search_mode: str = FIELD_HOSTNAME, apply_mode: str = 'loose'):
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
        apply_mode: str, optional
            Define how manager will apply configlets to device: loose (only attach listed configlet) or strict (attach listed configlet, remove others)

        Returns
        -------
        dict
            All Ansible output formated using CvAnsibleResponse
        """
        response = CvAnsibleResponse()

        self.__search_by = search_mode

        MODULE_LOGGER.debug('Manager search mode is set to: %s', str(search_mode))
        self.__search_by = search_mode

        cv_deploy = CvManagerResult(builder_name='devices_deployed')
        cv_move = CvManagerResult(builder_name='devices_moved')
        cv_configlets_attach = CvManagerResult(builder_name='configlets_attached')
        cv_configlets_detach = CvManagerResult(builder_name='configlets_detached')

        # Check if the devices defined exist in CVP
        list_non_existing_devices = self.check_device_exist(user_inventory=user_inventory, search_mode=search_mode)
        if list_non_existing_devices is not None and len(list_non_existing_devices) > 0:
            error_message = 'Error - the following devices do not exist in CVP {0} but are defined in the playbook. \
                \nMake sure that the devices are provisioned and defined with the full fqdn name \
                (including the domain name) if needed.'.format(str(list_non_existing_devices))
            MODULE_LOGGER.error(error_message)
            self.__ansible.fail_json(msg=error_message)

        # Need to collect all missing device systemMacAddress
        # deploy needs to locate devices by mac-address
        if self.__search_by == FIELD_FQDN:
            user_inventory = self.refresh_systemMacAddress(user_inventory=user_inventory)

        elif self.__search_by == FIELD_HOSTNAME:
            user_inventory = self.refresh_systemMacAddress(user_inventory=user_inventory)

        elif self.__search_by == FIELD_SERIAL:
            user_inventory = self.refresh_fqdn(user_inventory=user_inventory)
            user_inventory = self.refresh_systemMacAddress(user_inventory=user_inventory)

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

        response.add_manager(cv_move)
        MODULE_LOGGER.debug('AnsibleResponse updated, new content with cv_move: %s', str(response.content))
        response.add_manager(cv_deploy)
        MODULE_LOGGER.debug('AnsibleResponse updated, new content with cv_deploy: %s', str(response.content))
        response.add_manager(cv_configlets_attach)
        MODULE_LOGGER.debug('AnsibleResponse updated, new content with cv_configlets_attach: %s', str(response.content))
        response.add_manager(cv_configlets_detach)
        MODULE_LOGGER.debug('AnsibleResponse updated, new content with cv_configlets_detach: %s', str(response.content))

        return response.content

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
                    error_message = 'The target container \'{0}\' for the device \'{1}\' does not exist on CVP.'.format(device.container, device.fqdn)
                    MODULE_LOGGER.error(error_message)
                    self.__ansible.fail_json(msg=error_message)
                current_container_info = self.get_container_current(device_mac=device.system_mac)
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
        MODULE_LOGGER.debug('Apply configlets to following inventory: %s', str([x.info for x in user_inventory.devices]))
        for device in user_inventory.devices:
            MODULE_LOGGER.debug("Applying configlet for device: %s", str(device.fqdn))
            result_data = CvApiResult(action_name=device.fqdn + '_configlet_attached')
            current_container_info = self.get_container_current(device_mac=device.system_mac)
            if (device.configlets is None or current_container_info['name'] == UNDEFINED_CONTAINER):
                continue
            # get configlet information from CV
            configlets_attached = list()
            if self.__search_by == FIELD_SERIAL:
                configlets_attached = self.get_device_configlets(device_lookup=device.serial_number)
            elif self.__search_by == FIELD_HOSTNAME:
                configlets_attached = self.get_device_configlets(device_lookup=device.hostname)
            else:
                configlets_attached = self.get_device_configlets(device_lookup=device.fqdn)
            configlets_attached_before_changes = [x.name for x in configlets_attached]

            configlets_reordered_list = self.__get_reordered_configlets_list(configlets_attached, device.configlets)

            # Check if changes have been made
            MODULE_LOGGER.debug("[%s] - Old configlet list: %s", str(device.fqdn), str(configlets_attached_before_changes))
            MODULE_LOGGER.debug("[%s] - New configlet list: %s", str(device.fqdn), str([x['name'] for x in configlets_reordered_list]))
            if str(configlets_attached_before_changes) == str([x['name'] for x in configlets_reordered_list]):
                MODULE_LOGGER.info("[%s] - There was no changes detected in the configlets list, skipping task creation for the device.", str(device.fqdn))
                continue

            MODULE_LOGGER.info("Creating task for device [%s] configlet list is: %s", str(device.fqdn), str([x['name'] for x in configlets_reordered_list]))
            # get device facts from CV
            device_facts = dict()
            if self.__search_by == FIELD_FQDN:
                device_facts = self.__cv_client.api.get_device_by_name(
                    fqdn=device.fqdn, search_by_hostname=False)
            elif self.__search_by == FIELD_HOSTNAME:
                device_facts = self.__cv_client.api.get_device_by_name(
                    fqdn=device.fqdn, search_by_hostname=True)
            elif self.__search_by == FIELD_SERIAL:
                device_facts = self.__cv_client.api.get_device_by_serial(device_serial=device.serial_number)
            # Attach configlets to device
            if len(configlets_reordered_list) > 0:
                try:
                    resp = self.__cv_client.api.apply_configlets_to_device(app_name='CvDeviceTools.apply_configlets',
                                                                           dev=device_facts,
                                                                           new_configlets=configlets_reordered_list,
                                                                           create_task=True,
                                                                           reorder_configlets=True)
                except TypeError:
                    error_message = 'The function to reorder the configlet is not present. Please, check your cvprac version (>= 1.0.7 required).'
                    MODULE_LOGGER.error(error_message)
                    self.__ansible.fail_json(msg=error_message)
                except CvpApiError:
                    MODULE_LOGGER.error('Error applying configlets to device')
                    self.__ansible.fail_json(msg='Error applying configlets to device')
                else:
                    if resp['data']['status'] == 'success':
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = resp['data']['taskIds']
                        result_data.add_entry('{} adds {}'.format(device.fqdn, *device.configlets))
                        MODULE_LOGGER.debug('CVP response is: %s', str(resp))
                        MODULE_LOGGER.info('Reponse data is: %s', str(result_data.results))
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
                        fqdn=device.fqdn, search_by_hostname=False)
                elif self.__search_by == FIELD_HOSTNAME:
                    device_facts = self.__cv_client.api.get_device_by_name(
                        fqdn=device.fqdn, search_by_hostname=True)
                elif self.__search_by == FIELD_SERIAL:
                    device_facts = self.__cv_client.api.get_device_by_serial(
                        device_serial=device.serial_number)
            
                # List of expected configlet applied to the device, taking into account the configlets inherited from parent containers
                expected_device_configlet_list = self.__get_configlet_list_inherited_from_container(device) + device.configlets
                
                configlets_to_remove = list()
                
                # get list of configured configlets
                configlets_attached = self.get_device_configlets(device_lookup=device.info[self.__search_by])
                MODULE_LOGGER.debug('Current configlet attached {}'.format(configlets_attached))
                
                # For each configlet not in the list, add to list of configlets to remove
                for configlet in configlets_attached:
                    if configlet.name not in expected_device_configlet_list:
                        MODULE_LOGGER.info('Configlet [%s] is added to detach list', str(configlet.name))
                        result_data.name = result_data.name + ' - ' + configlet.name
                        configlets_to_remove.append(configlet.data)
                # Detach configlets to device
                if len(configlets_to_remove) > 0:
                    MODULE_LOGGER.debug('List of configlet to remove for device {} is {}'.format(device.fqdn, [x['name'] for x in configlets_to_remove]))
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
                        fqdn=device.fqdn, search_by_hostname=False)
                elif self.__search_by == FIELD_HOSTNAME:
                    device_facts = self.__cv_client.api.get_device_by_name(
                        fqdn=device.fqdn, search_by_hostname=True)
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
            result_data = CvApiResult(action_name=device.info[self.__search_by] + '_deployed')
            if device.system_mac is not None:
                configlets_info = list()
                for configlet in device.configlets:
                    new_configlet = self.__get_configlet_info(configlet_name=configlet)
                    if new_configlet is None:
                        error_message = "The configlet \'{0}\' defined to be applied on the device \'{1}\' does not \
                            exist on the CVP server.".format(str(configlet), str(device.fqdn))
                        MODULE_LOGGER.error(error_message)
                        self.__ansible.fail_json(msg=error_message)
                    else:
                        configlets_info.append(new_configlet)
                # Move devices when they are not in undefined container
                current_container_info = self.get_container_current(
                    device_mac=device.system_mac)
                MODULE_LOGGER.debug('Device {0} is currently under {1}'.format(
                    device.fqdn, current_container_info['name']))
                device_info = self.get_device_facts(device_lookup=device.fqdn)
                if (current_container_info['name'] == 'Undefined'):
                    if self.__check_mode:
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = ['unsupported_in_check_mode']
                    else:
                        # Check if the target container exists
                        target_container_info = self.get_container_info(container_name=device.container)
                        if target_container_info is None:
                            error_message = 'The target container \'{0}\' for the device \'{1}\' does not exist on CVP.'.format(device.container, device.fqdn)
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

                    result_data.add_entry('{0} deployed to {1}'.format(
                        device.info[self.__search_by], device.container))
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
            elif self.__search_by == FIELD_SYSMAC:
                if self.is_in_container(device_lookup=device.system_mac,
                                        container_name=device.container) is False:
                    devices_to_move.append(device)
            elif self.__search_by == FIELD_SERIAL:
                if self.is_in_container(device_lookup=device.serial_number,
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

    def is_device_exist(self, device_lookup: str, search_mode: str = FIELD_HOSTNAME):
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
            search_value=device_lookup, search_by=search_mode)
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
