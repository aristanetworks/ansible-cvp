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
import string
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import (
    ModuleOptionValues,
    DeviceResponseFields,
)
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas import v3 as schema
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import validate_json_schema
try:
    from cvprac.cvp_client_errors import CvpApiError
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info('Start tag_tools module execution')


class CvValidateInput(object):
    def __init__(self, device: dict, schema=schema.SCHEMA_CV_VALIDATE):
        self.__device = device
        self.__schema = schema

    @property
    def is_valid(self):
        """
        check_schemas Validate schemas for user's input
        """
        if not validate_json_schema(user_json=self.__device, schema=self.__schema):
            MODULE_LOGGER.error("Invalid tags input : \n%s", str(self.__device))
            return False
        return True


class CvValidationTools(object):
    """
    CvValidationTools Class to manage CloudVision configlet validation related tasks
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module

    def get_system_mac(self, search_value: str, search_type: str = 'fqdn'):
        """
        get_system_mac Get serial number from FQDN or hostname or serialNumber

        Parameters
        ----------
        search_value: str
            search string of the switch in CloudVision

        search_type: str
            type of search string. Can be fqdn, hostname or serialNum

        Returns
        -------
        str
            system mac of the switch
        """
        # lookup by fqdn
        if search_type == 'fqdn':
            device_details = self.__cv_client.api.get_device_by_name(fqdn=search_value)
            if "systemMacAddress" in device_details.keys():
                return device_details["systemMacAddress"]
        # lookup by hostname(by splitting fqdn filed on dots and taking the first split as hostname)
        if search_type == 'hostname':
            device_details = self.__cv_client.api.get_device_by_name(
                fqdn=search_value, search_by_hostname=True)
            if "systemMacAddress" in device_details.keys():
                return device_details["systemMacAddress"]
        # lookup by serialNumber
        if search_type == 'serialNum':
            device_details = self.__cv_client.api.get_device_by_serial(device_serial=search_value)
            if "systemMacAddress" in device_details.keys():
                return device_details["systemMacAddress"]
        self.__ansible.fail_json(msg=f"Error, Device {search_value} doesn't exists on CV. Check the hostname/fqdn")

    def get_configlet_by_name(self, configlet_name):
        """
        get_configlet_by_name Get configlet information from CVP using configlet name

        Parameters
        ----------
        configlet_name: str
            name of the configlet

        Returns
        -------
        dict
            the configlet dict
        """
        resp = self.__cv_client.api.get_configlet_by_name(configlet_name)
        if 'errorCode' in resp.keys():
            return {}
        return resp

    def manager(self, devices: list, validate_mode: string):
        """
        manager Generic entry point to manage configlet validation related tasks

        Parameters
        ----------
        devices: list
            devices information to validate configlet against
        validation_mode: string
            validation mode
        source: string
            location of configlet to be validated
        Returns
        -------
        CvAnsibleResponse
            Data structure to pass to ansible module.

        """
        ansible_response = CvAnsibleResponse()
        validation_manager = CvManagerResult(builder_name=DeviceResponseFields.CONFIGLET_VALIDATED)

        results = []
        device_data = {
            "warnings": [],
            "errors": [],
            "configlets_validated_count": 0,
            "configlets_validated_list": [],
            "diff": {},
            "success": True,
            "taskIds": [],
        }
        for device_info in devices:
            # look up system mac address using fqdn, hostname or serialNum. default=hostname
            if 'search_type' in device_info:
                if device_info['search_type'] == 'fqdn':
                    system_mac = self.get_system_mac(device_info['device_name'], search_type='fqdn')
                elif device_info['search_type'] == 'hostname':
                    system_mac = self.get_system_mac(device_info['device_name'], search_type='hostname')
                elif device_info['search_type'] == 'serialNumber':
                    system_mac = self.get_system_mac(device_info['device_name'], search_type='serialNum')
            else:
                system_mac = self.get_system_mac(device_info['device_name'], search_type='hostname')

            if system_mac is None:
                continue
            device_infokeys = device_info.keys()
            configlets = {}
            if 'cvp_configlets' in device_infokeys:
                for configlet in device_info['cvp_configlets']:
                    vc_configlet = self.get_configlet_by_name(configlet)
                    if not vc_configlet:
                        error_message = f"The configlet '{configlet}' defined to be validated \
                            against device '{device_info['fqdn']}' does not exist on the CVP server."
                        MODULE_LOGGER.error(error_message)
                        self.__ansible.fail_json(msg=error_message)
                    configlets.update({vc_configlet['name']: vc_configlet['config']})

            if 'local_configlets' in device_infokeys:
                for configlet_name, data in device_info['local_configlets'].items():
                    configlets.update({configlet_name: data})

            for configlet_name, config in configlets.items():
                MODULE_LOGGER.debug(
                    "Configlet being validated is %s", str(configlet_name))
                MODULE_LOGGER.debug("Configlet information: %s", str(config))

                result_data = CvApiResult(
                    action_name=configlet_name
                    + "_on_"
                    + device_info['search_type']
                    + "_validated"
                )
                MODULE_LOGGER.debug(f"adding {0} to result_data".format(configlet_name))
                try:
                    MODULE_LOGGER.debug(
                        "Ansible is going to validate configlet %s against device %s", str(
                            configlet_name), str(device_info['device_name']))
                    MODULE_LOGGER.debug(
                        "queryParams are deviceMac: %s and configuration: %s", str(
                            system_mac), str(config))
                    resp = self.__cv_client.api.validate_config_for_device(
                        device_mac=system_mac,
                        config=config)
                    result_data.add_entry(
                        configlet_name + "_validated_against_" + device_info['device_name']
                    )
                    result_data.success = True

                except CvpApiError:
                    MODULE_LOGGER.critical(
                        "Error validation failed on device %s", str(device_info['device_name'])
                    )
                    self.__ansible.fail_json(
                        msg=f"Error validation failed on device {device_info['device_name']}")
                else:
                    if "result" in resp:
                        result_data.success = True
                    if "warnings" in resp and resp["warningCount"] > 0:
                        err_msg = resp["warnings"]
                        msg = f"Configlet validation failed with {err_msg}"
                        result_data.success = True
                        MODULE_LOGGER.error(msg)
                        device_data["warnings"].append(
                            {"device": device_info['device_name'], "configlet_name": configlet_name, "warnings": err_msg}
                        )
                        result_data.add_warning(
                            {"device": device_info['device_name'], "configlet_name": configlet_name, "warnings": err_msg}
                        )
                    if "errors" in resp:
                        err_msg = resp["errors"]
                        msg = f"Configlet validation failed with {err_msg}"
                        result_data.success = True
                        MODULE_LOGGER.error(msg)
                        device_data["errors"].append(
                            {"device": device_info['device_name'], "configlet_name": configlet_name, "errors": err_msg}
                        )
                        result_data.add_errors(
                            {"device": device_info['device_name'], "configlet_name": configlet_name, "errors": err_msg}
                        )
                results.append(result_data)
                device_data["configlets_validated_count"] += 1
                device_data["configlets_validated_list"].append(
                    configlet_name + "_on_" + device_info['device_name'] + "_validated"
                )
        if len(device_data["errors"]) > 0:
            message = (
                f"Encountered {len(device_data['errors'])} errors during"
                " validation. Refer to 'configlets_validated' for more details."
            )
            if validate_mode in [
                ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING,
                ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR,
            ]:
                self.__ansible.fail_json(msg=message, configlets_validated=device_data)

        elif len(device_data["warnings"]) > 0:
            message = (
                f"Encountered {len(device_data['warnings'])} warnings during"
                " validation. Refer to 'configlets_validated' for more details."
            )
            if validate_mode == ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING:
                self.__ansible.fail_json(msg=message, configlets_validated=device_data)

        for update in results:
            validation_manager.add_change(change=update)
        ansible_response.add_manager(validation_manager)
        return ansible_response
