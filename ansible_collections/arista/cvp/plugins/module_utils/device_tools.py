#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# flake8: noqa: W1202
#


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import traceback
import logging
import uuid
import time
from functools import lru_cache
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger  # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import (
    CvApiResult,
    CvManagerResult,
    CvAnsibleResponse,
)
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import (
    ModuleOptionValues,
    DeviceResponseFields,
)
from ansible_collections.arista.cvp.plugins.module_utils.generic_tools import CvElement
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas import (
    v3 as schema,
)
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import (
    validate_json_schema,
)

try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import (
        CvpApiError,
        CvpRequestError,
    )  # noqa # pylint: disable=unused-import

    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()
try:
    import jsonschema  # noqa # pylint: disable=unused-import

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info("Start device_tools module execution")

# TODO - use f-strings
# pylint: disable=consider-using-f-string


class DeviceElement(object):
    """
    DeviceElement Object to represent Device Element from user inventory
    """

    def __init__(self, data: dict):
        self.__data = data
        self.__fqdn = self.__data.get(Api.device.FQDN)
        self.__sysmac = self.__data.get(Api.device.SYSMAC)
        self.__serial = self.__data.get(Api.device.SERIAL)
        self.__mgmtip = self.__data.get(Api.device.MGMTIP)
        self.__container = self.__data[Api.generic.PARENT_CONTAINER_NAME]
        self.__current_parent_container_id = None
        self.__image_bundle = self.__data.get(Api.device.BUNDLE)

        if Api.device.BUNDLE in self.__data:
            self.__image_bundle = data[Api.device.BUNDLE]
        if Api.device.SYSMAC in data:
            self.__sysmac = data[Api.device.SYSMAC]
        if Api.device.SERIAL in data:
            self.__serial = data[Api.device.SERIAL]
        if Api.device.HOSTNAME in data:
            self.__hostname = data[Api.device.HOSTNAME]
        if Api.device.MGMTIP in data:
            self.__mgmtip = data[Api.device.MGMTIP]
        elif Api.device.FQDN in data:
            self.__hostname = data[Api.device.FQDN].split(".")[0]
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
    def mgmt_ip(self):
        """
        system_mac Getter for SystemMac value

        Returns
        -------
        str
            mgmtIp address for the device
        """
        return self.__mgmtip

    @mgmt_ip.setter
    def mgmt_ip(self, mgmtip: str):
        """
        mgmt_ip Setter for MgmtIp address

        Parameters
        ----------
        ip : str
            mgmtIp address to configure on device
        """
        self.__mgmtip = mgmtip

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
        if Api.generic.CONFIGLETS in self.__data:
            return self.__data[Api.generic.CONFIGLETS]
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

    @property
    def image_bundle(self):
        """
        image_bundle Getter for image bundle info

        Returns
        -------
        dict
            Dict with name, ID and type of bundle
        """
        return self.__image_bundle

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
        res = {
            Api.device.FQDN: self.__fqdn,
            Api.device.HOSTNAME: self.__hostname,
        }

        if self.__serial is not None:
            res[Api.device.SERIAL] = self.__serial
        if self.__sysmac is not None:
            res[Api.device.SYSMAC] = self.__sysmac
            res[Api.generic.KEY] = self.__sysmac
        res[Api.generic.PARENT_CONTAINER_NAME] = self.__container
        if Api.generic.CONFIGLETS in self.__data:
            res[Api.generic.CONFIGLETS] = self.__data[Api.generic.CONFIGLETS]
        else:
            res[Api.generic.CONFIGLETS] = []
        # res[Api.generic.PARENT_CONTAINER_ID] = self.__current_parent_container_id
        if Api.generic.IMAGE_BUNDLE_NAME in self.__data:
            res[Api.generic.IMAGE_BUNDLE_NAME] = self.__data[
                Api.generic.IMAGE_BUNDLE_NAME
            ]
        return res


class DeviceInventory(object):
    """
    DeviceInventory Local User defined inventory
    """

    def __init__(
        self,
        data: list,
        schema=schema.SCHEMA_CV_DEVICE,
        search_method: str = Api.device.FQDN,
    ):
        self.__inventory = []
        self.__data = data
        self.__schema = schema
        self.search_method = search_method
        for entry in data:
            # if Api.device.FQDN in entry:
            self.__inventory.append(DeviceElement(data=entry))

    @property
    def is_valid(self):
        """
        check_schemas Validate schemas for user's input
        """
        if not validate_json_schema(user_json=self.__data, schema=self.__schema):
            MODULE_LOGGER.error("Invalid configlet input : \n%s", str(self.__data))
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

    def get_device(self, device_string: str, search_method: str = Api.device.FQDN):
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
        for device in self.__inventory:
            if (
                self.search_method is Api.device.SYSMAC
                or search_method is Api.device.SYSMAC
            ):
                if device.system_mac == device_string:
                    return device
            elif device.fqdn == device_string:
                return device
        return None


