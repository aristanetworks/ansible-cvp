#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801
"""
    test_cv_device_tools_fqdn.py - Testcases related to cv device tools fqdn
"""

from __future__ import (absolute_import, division, print_function)
import ssl
import sys
import pytest
import logging
import requests.packages.urllib3
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SYSMAC, FIELD_PARENT_NAME
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools, FIELD_CONFIGLETS
from lib.helpers import time_log
from constants_data import CHECK_MODE, CONTAINER_DESTINATION
from lib.utils import cvp_login, get_devices



# Hack to silent SSL warning
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()


# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #


@pytest.fixture(scope="class")
def CvDeviceTools_Manager(request):
    logging.info("Execute fixture to create class elements")
    request.cls.cvp = cvp_login()
    request.cls.inventory = CvDeviceTools(cv_connection=request.cls.cvp)

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #


@pytest.mark.usefixtures("CvDeviceTools_Manager")
class TestCvDeviceToolsWithFQDN():

    def test_cvp_connection(self):
        assert True
        logging.info("Connected to CVP")

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_search_by_getter_setter(self, CV_DEVICE):
        self.inventory.search_by = FIELD_FQDN
        assert self.inventory.search_by == FIELD_FQDN
        logging.info(
            "Setter & Getter for search_by using {} is valid".format(FIELD_FQDN))

    ######################################################################
    ### --------------------  Get data functions  -------------------- ###
    ######################################################################

    # Test if device information is correctly retrieved from Cloudvision
    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_get_device_facts(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        logging.debug("CV_DEVICE data is: %s", str(CV_DEVICE))
        if FIELD_FQDN in CV_DEVICE:
            assert self.inventory.get_device_facts(
                device_lookup=CV_DEVICE[FIELD_FQDN])
        else:
            logging.info("Device not based on serial number")
        logging.info("End of CV query at {}".format(time_log()))

    # Test if device ID is correctly retrieved from Cloudvision
    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_get_device_id(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        logging.debug("CV_DEVICE data is: %s", str(CV_DEVICE))
        if FIELD_FQDN in CV_DEVICE:
            assert self.inventory.get_device_id(
                device_lookup=CV_DEVICE[FIELD_FQDN]) == CV_DEVICE[FIELD_SYSMAC]
        else:
            logging.info("Device not based on serial number")
        logging.info("End of CV query at {}".format(time_log()))

    # Test if device configlets are OK
    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_get_device_id(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        logging.debug("CV_DEVICE data is: %s", str(CV_DEVICE))
        if FIELD_FQDN in CV_DEVICE:
            cv_data = self.inventory.get_device_configlets(
                device_lookup=CV_DEVICE[FIELD_FQDN])
            inventory_data = CV_DEVICE[FIELD_CONFIGLETS]
            comparison = list(set(cv_data).intersection(set(inventory_data)))
            assert len(comparison) == 0
        else:
            logging.info("Device not based on serial number")
        logging.info("End of CV query at {}".format(time_log()))

    # Test if device ID is correctly retrieved from Cloudvision
    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_get_device_container(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        logging.debug("CV_DEVICE data is: %s", str(CV_DEVICE))
        if FIELD_FQDN in CV_DEVICE:
            assert self.inventory.get_device_container(device_lookup=CV_DEVICE[FIELD_FQDN])[
                FIELD_PARENT_NAME] == CV_DEVICE[FIELD_PARENT_NAME]
        else:
            logging.info("Device not based on serial number")
        logging.info("End of CV query at {}".format(time_log()))

    ######################################################################
    ### ----------------------  Test functions  ---------------------- ###
    ######################################################################

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_device_is_present_by_fqdn(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        if FIELD_FQDN in CV_DEVICE:
            assert self.inventory.is_device_exist(
                device_lookup=CV_DEVICE[FIELD_FQDN], search_mode=FIELD_FQDN) is True
            logging.info("End of CV query at {}".format(time_log()))
            logging.info("Device {} is not present on Cloudvision".format(
                CV_DEVICE[FIELD_FQDN]))
        else:
            logging.info(
                "Device has no serial set in inventory: {}".format(CV_DEVICE))

    # Test if device is in correct container from Cloudvision
    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_device_in_container(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        logging.debug("CV_DEVICE data is: %s", str(CV_DEVICE))
        if FIELD_FQDN in CV_DEVICE:
            assert self.inventory.is_in_container(
                device_lookup=CV_DEVICE[FIELD_FQDN], container_name=CV_DEVICE[FIELD_PARENT_NAME])
            logging.info("Device {} is correctly configured under {}".format(
                CV_DEVICE[FIELD_FQDN], CV_DEVICE[FIELD_PARENT_NAME]))
        else:
            logging.info("Device not based on serial number")
        logging.info("End of CV query at {}".format(time_log()))

    ######################################################################
    ### -------------------  CV Actions functions  ------------------- ###
    ######################################################################

    @pytest.mark.create
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_configlet_apply(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        CV_DEVICE_LOCAL = CV_DEVICE
        if FIELD_FQDN in CV_DEVICE:
            CV_DEVICE_LOCAL[FIELD_CONFIGLETS].append("01DEMO-01")
            self.inventory.check_mode = CHECK_MODE
            user_inventory = DeviceInventory(data=[CV_DEVICE_LOCAL])
            logging.info("Start CV query at {}".format(time_log()))
            resp = self.inventory.apply_configlets(
                user_inventory=user_inventory)
            logging.info("End of CV query at {}".format(time_log()))
            logging.debug("Data response: {}".format(resp[0].results))
            assert len(resp[0].results) > 0
        else:
            logging.info("Device not based on serial number")
        logging.info("End of CV query at {}".format(time_log()))

    @pytest.mark.create
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_device_move(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        if FIELD_FQDN in CV_DEVICE:
            CV_DEVICE[FIELD_PARENT_NAME] = CONTAINER_DESTINATION
            logging.info("Send update to CV with {}".format(CV_DEVICE))
            self.inventory.check_mode = CHECK_MODE
            user_inventory = DeviceInventory(data=[CV_DEVICE])
            logging.info("Start CV query at {}".format(time_log()))
            resp = self.inventory.move_device(user_inventory=user_inventory)
            logging.info("End of CV query at {}".format(time_log()))
            logging.debug("Data response: {}".format(resp[0].results))
            assert len(resp[0].results) > 0
            assert resp[0].results["success"]
            assert resp[0].results["changed"]
        else:
            logging.info("Device not based on serial number")
        logging.info("End of CV query at {}".format(time_log()))