class CvDeviceTools(object):
    """
    CvDeviceTools Object to operate Device operation on Cloudvision
    """

    # Updated as per issue #365 to set default search with hostname field
    def __init__(
        self,
        cv_connection,
        ansible_module: AnsibleModule = None,
        search_by: str = Api.device.HOSTNAME,
        check_mode: bool = False,
    ):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module
        self.__search_by = search_by
        self.__configlets_and_mappers_cache = None
        self.__check_mode = check_mode
        # Cache for list of configlets applied to each container - format {<container_id>: {"name": "<>", "parentContainerId": "<>", "configlets": ['', '']}
        self.__containers_configlet_list_cache = {}

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
    @lru_cache
    def __get_device(self, search_value: str, search_by: str = Api.device.HOSTNAME):
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
        cv_data: dict = {}
        MODULE_LOGGER.debug("Looking for device using %s as search_by", str(search_by))
        if search_by == Api.device.FQDN:
            cv_data = self.__cv_client.api.get_device_by_name(
                fqdn=search_value, search_by_hostname=False
            )
        elif search_by == Api.device.HOSTNAME:
            cv_data = self.__cv_client.api.get_device_by_name(
                fqdn=search_value, search_by_hostname=True
            )
        elif search_by == Api.device.SYSMAC:
            cv_data = self.__cv_client.api.get_device_by_mac(device_mac=search_value)
        elif search_by == Api.device.SERIAL:
            cv_data = self.__cv_client.api.get_device_by_serial(
                device_serial=search_value
            )

        if cv_data is not None and len(cv_data) > 0:
            cv_data[Api.device.BUNDLE] = self.__cv_client.api.get_device_image_info(
                cv_data["key"]
            )

        MODULE_LOGGER.debug(
            "Got following data for %s using %s: %s",
            str(search_value),
            str(search_by),
            str(cv_data),
        )
        return cv_data

    @lru_cache
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
            self.__configlets_and_mappers_cache = (
                self.__cv_client.api.get_configlets_and_mappers()
            )
        for configlet in self.__configlets_and_mappers_cache["data"][
            Api.generic.CONFIGLETS
        ]:
            if configlet_name == configlet[Api.generic.NAME]:
                return configlet
        return None

    def __get_reordered_configlets_list(
        self, configlet_applied_to_device_list, configlet_playbook_list
    ):
        """
        __get_reordered_configlets_list Provides mechanism to reorder the configlet lists.

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
        new_configlets_list = []
        for configlet in configlet_playbook_list:
            new_configlet = self.__get_configlet_info(configlet_name=configlet)
            if new_configlet is None:
                error_message = (
                    "The configlet '%s' defined to be applied on the device does not exist on CVP.",
                    str(configlet),
                )
                MODULE_LOGGER.error(error_message)
                self.__ansible.fail_json(msg=error_message)

            # If the configlet is not applied, add it to the new list avoiding duplicates.
            if configlet not in [x.name for x in configlet_applied_to_device_list] and new_configlet not in new_configlets_list:
                new_configlets_list.append(new_configlet)

            # If the configlet is already applied, remove it from the main list and add it to the end of the new list
            else:
                MODULE_LOGGER.debug(
                    "Removing the configlet %s from the current configlet list and adding it to the new list.",
                    str(configlet),
                )
                for x in configlet_applied_to_device_list:
                    if x.name == configlet:
                        configlet_applied_to_device_list.remove(x)
                        if new_configlet not in new_configlets_list:
                            new_configlets_list.append(new_configlet)
                            break
        configlets_attached_get_configlet_info = [
            self.__get_configlet_info(configlet_name=x.name)
            for x in configlet_applied_to_device_list
        ]

        # Joining the 2 new list (configlets already present + new configlet in right order)
        reordered_configlets_list = configlets_attached_get_configlet_info + new_configlets_list
        MODULE_LOGGER.debug("reordered_configlets_list %s", str(reordered_configlets_list))
        # Find any reconcile configlet and move to the end of the reordered list.
        reconciled_configlet_indexes = [index for index, configlet in enumerate(reordered_configlets_list) if configlet["reconciled"]]
        reconciled_configlet_indexes.reverse()
        reconciled_configlets = [reordered_configlets_list.pop(index) for index in reconciled_configlet_indexes]
        reordered_configlets_list.extend(reconciled_configlets)

        if len(reconciled_configlet_indexes) > 1:
            reconcile_configlet_names = ", ".join([configlet.name for configlet in reconciled_configlets])
            error_message = (
                "Two 'reconcile' configlets '%s' are assigned to one device, which is not supported by CloudVision.",
                reconcile_configlet_names,
            )
            MODULE_LOGGER.error(error_message)
            self.__ansible.fail_json(msg=error_message)

        return reordered_configlets_list

    def __refresh_user_inventory(self, user_inventory: DeviceInventory):
        """
        __refresh_user_inventory Get all data from Cloudvision to populate user_inventory

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user

        Returns
        -------
        DeviceInventory
            Device inventory with missing data
        """
        # Need to collect all missing device systemMacAddress
        # deploy needs to locate devices by mac-address
        if self.__search_by in [Api.device.FQDN, Api.device.HOSTNAME]:
            user_inventory = self.refresh_systemMacAddress(
                user_inventory=user_inventory
            )

        elif self.__search_by == Api.device.SERIAL:
            user_inventory = self.refresh_fqdn(user_inventory=user_inventory)
            user_inventory = self.refresh_systemMacAddress(
                user_inventory=user_inventory
            )

        return user_inventory

    def __check_devices_exist(self, user_inventory: DeviceInventory):
        """
        __check_devices_exist Check devices are all present on Cloudvision

        Check devices are configured on Cloudvision and returns error message
        if at least one device is missing

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user
        """
        list_non_existing_devices = self.check_device_exist(
            user_inventory=user_inventory, search_mode=self.__search_by
        )
        if list_non_existing_devices is not None and len(list_non_existing_devices) > 0:
            error_message = "Error - the following devices do not exist in CVP {0} but are defined in the playbook. \
                Make sure that the devices are provisioned and defined with the full fqdn name \
                (including the domain name) if needed.".format(
                str(list_non_existing_devices)
            )
            MODULE_LOGGER.error(error_message)
            self.__ansible.fail_json(msg=error_message)
        return True

    def __remove_missing_devices(self, user_inventory: DeviceInventory):
        """
        __remove_missing_devices Check if devices are present on Cloudvision and remove missing devices from the user_inventory

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user

        Returns
        -------
        DeviceInventory
            Device inventory where missing devices are removed
        """

        # Use dict to map the relevant attribute of the device to use for search
        DEVICE_SEARCH_ATTRIBUTE = {
            Api.device.HOSTNAME: "fqdn",
            Api.device.FQDN: "fqdn",
            Api.device.SYSMAC: "system_mac",
            Api.device.SERIAL: "serial_number",
        }

        MODULE_LOGGER.debug("Remove missing devices from user_inventory")

        # Loop through devices and record index of missing ones for later removal
        missing_devices_indexes: list = []
        for index, device in enumerate(user_inventory.devices):
            device_search_key = getattr(
                device, DEVICE_SEARCH_ATTRIBUTE[self.__search_by], "fqdn"
            )
            if (
                self.is_device_exist(device_search_key, search_mode=self.__search_by)
                is False
            ):
                missing_devices_indexes.append(index)
                MODULE_LOGGER.debug(
                    "Device not present in CVP, removing from user_inventory: %s",
                    device_search_key,
                )

        # Remove missing devices from list - reversed to not change indexes.
        missing_devices_indexes.reverse()
        for index in missing_devices_indexes:
            user_inventory.devices.pop(index)

        return user_inventory

    def __state_present(self, user_inventory: DeviceInventory, apply_mode: str = ModuleOptionValues.APPLY_MODE_LOOSE,
                        inventory_mode: str = ModuleOptionValues.INVENTORY_MODE_STRICT):
        """
        __state_present Execute actions when user configures state=present

        Run following actions:
            - Provision devices
            - Move devices
            - Add configlets to devices
            - Remove configlets to devices (when in strict mode)

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user
        apply_mode : str, optional
            Method to manage configlets, by default 'loose'

        Returns
        -------
        CvAnsibleResponse
            Ansible Output message
        """
        cv_deploy = CvManagerResult(builder_name=DeviceResponseFields.DEVICE_DEPLOYED)
        cv_move = CvManagerResult(builder_name=DeviceResponseFields.DEVICE_MOVED)
        cv_configlets_attach = CvManagerResult(
            builder_name=DeviceResponseFields.CONFIGLET_ATTACHED
        )
        cv_configlets_detach = CvManagerResult(
            builder_name=DeviceResponseFields.CONFIGLET_DETACHED
        )
        cv_bundle_attach = CvManagerResult(
            builder_name=DeviceResponseFields.BUNDLE_ATTACHED
        )
        cv_bundle_detach = CvManagerResult(
            builder_name=DeviceResponseFields.BUNDLE_DETACHED
        )
        response = CvAnsibleResponse()

        if inventory_mode == ModuleOptionValues.INVENTORY_MODE_LOOSE:
            # Remove missing devices on CV from inventory (ignore missing)
            user_inventory = self.__remove_missing_devices(
                user_inventory=user_inventory
            )
        else:
            # Check if all devices are present on CV (fail on missing)
            self.__check_devices_exist(user_inventory=user_inventory)

        # Refresh UserInventory data with data from Cloudvision
        user_inventory = self.__refresh_user_inventory(user_inventory=user_inventory)

        # Deploy device if it is under undefined container
        action_result = self.deploy_device(user_inventory=user_inventory)
        if action_result is not None:
            for update in action_result:
                cv_deploy.add_change(change=update)

        # Move devices to their destination container
        action_result = self.move_device(user_inventory=user_inventory)
        if action_result is not None:
            for update in action_result:
                cv_move.add_change(change=update)

        # Apply configlets as set in inventory
        action_result = self.apply_configlets(user_inventory=user_inventory)
        if action_result is not None:
            for update in action_result:
                cv_configlets_attach.add_change(change=update)

        # Apply image bundle as set in inventory
        action_result = self.apply_bundle(user_inventory=user_inventory)
        if action_result is not None:
            for update in action_result:
                cv_bundle_attach.add_change(change=update)

        # Remove configlets configured on CVP and if module runs in strict mode
        if apply_mode == ModuleOptionValues.APPLY_MODE_STRICT:
            action_result = self.detach_configlets(user_inventory=user_inventory)
            if action_result is not None:
                for update in action_result:
                    cv_configlets_detach.add_change(change=update)

            action_result = self.detach_bundle(user_inventory=user_inventory)
            if action_result is not None:
                for update in action_result:
                    cv_bundle_detach.add_change(change=update)

        # Generate result output
        response.add_manager(cv_move)
        MODULE_LOGGER.debug(
            "AnsibleResponse updated, new content with cv_move: %s",
            str(response.content),
        )
        response.add_manager(cv_deploy)
        MODULE_LOGGER.debug(
            "AnsibleResponse updated, new content with cv_deploy: %s",
            str(response.content),
        )
        response.add_manager(cv_configlets_attach)
        MODULE_LOGGER.debug(
            "AnsibleResponse updated, new content with cv_configlets_attach: %s",
            str(response.content),
        )
        response.add_manager(cv_bundle_attach)
        MODULE_LOGGER.debug(
            "AnsibleResponse updated, new content with cv_bundle_attach: %s",
            str(response.content),
        )
        response.add_manager(cv_configlets_detach)
        MODULE_LOGGER.debug(
            "AnsibleResponse updated, new content with cv_configlets_detach: %s",
            str(response.content),
        )
        response.add_manager(cv_bundle_detach)
        MODULE_LOGGER.debug(
            "AnsibleResponse updated, new content with cv_bundle_detach: %s",
            str(response.content),
        )

        return response

    def __state_factory_reset(
        self,
        user_inventory: DeviceInventory,
        inventory_mode: str = ModuleOptionValues.INVENTORY_MODE_STRICT,
    ):
        """
        __state_factory_reset Execute actions when user configures state=factory_reset

        Run following actions:
            - Reset device to ztp mode

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user

        Returns
        -------
        CvAnsibleResponse
            Ansible Output message
        """
        response = CvAnsibleResponse()
        cv_reset = CvManagerResult(builder_name=DeviceResponseFields.DEVICE_RESET)

        if inventory_mode == ModuleOptionValues.INVENTORY_MODE_LOOSE:
            # Remove missing devices on CV from inventory (ignore missing)
            user_inventory = self.__remove_missing_devices(
                user_inventory=user_inventory
            )
        else:
            # Check if all devices are present on CV (fail on missing)
            self.__check_devices_exist(user_inventory=user_inventory)

        user_inventory = self.__refresh_user_inventory(user_inventory=user_inventory)

        # Execute device reset
        action_result = self.reset_device(user_inventory=user_inventory)
        if action_result is not None:
            MODULE_LOGGER.debug("action_result is: %s", str(action_result))
            for update in action_result:
                cv_reset.add_change(change=update)
        response.add_manager(cv_reset)
        return response

    def __state_provisioning_reset(
        self,
        user_inventory: DeviceInventory,
        inventory_mode: str = ModuleOptionValues.INVENTORY_MODE_STRICT,
    ):
        """
        __state_provisioning_reset Execute actions when user configures state=provisioning_reset

        Run following actions:
            - Remove the device from provisioning (pre CVP 2021.3.0)
            - Move device back to the Undefined container (post CVP 2021.3.0)

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user

        Returns
        -------
        CvAnsibleResponse
            Ansible Output message
        """
        response = CvAnsibleResponse()
        cv_reset = CvManagerResult(builder_name=DeviceResponseFields.DEVICE_REMOVED)

        if inventory_mode == ModuleOptionValues.INVENTORY_MODE_LOOSE:
            # Remove missing devices on CV from inventory (ignore missing)
            user_inventory = self.__remove_missing_devices(
                user_inventory=user_inventory
            )
        else:
            # Check if all devices are present on CV (fail on missing)
            self.__check_devices_exist(user_inventory=user_inventory)

        user_inventory = self.__refresh_user_inventory(user_inventory=user_inventory)

        # Execute device delete
        action_result = self.delete_device(user_inventory=user_inventory)
        if action_result is not None:
            MODULE_LOGGER.debug("action_result is: %s", str(action_result))
            for update in action_result:
                cv_reset.add_change(change=update)
        response.add_manager(cv_reset)
        return response

    def __state_absent(
        self,
        user_inventory: DeviceInventory,
        inventory_mode: str = ModuleOptionValues.INVENTORY_MODE_STRICT,
    ):
        """
        __state_absent Execute actions when user configures state=absent

        Run following actions:
            - decommission devices (the API stops TerminAttr and removes the device fully from CVP)

        Parameters
        ----------
        user_inventory : DeviceInventory
            Inventory provided by user

        Returns
        -------
        CvAnsibleResponse
            Ansible Output message
        """
        response = CvAnsibleResponse()
        cv_reset = CvManagerResult(
            builder_name=DeviceResponseFields.DEVICE_DECOMMISSIONED
        )

        if inventory_mode == ModuleOptionValues.INVENTORY_MODE_LOOSE:
            # Remove missing devices on CV from inventory (ignore missing)
            user_inventory = self.__remove_missing_devices(
                user_inventory=user_inventory
            )
        else:
            # Check if all devices are present on CV (fail on missing)
            self.__check_devices_exist(user_inventory=user_inventory)

        user_inventory = self.__refresh_user_inventory(user_inventory=user_inventory)

        # Execute device decommission
        action_result = self.decommission_device(user_inventory=user_inventory)
        if action_result is not None:
            MODULE_LOGGER.debug("action_result is: %s", str(action_result))
            for update in action_result:
                cv_reset.add_change(change=update)
        response.add_manager(cv_reset)
        return response

    def __build_topology_cache(self, container):
        """
        Recursive method. Takes a container in the format of __cv_client.api.filter_topology() cvprac call and
        store the information in the self.__containers_configlet_list_cache variable with the correct format.
        Format is:  {<container_id>: {"name": "<>", "parentContainerId": "<>", "configlets": ['', '']}
        The function is then called again with the child_containers (if any).

        Parameters
        ----------
        container : dict
            container information. dict_keys(['key', Api.generic.NAME, 'type', 'childContainerCount', 'childNetElementCount', 'parentContainerId', 'mode',
            'deviceStatus', 'childTaskCount', 'childContainerList', 'childNetElementList', 'hierarchyNetElementCount', 'tempAction', 'tempEvent'])
        """
        MODULE_LOGGER.debug(
            "Adding to cache container: {0}".format(container[Api.generic.NAME])
        )
        cache_new_entry = {
            Api.generic.NAME: container[Api.generic.NAME],
            Api.generic.PARENT_CONTAINER_ID: container[Api.generic.PARENT_CONTAINER_ID],
        }
        self.__containers_configlet_list_cache[
            container[Api.generic.KEY]
        ] = cache_new_entry
        for child_container in container[Api.container.CHILDREN_LIST]:
            self.__build_topology_cache(child_container)

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
        inherited_configlet_list = []
        # If the cache is not empty, we skip the API call
        if not self.__containers_configlet_list_cache:
            MODULE_LOGGER.debug(
                "[API call] get info about all the containers: self.__cv_client.api.filter_topology()"
            )
            topology = self.__cv_client.api.filter_topology()
            self.__build_topology_cache(topology[Api.container.TOPOLOGY])

        parent_container_name = device.container
        # Get parent container id of the device by comparing all containers name in the topology
        parent_container_id = ""
        # TODO - use dict items
        #      for container_id in ..
        # pylint: disable=consider-using-dict-items
        for container_id in self.__containers_configlet_list_cache:
            if (
                self.__containers_configlet_list_cache[container_id][Api.generic.NAME]
                == parent_container_name
            ):
                parent_container_id = container_id
                break
        MODULE_LOGGER.debug(
            "parent_container_name is:  {0}".format(parent_container_name)
        )
        MODULE_LOGGER.debug("parent_container_id is:  {0}".format(parent_container_id))

        # While loop to retrieve the lists of configlets applied to all the parents containers
        # Cache variable is self.__containers_configlet_list_cache - format
        # {<container_id>: {"name": "<>", "parentContainerId": "<>", "configlets": ['', '']}
        while parent_container_id is not None:
            container_id = parent_container_id
            # If the container is in cache
            if (
                container_id in self.__containers_configlet_list_cache.keys()
                and Api.generic.CONFIGLETS
                in self.__containers_configlet_list_cache[container_id].keys()
            ):
                MODULE_LOGGER.debug(
                    "Using cache for following container: {0}".format(container_id)
                )
                inherited_configlet_list += self.__containers_configlet_list_cache[
                    container_id
                ][Api.generic.CONFIGLETS]
                parent_container_id = self.__containers_configlet_list_cache[
                    container_id
                ][Api.generic.PARENT_CONTAINER_ID]

            # If the container is not in cache
            else:
                container_name = self.__containers_configlet_list_cache[container_id][
                    Api.generic.NAME
                ]
                # Get list of configlet for current container
                MODULE_LOGGER.debug(
                    "[API call] Get configlet associated with container: {0}".format(
                        container_name
                    )
                )
                current_container_configlets_info = (
                    self.__cv_client.api.get_configlets_by_container_id(container_id)
                )
                configletList = [
                    x[Api.generic.NAME]
                    for x in current_container_configlets_info[
                        Api.container.CONFIGLETS_LIST
                    ]
                ]
                inherited_configlet_list += configletList

                # Get parent container ID
                parent_container_id = self.__containers_configlet_list_cache[
                    container_id
                ][Api.generic.PARENT_CONTAINER_ID]

                # Adding current container to cache
                self.__containers_configlet_list_cache[container_id][
                    Api.generic.CONFIGLETS
                ] = configletList
                MODULE_LOGGER.debug(
                    "Cache updated: with configlets {0} from container {1}".format(
                        configletList, container_name
                    )
                )

        MODULE_LOGGER.debug(
            "Container inherited configlet list is: {0}".format(
                inherited_configlet_list
            )
        )
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
        return self.__get_device(search_value=device_lookup, search_by=self.__search_by)

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
            return data[Api.device.SYSMAC]
        return None

    @lru_cache
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
        if self.__search_by in [
            Api.device.FQDN,
            Api.device.SERIAL,
            Api.device.HOSTNAME,
        ]:
            configlet_list = []
            # get_configlets_by_device_id
            try:
                device_id = self.get_device_id(device_lookup=device_lookup)
            except CvpApiError:
                MODULE_LOGGER.error("Error getting device ID from cloudvision")
            else:
                if device_id is None:
                    MODULE_LOGGER.error("Error cannot get device ID from Cloudvision")
                configlets_data = self.__cv_client.api.get_configlets_by_device_id(
                    mac=device_id
                )
                for configlet in configlets_data:
                    configlet_list.append(CvElement(cv_data=configlet))
                MODULE_LOGGER.debug("configlet_list in get_device_configlets function is: %s", str([x.name for x in configlet_list]))
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
            return {
                Api.generic.PARENT_CONTAINER_ID: cv_data[
                    Api.generic.PARENT_CONTAINER_ID
                ],
                Api.generic.PARENT_CONTAINER_NAME: cv_data[Api.device.CONTAINER_NAME],
            }
        return None

    def get_device_image_bundle(self, device_lookup: str):
        """
        get_device_image_bundle Retrieve image bundle attached to the device

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
        MODULE_LOGGER.debug("cv_data lookup returned: %s", str(cv_data))
        if cv_data is not None and Api.generic.IMAGE_BUNDLE_NAME in cv_data:
            if cv_data[Api.generic.IMAGE_BUNDLE_NAME][Api.image.NAME] is None:
                return {
                    Api.generic.IMAGE_BUNDLE_NAME: None,
                    Api.image.ID: None,
                    Api.image.TYPE: None,
                }
            else:
                return {
                    Api.generic.IMAGE_BUNDLE_NAME: cv_data["imageBundle"][
                        Api.image.NAME
                    ],
                    Api.image.ID: cv_data["imageBundle"][Api.image.ID],
                    Api.image.TYPE: cv_data["imageBundle"]["imageBundleMapper"][
                        cv_data["imageBundle"][Api.image.ID]
                    ][Api.image.TYPE],
                }
        return None

    @lru_cache
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
            MODULE_LOGGER.debug("Error getting container ID from Cloudvision")
        else:
            return resp
        return None

    @lru_cache
    def get_container_current(self, device_lookup: str):
        """
        get_container_current Retrieve name of current container where device is attached to

        Parameters
        ----------
        device_lookup : str
            Device name to look for

        Returns
        -------
        dict
            A dict with key and name
        """
        MODULE_LOGGER.debug("Get container for device %s", str(device_lookup))
        container_id = self.get_device_facts(device_lookup=device_lookup)
        if Api.generic.PARENT_CONTAINER_ID in container_id:
            return {
                Api.generic.NAME: container_id[Api.device.CONTAINER_NAME],
                Api.generic.KEY: container_id[Api.generic.PARENT_CONTAINER_ID],
            }
        else:
            return None

    def refresh_systemMacAddress(self, user_inventory: DeviceInventory):
        # sourcery skip: class-extract-method
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
        user_result: list = []
        MODULE_LOGGER.info("Inventory to refresh is %s", str(user_inventory.devices))
        for device in user_inventory.devices:
            MODULE_LOGGER.info("Lookup is based on %s field", str(self.__search_by))
            MODULE_LOGGER.debug("Found device %s to refresh data", str(device.info))
            if device.system_mac is None:
                system_mac = self.get_device_facts(
                    device_lookup=device.info[self.__search_by]
                )[Api.device.SYSMAC]
                MODULE_LOGGER.debug(
                    "Get sysmac %s for device %s", str(device.fqdn), str(system_mac)
                )
                device.system_mac = system_mac

            if device.system_mac is not None:
                user_result.append(device.info)

        MODULE_LOGGER.warning("Update list is: %s", str(user_result))
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
        user_result: list = []
        MODULE_LOGGER.info("Inventory to refresh is %s", str(user_inventory.devices))
        for device in user_inventory.devices:
            MODULE_LOGGER.debug("Found device %s to refresh data", str(device.info))
            if device.system_mac is not None and self.__search_by == Api.device.SYSMAC:
                fqdn = self.get_device_facts(device_lookup=device.system_mac)[
                    Api.device.FQDN
                ]
                MODULE_LOGGER.debug(
                    "Get fqdn %s for device %s", str(fqdn), str(device.system_mac)
                )
                device.fqdn = fqdn
                user_result.append(device.info)
            elif (
                device.serial_number is not None
                and self.__search_by == Api.device.SERIAL
            ):
                fqdn = self.get_device_facts(device_lookup=device.serial_number)[
                    Api.device.FQDN
                ]
                MODULE_LOGGER.debug(
                    "Get fqdn %s for device %s", str(fqdn), str(device.serial_number)
                )
                device.fqdn = fqdn
                user_result.append(device.info)
            else:
                MODULE_LOGGER.debug("Skipping following device: %s", device.info)

        MODULE_LOGGER.warning("Update list is: %s", str(user_result))
        return DeviceInventory(data=user_result)

    def check_device_exist(
        self, user_inventory: DeviceInventory, search_mode: str = Api.device.FQDN
    ):
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
        MODULE_LOGGER.debug("Check if all the devices specified exist in CVP")
        device_not_present: list = []
        for device in user_inventory.devices:
            if (
                self.__search_by == Api.device.HOSTNAME
                or search_mode == Api.device.HOSTNAME
            ):
                if (
                    self.is_device_exist(device.fqdn, search_mode=Api.device.HOSTNAME)
                    is False
                ):
                    device_not_present.append(device.fqdn)
                    MODULE_LOGGER.error(
                        "Device not present in CVP but in the user_inventory: %s",
                        device.fqdn,
                    )

            elif self.__search_by == Api.device.FQDN or search_mode == Api.device.FQDN:
                if (
                    self.is_device_exist(device.fqdn, search_mode=Api.device.FQDN)
                    is False
                ):
                    device_not_present.append(device.fqdn)
                    MODULE_LOGGER.error(
                        "Device not present in CVP but in the user_inventory: %s",
                        device.fqdn,
                    )

            elif self.__search_by == Api.device.SYSMAC:
                if self.is_device_exist(device.system_mac) is False:
                    device_not_present.append(
                        device.system_mac, search_mode=Api.device.SYSMAC
                    )
                    MODULE_LOGGER.error(
                        "Device not present in CVP but in the user_inventory: %s",
                        device.system_mac,
                    )
            elif search_mode == Api.device.SERIAL:
                if (
                    self.is_device_exist(
                        device.serial_number, search_mode=Api.device.SERIAL
                    )
                    is False
                ):
                    device_not_present.append(device.serial_number)
                    MODULE_LOGGER.error(
                        "Device not present in CVP but in the user_inventory: %s",
                        device.serial_number,
                    )
        return device_not_present

    # ------------------------------------------ #
    # Workers function
    # ------------------------------------------ #

    def manager(
        self,
        user_inventory: DeviceInventory,
        search_mode: str = Api.device.HOSTNAME,
        apply_mode: str = ModuleOptionValues.APPLY_MODE_LOOSE,
        state: str = ModuleOptionValues.STATE_MODE_PRESENT,
        inventory_mode: str = ModuleOptionValues.INVENTORY_MODE_STRICT,
    ):
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
        state: str, optional
            Define if devices must be provisioned or reset to default configuration.
        inventory_mode: str, optional
            Define how manager will handle missing devices: loose (ignore missing devices) or strict (fail on missing devices)

        Returns
        -------
        dict
            All Ansible output formated using CvAnsibleResponse
        """
        response = CvAnsibleResponse()
        self.__search_by = search_mode
        MODULE_LOGGER.debug("Manager search mode is set to: %s", str(self.__search_by))

        if state == ModuleOptionValues.STATE_MODE_PRESENT:
            MODULE_LOGGER.info("Processing data to create/update devices")
            response = self.__state_present(
                user_inventory=user_inventory,
                apply_mode=apply_mode,
                inventory_mode=inventory_mode,
            )

        elif state == ModuleOptionValues.STATE_MODE_ABSENT:
            MODULE_LOGGER.info("Processing data to reset devices")
            response = self.__state_factory_reset(
                user_inventory=user_inventory, inventory_mode=inventory_mode
            )

        elif state == ModuleOptionValues.STATE_MODE_REMOVE:
            MODULE_LOGGER.info("Processing data to reset devices")
            response = self.__state_provisioning_reset(
                user_inventory=user_inventory, inventory_mode=inventory_mode
            )

        elif state == ModuleOptionValues.STATE_MODE_DECOMM:
            MODULE_LOGGER.info("Processing data to decommission devices")
            response = self.__state_absent(
                user_inventory=user_inventory, inventory_mode=inventory_mode
            )

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
        results = []
        for device in user_inventory.devices:
            result_data = CvApiResult(
                action_name="{0}_to_{1}".format(device.fqdn, device.container)
            )
            if device.system_mac is not None:
                new_container_info = self.get_container_info(
                    container_name=device.container
                )
                if new_container_info is None:
                    error_message = f"The target container '{device.container}' for the device '{device.fqdn}' does not exist on CVP."
                    MODULE_LOGGER.error(error_message)
                    self.__ansible.fail_json(msg=error_message)

                current_container_info = self.get_container_current(
                    device_lookup=device.info[self.__search_by]
                )

                # Move devices when they are not in undefined container
                if (
                    current_container_info is not None
                    and current_container_info[Api.generic.NAME]
                    != Api.container.UNDEFINED_CONTAINER_ID
                    and current_container_info[Api.generic.NAME] != device.container
                ):
                    if self.__check_mode:
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = ["unsupported_in_check_mode"]
                    else:
                        try:
                            resp = self.__cv_client.api.move_device_to_container(
                                app_name="CvDeviceTools.move_device",
                                device=device.info,
                                container=new_container_info,
                                create_task=True,
                            )
                        except CvpApiError:
                            error_message = f"Error to move device {device.fqdn} to container {device.container}"
                            MODULE_LOGGER.error(error_message)
                            self.__ansible.fail_json(msg=error_message)
                        except CvpRequestError:
                            error_message = f"Move device {device.fqdn} to container {device.container} failed. User is unauthorized!"
                            MODULE_LOGGER.error(error_message)
                            self.__ansible.fail_json(msg=error_message)
                        else:
                            if resp and resp['data']['status'] == 'success':
                                result_data.changed = True
                                result_data.success = True
                                result_data.taskIds = resp["data"][Api.task.TASK_IDS]

                    result_data.add_entry(
                        "{0}-{1}".format(device.fqdn, device.container)
                    )
            results.append(result_data)
        return results

    def apply_bundle(self, user_inventory: DeviceInventory):
        """
        apply_bundle - apply an image bundle to a device

        Execute the API calls to attach an image bundle to a device.
        Note that only 1 image bundle can be attached to a device.

        If an image bundle is already attached to the device (type: netelement)
        the new image bundle will replace the old.

        Our behaviour is as follows;
        * Bundle already attached to the device - update if different, skip if the same
        * Bundle inherited from container (type: container) - attach bundle to device, regardless
        of whether or not it is the same

        Parameters
        ----------
        user_inventory : DeviceInventory
            Ansible inventory to configure on Cloudvision

        Returns
        -------
        list
            List of CvApiResult for all API calls
        """
        results = []

        for device in user_inventory.devices:
            MODULE_LOGGER.debug(
                "Applying image bundle for device: %s", str(device.fqdn)
            )
            result_data = CvApiResult(
                action_name=device.fqdn + "_image_bundle_attached"
            )

            # We can't attach/detach an image to a device in the undefined container
            current_container_info = self.get_container_current(
                device_lookup=device.info[self.__search_by]
            )
            if (
                device.configlets is None
                or current_container_info[Api.generic.NAME]
                == Api.container.UNDEFINED_CONTAINER_ID
            ):
                MODULE_LOGGER.debug(
                    "The device is in undefined container"
                )
                continue

            # GET IMAGE BUNDLE
            MODULE_LOGGER.debug(
                "Attempting to get current image bundle for %s using %s",
                str(device.fqdn),
                str(device.info[self.__search_by]),
            )
            current_image_bundle = self.get_device_image_bundle(
                device_lookup=device.info[self.__search_by]
            )
            MODULE_LOGGER.debug(
                "Current image bundle assigned is: %s", str(current_image_bundle)
            )
            MODULE_LOGGER.debug(
                "User assigned image bundle is: %s", str(device.image_bundle)
            )

            if device.image_bundle is not None:
                if (
                    current_image_bundle and
                    device.image_bundle
                    == current_image_bundle[Api.generic.IMAGE_BUNDLE_NAME]
                    and current_image_bundle[Api.image.TYPE] == "netelement"
                ):
                    MODULE_LOGGER.debug(
                        "No actions needed for device: %s", str(device.fqdn)
                    )
                    MODULE_LOGGER.debug(
                        "%s has %s assigned and applied",
                        str(device.fqdn),
                        current_image_bundle[Api.generic.IMAGE_BUNDLE_NAME],
                    )
                    pass
                    # Nothing to do
                else:
                    MODULE_LOGGER.debug(
                        "Updating %s to use image bundle: %s",
                        str(device.fqdn),
                        str(device.image_bundle),
                    )

                    # get device facts from CV
                    device_facts = self.get_device_facts(
                        device_lookup=device.info[self.__search_by]
                    )

                    assigned_image_facts = (
                        self.__cv_client.api.get_image_bundle_by_name(
                            device.image_bundle
                        )
                    )
                    if assigned_image_facts is None:
                        MODULE_LOGGER.error(
                            "Error image bundle %s not found", str(device.image_bundle)
                        )
                        self.__ansible.fail_json(
                            msg=f"Error applying bundle to device {device.fqdn}: {str(device.image_bundle)} not found"
                        )

                    MODULE_LOGGER.debug(
                        "%s image bundle facts are: %s",
                        str(device.image_bundle),
                        str(assigned_image_facts),
                    )

                    if self.__check_mode:
                        result_data.changed = False
                        result_data.success = True
                        result_data.taskIds = ["check_mode"]
                        MODULE_LOGGER.warning(
                            "[check_mode] - Fake assign of %s to %s",
                            str(device.image_bundle),
                            device.hostname,
                        )
                    else:
                        try:
                            resp = self.__cv_client.api.apply_image_to_element(
                                assigned_image_facts,
                                device_facts,
                                device.hostname,
                                "netelement",
                            )

                        except CvpApiError as catch_error:
                            MODULE_LOGGER.error(
                                "Error applying bundle to device: %s", str(catch_error)
                            )
                            self.__ansible.fail_json(
                                msg=f"Error applying bundle to device {device.fqdn}: {str(catch_error)}"
                            )
                        except CvpRequestError as catch_error:
                            MODULE_LOGGER.error(
                                "Error applying bundle to device: %s", str(catch_error)
                            )
                            self.__ansible.fail_json(
                                msg=f"Error applying bundle to device {device.fqdn}: {str(catch_error)}"
                            )
                        else:
                            if resp and resp["data"]["status"] == "success":
                                result_data.changed = True
                                result_data.success = True
                                result_data.taskIds = resp["data"][Api.task.TASK_IDS]
                                result_data.add_entry(f"{device.image_bundle} apply to {device.fqdn}")

                results.append(result_data)

        return results

    def detach_bundle(self, user_inventory: DeviceInventory):
        """
        detach_bundle - detach an image bundle from a device

        Execute the API calls to detach an image bundle from a device.

        Parameters
        ----------
        user_inventory : DeviceInventory
            Ansible inventory to configure on Cloudvision

        Returns
        -------
        list
            List of CvApiResult for all API calls
        """
        results = []

        for device in user_inventory.devices:
            MODULE_LOGGER.debug(
                "Detaching image bundle from device: %s", str(device.fqdn)
            )
            result_data = CvApiResult(
                action_name=device.fqdn + "_image_bundle_detached"
            )

            # We can't attach/detach an image to a device in the undefined container
            current_container_info = self.get_container_current(
                device_lookup=device.info[self.__search_by]
            )
            if (
                device.configlets is None
                or current_container_info[Api.generic.NAME]
                == Api.container.UNDEFINED_CONTAINER_ID
            ):
                continue

            # GET IMAGE BUNDLE
            MODULE_LOGGER.debug(
                "Attempting to get current image bundle for %s using %s",
                str(device.fqdn),
                str(device.info[self.__search_by]),
            )
            current_image_bundle = self.get_device_image_bundle(
                device_lookup=device.info[self.__search_by]
            )
            MODULE_LOGGER.debug(
                "Current image bundle assigned is: %s", str(current_image_bundle)
            )

            # Check to make sure that the assigned image isn't inherited from the container
            if (
                current_image_bundle is not None
                and current_image_bundle[Api.image.TYPE] == "netelement"
            ):
                if device.image_bundle is None:

                    # get device facts from CV
                    device_facts = self.get_device_facts(
                        device_lookup=device.info[self.__search_by]
                    )

                    assigned_image_facts = (
                        self.__cv_client.api.get_image_bundle_by_name(
                            current_image_bundle[Api.generic.IMAGE_BUNDLE_NAME]
                        )
                    )

                    if self.__check_mode:
                        result_data.changed = False
                        result_data.success = True
                        result_data.taskIds = ["check_mode"]
                        MODULE_LOGGER.warning(
                            "[check_mode] - Fake removal of image bundle from %s",
                            device.hostname,
                        )
                    else:
                        try:
                            resp = self.__cv_client.api.remove_image_from_element(
                                assigned_image_facts,
                                device_facts,
                                device.hostname,
                                "netelement",
                            )

                        except CvpApiError as catch_error:
                            MODULE_LOGGER.error(
                                "Error removing bundle from device: %s",
                                str(catch_error),
                            )
                            self.__ansible.fail_json(
                                msg=f"Error removing bundle from device {device.fqdn}: {str(catch_error)}"
                            )
                        else:
                            if resp and resp["data"]["status"] == "success":
                                result_data.changed = True
                                result_data.success = True
                                result_data.taskIds = resp["data"][Api.task.TASK_IDS]
                                result_data.add_entry(f"{device.image_bundle} detach from {device.fqdn}")

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
        results = []
        MODULE_LOGGER.debug(
            "Apply configlets to following inventory: %s",
            str([x.info for x in user_inventory.devices]),
        )
        for device in user_inventory.devices:
            MODULE_LOGGER.debug("Applying configlet for device: %s", str(device.fqdn))
            result_data = CvApiResult(action_name=device.fqdn + "_configlet_attached")
            current_container_info = self.get_container_current(
                device_lookup=device.info[self.__search_by]
            )
            if (
                device.configlets is None
                or current_container_info[Api.generic.NAME]
                == Api.container.UNDEFINED_CONTAINER_ID
            ):
                continue
            # get configlet information from CV
            configlets_attached = []
            if self.__search_by == Api.device.SERIAL:
                configlets_attached = self.get_device_configlets(
                    device_lookup=device.serial_number
                )
            elif self.__search_by == Api.device.HOSTNAME:
                configlets_attached = self.get_device_configlets(
                    device_lookup=device.hostname
                )
            else:
                configlets_attached = self.get_device_configlets(
                    device_lookup=device.fqdn
                )
            configlets_attached_before_changes = [x.name for x in configlets_attached]

            configlets_reordered_list = self.__get_reordered_configlets_list(
                configlets_attached, device.configlets
            )

            # Check if changes have been made
            MODULE_LOGGER.debug(
                "[%s] - Old configlet list: %s",
                str(device.fqdn),
                str(configlets_attached_before_changes),
            )
            MODULE_LOGGER.debug(
                "[%s] - New configlet list: %s",
                str(device.fqdn),
                str([x[Api.generic.NAME] for x in configlets_reordered_list]),
            )
            if str(configlets_attached_before_changes) == str(
                [x[Api.generic.NAME] for x in configlets_reordered_list]
            ):
                MODULE_LOGGER.info(
                    "[%s] - There was no changes detected in the configlets list, skipping task creation for the device.",
                    str(device.fqdn),
                )
                continue

            MODULE_LOGGER.info(
                "Creating task for device [%s] configlet list is: %s",
                str(device.fqdn),
                str([x[Api.generic.NAME] for x in configlets_reordered_list]),
            )
            # get device facts from CV
            device_facts = self.get_device_facts(
                device_lookup=device.info[self.__search_by]
            )

            # Attach configlets to device
            if len(configlets_reordered_list) > 0:
                if self.__check_mode:
                    result_data.changed = False
                    result_data.success = True
                    result_data.taskIds = ["check_mode"]
                    MODULE_LOGGER.warning(
                        "[check_mode] - Fake appcation of %d configlets to %s",
                        len(configlets_reordered_list),
                        device.hostname,
                    )
                else:
                    try:
                        resp = self.__cv_client.api.apply_configlets_to_device(
                            app_name="CvDeviceTools.apply_configlets",
                            dev=device_facts,
                            new_configlets=configlets_reordered_list,
                            create_task=True,
                            reorder_configlets=True,
                        )
                    except TypeError:
                        error_message = "The function to reorder the configlet is not present. Please, check your cvprac version (>= 1.0.7 required)."
                        MODULE_LOGGER.error(error_message)
                        self.__ansible.fail_json(msg=error_message)
                    except CvpApiError:
                        MODULE_LOGGER.error("Error applying configlets to device")
                        self.__ansible.fail_json(
                            msg="Error applying configlets to device"
                        )
                    except CvpRequestError:
                        message = "Failed to apply configlets to device. User is unauthorized!"
                        MODULE_LOGGER.error(message)
                        self.__ansible.fail_json(msg=message)
                    else:
                        if resp["data"]["status"] == "success":
                            result_data.changed = True
                            result_data.success = True
                            result_data.taskIds = resp["data"][Api.task.TASK_IDS]
                            for configlet in device.configlets:
                                result_data.add_entry(
                                    "{0} adds {1}".format(device.fqdn, configlet)
                                )
                            MODULE_LOGGER.debug("CVP response is: %s", str(resp))
                            MODULE_LOGGER.info(
                                "Reponse data is: %s", str(result_data.results)
                            )
            else:
                result_data.name = result_data.name + " - nothing attached"
            results.append(result_data)
        return results

    def detach_configlets(self, user_inventory: DeviceInventory):
        results = []
        for device in user_inventory.devices:
            result_data = CvApiResult(action_name=device.fqdn + "_configlet_removed")
            # FIXME: Should we ignore devices listed with no configlets ?
            MODULE_LOGGER.debug("Device configlet list is: %s", str(device.configlets))
            if device.configlets is not None:
                # get device facts from CV
                device_facts = self.get_device_facts(
                    device_lookup=device.info[self.__search_by]
                )

                # List of expected configlet applied to the device, taking into account the configlets inherited from parent containers
                expected_device_configlet_list = (
                    self.__get_configlet_list_inherited_from_container(device)
                    + device.configlets
                )
                MODULE_LOGGER.debug("Expected configlet list is: %s", str(expected_device_configlet_list))
                configlets_to_remove = []

                # get list of configured configlets
                configlets_attached = self.get_device_configlets(
                    device_lookup=device.info[self.__search_by]
                )
                MODULE_LOGGER.debug(
                    "Current configlet attached lru cache {0}".format(
                        [x.name for x in configlets_attached]
                    )
                )
                MODULE_LOGGER.debug("Configlets attached raw data {0}".format(configlets_attached))
                # For each configlet not in the list, add to list of configlets to remove
                for configlet in configlets_attached:
                    if configlet.name not in expected_device_configlet_list:
                        MODULE_LOGGER.info(
                            "Configlet [%s] is added to detach list",
                            str(configlet.name),
                        )
                        result_data.name = result_data.name + " - " + configlet.name
                        configlets_to_remove.append(configlet.data)
                # Detach configlets to device
                if configlets_to_remove:
                    MODULE_LOGGER.debug(
                        "List of configlet to remove for device {0} is {1}".format(
                            device.fqdn,
                            [x[Api.generic.NAME] for x in configlets_to_remove],
                        )
                    )
                    if self.__check_mode:
                        result_data.changed = False
                        result_data.success = True
                        result_data.taskIds = ["check_mode"]
                        MODULE_LOGGER.warning(
                            "[check_mode] - Fake detach of %d configlets from %s",
                            len(configlets_to_remove),
                            device.hostname,
                        )
                    else:
                        try:
                            resp = self.__cv_client.api.remove_configlets_from_device(
                                app_name="CvDeviceTools.detach_configlets",
                                dev=device_facts,
                                del_configlets=configlets_to_remove,
                                create_task=True,
                            )
                        except CvpApiError as catch_error:
                            MODULE_LOGGER.error(
                                "Error applying configlets to device: %s",
                                str(catch_error),
                            )
                            self.__ansible.fail_json(
                                msg=f"Error detaching configlets from device {device.fqdn}: {catch_error}"
                            )
                        except CvpRequestError:
                            MODULE_LOGGER.error("Error detaching configlets to device. User is unauthorized!")
                            self.__ansible.fail_json(
                                msg="Error detaching configlets to device. User is unauthorized!"
                            )
                        else:
                            if resp["data"]["status"] == "success":
                                result_data.changed = True
                                result_data.success = True
                                result_data.taskIds = resp["data"][Api.task.TASK_IDS]
                                for configlet in configlets_to_remove:
                                    result_data.add_entry(
                                        "{0} removes {1}".format(
                                            device.fqdn, configlet
                                        )
                                    )
                else:
                    result_data.name = result_data.name + " - nothing detached"
                results.append(result_data)
        return results

    def remove_configlets(self, user_inventory: DeviceInventory):
        """
        remove_configlets UNSUPPORTED and NOT TESTED YET
        """
        results = []
        for device in user_inventory.devices:
            result_data = CvApiResult(action_name=device.fqdn + "_configlet_removed")
            if device.configlets is not None:
                # get configlet information from CV
                configlets_info = [
                    self.__get_configlet_info(configlet_name=configlet)
                    for configlet in device.configlets
                ]

                # get device facts from CV
                device_facts = self.get_device_facts(
                    device_lookup=device.info[self.__search_by]
                )

                # Attach configlets to device
                if self.__check_mode:
                    result_data.changed = False
                    result_data.success = True
                    result_data.taskIds = ["check_mode"]
                    MODULE_LOGGER.warning(
                        "[check_mode] - Fake removal of %d configlets from %s",
                        len(configlets_info),
                        device.hostname,
                    )
                else:
                    try:
                        resp = self.__cv_client.api.remove_configlets_from_device(
                            app_name="CvDeviceTools.remove_configlets",
                            dev=device_facts,
                            del_configlets=configlets_info,
                            create_task=True,
                        )
                    except CvpApiError:
                        MODULE_LOGGER.error("Error removing configlets to device")
                        self.__ansible.fail_json(
                            msg="Error removing configlets to device"
                        )
                    else:
                        if resp["data"]["status"] == "success":
                            result_data.changed = True
                            result_data.success = True
                            result_data.taskIds = resp["data"][Api.task.TASK_IDS]
                            result_data.add_entry(
                                "{} removes {}".format(device.fqdn, *device.configlets)
                            )
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
        results = []
        for device in user_inventory.devices:
            result_data = CvApiResult(
                action_name=device.info[self.__search_by] + "_deployed"
            )
            if device.system_mac is not None:
                configlets_info = []
                for configlet in device.configlets:
                    new_configlet = self.__get_configlet_info(configlet_name=configlet)
                    if new_configlet is None:
                        error_message = "The configlet '{0}' defined to be applied on the device '{1}' does not \
                            exist on the CVP server.".format(
                            str(configlet), str(device.fqdn)
                        )
                        MODULE_LOGGER.error(error_message)
                        self.__ansible.fail_json(msg=error_message)
                    else:
                        configlets_info.append(new_configlet)
                # Move devices when they are not in undefined container
                current_container_info = self.get_container_current(
                    device_lookup=device.info[self.__search_by]
                )

                MODULE_LOGGER.debug(
                    "Device {0} is currently under {1}".format(
                        device.fqdn, current_container_info[Api.generic.NAME]
                    )
                )
                device_info = self.get_device_facts(
                    device_lookup=device.info[self.__search_by]
                )
                if (
                    current_container_info[Api.generic.NAME]
                    == Api.container.UNDEFINED_CONTAINER_NAME
                ):
                    if self.__check_mode:
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = ["unsupported_in_check_mode"]
                    else:
                        # Check if the target container exists
                        target_container_info = self.get_container_info(
                            container_name=device.container
                        )
                        if target_container_info is None:
                            error_message = "The target container '{0}' for the device '{1}' does not exist on CVP.".format(
                                device.container, device.fqdn
                            )
                            MODULE_LOGGER.error(error_message)
                            self.__ansible.fail_json(msg=error_message)
                        try:
                            MODULE_LOGGER.debug(
                                "Ansible is going to deploy device %s in container %s with configlets %s",
                                str(device.fqdn),
                                str(device.container),
                                str(configlets_info),
                            )
                            resp = self.__cv_client.api.deploy_device(
                                app_name="CvDeviceTools.deploy",
                                device=device_info,
                                container=device.container,
                                configlets=configlets_info,
                                create_task=True,
                            )
                        except CvpApiError as error:
                            self.__ansible.fail_json(
                                msg=f"Error to deploy device {device.fqdn} to container {device.container}"
                            )
                            MODULE_LOGGER.critical(
                                "Error deploying device {0} : {1}".format(
                                    device.fqdn, error
                                )
                            )
                        else:
                            if resp["data"]["status"] == "success":
                                result_data.changed = True
                                result_data.success = True
                                result_data.taskIds = resp["data"][Api.task.TASK_IDS]

                    result_data.add_entry(
                        "{0} deployed to {1}".format(
                            device.info[self.__search_by], device.container
                        )
                    )
            results.append(result_data)
        return results

    def delete_device(self, user_inventory: DeviceInventory):
        results = []
        for device in user_inventory.devices:
            MODULE_LOGGER.info("removing device %s from provisioning", str(device.info))
            result_data = CvApiResult(
                action_name=device.info[self.__search_by] + "_delete"
            )
            if self.__check_mode:
                result_data.changed = False
                result_data.success = True
                result_data.taskIds = ["check_mode"]
                MODULE_LOGGER.warning(
                    "[check_mode] - Fake removal of device %s", device.hostname
                )
            else:
                try:
                    MODULE_LOGGER.info(
                        "send reset request for device %s", str(device.info)
                    )
                    resp = self.__cv_client.api.delete_device(device.system_mac)
                except CvpApiError:
                    MODULE_LOGGER.error("Error removing device from provisioning")
                    self.__ansible.fail_json(
                        msg="Error removing device from provisioning"
                    )
                except CvpRequestError:
                    message = "Failed to remove device from provisioning. User is unauthorized!"
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
                else:
                    if resp["result"] == "success":
                        result_data.changed = True
                        result_data.success = True
                        result_data.add_entry(
                            "{0} has been successfully deleted". format(device.fqdn)
                        )
            results.append(result_data)
        return results

    def decommission_device(self, user_inventory: DeviceInventory):
        results = []
        decomm_success = "DECOMMISSIONING_STATUS_SUCCESS"
        decomm_failure = "DECOMMISSIONING_STATUS_FAILURE"
        for device in user_inventory.devices:
            MODULE_LOGGER.info("removing device %s from provisioning", str(device.info))
            result_data = CvApiResult(
                action_name=device.info[self.__search_by] + "_delete"
            )
            try:
                MODULE_LOGGER.info("send reset request for device %s", str(device.info))
                req_id = str(uuid.uuid4())
                device_fact = self.get_device_facts(device_lookup=device.hostname)
                device_id = device_fact["serialNumber"]
                MODULE_LOGGER.info("Found device serial number: %s", device_id)
                if self.__check_mode:
                    result_data.changed = False
                    result_data.success = True
                    result_data.taskIds = ["check_mode"]
                    MODULE_LOGGER.warning(
                        "[check_mode] - Fake decomissioning of device %s",
                        device.hostname,
                    )
                else:
                    self.__cv_client.api.device_decommissioning(device_id, req_id)
            except CvpApiError:
                MODULE_LOGGER.error("Error decommissioning device")
                self.__ansible.fail_json(msg="Error decommissioning device")
            except CvpRequestError as e:
                if "403 Forbidden" in e.msg:
                    request_err_msg = f"Failed to decommission device {device_id}. User is unauthorized!"
                else:
                    request_err_msg = f"Device with {device_id} does not exist or is not registered to decommission"
                MODULE_LOGGER.error(request_err_msg)
                self.__ansible.fail_json(msg=request_err_msg)
            else:
                if self.__check_mode:
                    status = decomm_success
                else:
                    status = ""

                while status != decomm_success:
                    try:
                        decomm_state_fact = (
                            self.__cv_client.api.device_decommissioning_status_get_one(
                                req_id
                            )
                        )
                        status = decomm_state_fact["value"]["status"]
                    except CvpRequestError:
                        continue
                    if status == decomm_failure:
                        err_msg = decomm_state_fact["value"]["error"]
                        msg = f"Device decommissioning failed due to {err_msg}"
                        MODULE_LOGGER.error(msg)
                        self.__ansible.fail_json(msg=msg)
                    else:
                        time.sleep(10)
                if not self.__check_mode:
                    result_data.changed = True
                    result_data.add_entry(
                        "{0} has been successfully decommissioned". format(device.fqdn)
                    )
                result_data.success = True

            results.append(result_data)
        return results

    def reset_device(self, user_inventory: DeviceInventory):
        results = []
        for device in user_inventory.devices:
            MODULE_LOGGER.info("start process resetting device %s", str(device.info))
            result_data = CvApiResult(
                action_name=device.info[self.__search_by] + "_reset"
            )
            if self.__check_mode:
                result_data.changed = False
                result_data.success = True
                result_data.taskIds = ["check_mode"]
                MODULE_LOGGER.warning(
                    "[check_mode] - Fake resetting of device %s", device.hostname
                )
            else:
                try:
                    MODULE_LOGGER.info(
                        "send reset request for device %s", str(device.info)
                    )
                    resp = self.__cv_client.api.reset_device(
                        app_name="CvDeviceTools.reset_device",
                        device=device.info,
                        create_task=True,
                    )
                except CvpApiError:
                    MODULE_LOGGER.error("Error resetting device")
                    self.__ansible.fail_json(msg="Error resetting device")
                except CvpRequestError:
                    message = "Failed to reset device. Users is unauthorized!"
                    MODULE_LOGGER.error(message)
                    self.__ansible.fail_json(msg=message)
                else:
                    if resp and resp["data"]["status"] == "success":
                        result_data.changed = True
                        result_data.success = True
                        result_data.taskIds = resp["data"][Api.task.TASK_IDS]
                        result_data.add_entry(f"{device.fqdn} resets {device.configlets}")
            results.append(result_data)
        return results

    # ------------------------------------------ #
    # Helpers function
    # ------------------------------------------ #

    def list_devices_to_move(self, inventory: DeviceInventory):
        """
        list_devices_to_move UNSUPPORTED and NOT TESTED YET
        """
        devices_to_move = []
        for device in inventory.devices:
            if self.__search_by == Api.device.FQDN:
                if (
                    self.is_in_container(
                        device_lookup=device.fqdn, container_name=device.container
                    )
                    is False
                ):
                    devices_to_move.append(device)
            elif self.__search_by == Api.device.SYSMAC:
                if (
                    self.is_in_container(
                        device_lookup=device.system_mac, container_name=device.container
                    )
                    is False
                ):
                    devices_to_move.append(device)
            elif self.__search_by == Api.device.SERIAL:
                if (
                    self.is_in_container(
                        device_lookup=device.serial_number,
                        container_name=device.container,
                    )
                    is False
                ):
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
        if data is not None and Api.generic.PARENT_CONTAINER_ID in data:
            container_data = self.get_container_info(container_name=container_name)
            if (
                container_data is not None
                and container_data[Api.generic.KEY]
                == data[Api.generic.PARENT_CONTAINER_ID]
            ):
                return True
        return False

    def is_device_exist(
        self, device_lookup: str, search_mode: str = Api.device.HOSTNAME
    ):
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
        data = self.__get_device(search_value=device_lookup, search_by=search_mode)
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
