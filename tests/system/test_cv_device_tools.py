#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

"""
test_cv_device_tools.py - Testcases related to device tools.
"""


from __future__ import (absolute_import, division, print_function)
import sys
import ssl
import logging
import pytest
import requests.packages.urllib3
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SYSMAC, FIELD_ID, FIELD_PARENT_NAME, FIELD_PARENT_ID, FIELD_HOSTNAME
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools, FIELD_CONTAINER_NAME
from lib.helpers import time_log
from lib.utils import cvp_login, get_devices, get_devices_unknown, get_devices_to_move
from constants_data import ANSIBLE_CV_SEARCH_MODE


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
class TestCvDeviceTools():

    def test_cvp_connection(self):
        """Test cvp connection
        return: None
        """
        assert True
        logging.info("Connected to CVP")

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_search_by_getter_setter(self, CV_DEVICE):
        self.inventory.search_by = FIELD_SYSMAC
        assert self.inventory.search_by == FIELD_SYSMAC
        logging.info(
            "Setter & Getter for search_by using {} is valid".format(FIELD_SYSMAC))
        self.inventory.search_by = FIELD_FQDN
        assert self.inventory.search_by == FIELD_FQDN
        self.inventory.search_by = FIELD_HOSTNAME
        assert self.inventory.search_by == FIELD_HOSTNAME
        self.inventory.search_by = ANSIBLE_CV_SEARCH_MODE
        logging.info(
            "Setter & Getter for search_by using {} is valid".format(FIELD_FQDN))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_is_device_exists_by_fqdn(self, CV_DEVICE):
        logging.info("Search device {} in Cloudvision".format(
            CV_DEVICE[FIELD_FQDN]))
        logging.info("Start CV query at {}".format(time_log()))
        requests.packages.urllib3.disable_warnings()
        assert self.inventory.is_device_exist(
            device_lookup=CV_DEVICE[FIELD_FQDN], search_mode=FIELD_FQDN) is True
        logging.info("End of CV query at {}".format(time_log()))
        logging.info("Device {} is present in Cloudvision".format(
            CV_DEVICE[FIELD_FQDN]))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE_UNKNOWN", get_devices_unknown())
    def test_device_is_not_present(self, CV_DEVICE_UNKNOWN):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        assert self.inventory.is_device_exist(
            device_lookup=CV_DEVICE_UNKNOWN[FIELD_FQDN]) is False
        logging.info("End of CV query at {}".format(time_log()))
        logging.info("Device {} is not present on Cloudvision".format(
            CV_DEVICE_UNKNOWN[FIELD_FQDN]))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_device_in_container(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        assert self.inventory.is_in_container(
            device_lookup=CV_DEVICE[FIELD_FQDN], container_name=CV_DEVICE[FIELD_PARENT_NAME])
        logging.info("End of CV query at {}".format(time_log()))
        logging.info("Device {} is correctly configured under {}".format(
            CV_DEVICE[FIELD_FQDN], CV_DEVICE[FIELD_PARENT_NAME]))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE_UNKNOWN", get_devices_unknown())
    def test_device_not_in_container(self, CV_DEVICE_UNKNOWN):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        assert self.inventory.is_in_container(
            device_lookup=CV_DEVICE_UNKNOWN[FIELD_FQDN], container_name=CV_DEVICE_UNKNOWN[FIELD_FQDN]) is False
        logging.info("End of CV query at {}".format(time_log()))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_device_facts_default(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        device_facts = self.inventory.get_device_facts(
            device_lookup=CV_DEVICE[FIELD_FQDN])
        logging.info("End of CV query at {}".format(time_log()))
        assert device_facts is not None
        assert FIELD_FQDN in device_facts
        if self.inventory.search_by == "fqdn":
            assert device_facts[FIELD_FQDN] == CV_DEVICE[FIELD_FQDN]
        elif self.inventory.search_by == "hostname":
            assert device_facts[FIELD_FQDN].split(
                ".")[0] == CV_DEVICE[FIELD_FQDN]
        logging.info("Facts for device {} are correct: {}".format(
            CV_DEVICE[FIELD_FQDN], device_facts))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_get_device_id(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        device_facts = self.inventory.get_device_id(
            device_lookup=CV_DEVICE[FIELD_FQDN])
        logging.info("End of CV query at {}".format(time_log()))
        assert device_facts is not None
        assert device_facts == CV_DEVICE[FIELD_SYSMAC]
        logging.info("Device {} has ID: {}".format(
            CV_DEVICE[FIELD_FQDN], device_facts))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_get_configlets(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        logging.info("Start CV query at {}".format(time_log()))
        configlets = self.inventory.get_device_configlets(
            device_lookup=CV_DEVICE[FIELD_FQDN])
        logging.info("End of CV query at {}".format(time_log()))
        assert configlets is not None

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_container_id(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = DeviceInventory(data=[CV_DEVICE])
        logging.info("Start CV query at {}".format(time_log()))
        result = self.inventory.get_container_info(
            container_name=user_inventory.devices[0].container)
        logging.info("End of CV query at {}".format(time_log()))
        assert result[FIELD_ID] == self.cvp.api.get_container_by_name(
            CV_DEVICE[FIELD_PARENT_NAME])[FIELD_ID]

    @pytest.mark.create
    @pytest.mark.parametrize("CV_DEVICE_MOVE", get_devices_to_move())
    def test_device_move(self, CV_DEVICE_MOVE):
        requests.packages.urllib3.disable_warnings()
        logging.critical("{}".format(CV_DEVICE_MOVE))
        user_inventory = DeviceInventory(data=[CV_DEVICE_MOVE])
        logging.info("Start CV query at {}".format(time_log()))
        resp = self.inventory.move_device(user_inventory=user_inventory)
        logging.info("End of CV query at {}".format(time_log()))
        if resp[0].results["success"]:
            assert resp[0].results["success"]
            assert resp[0].results["changed"]
            assert len(resp[0].results["taskIds"]) > 0
            assert int(resp[0].count) > 0
            logging.info("Move device {} to {} with result: {}".format(
                CV_DEVICE_MOVE[FIELD_FQDN], CV_DEVICE_MOVE[FIELD_PARENT_NAME], resp[0].results))
        else:
            pytest.skip("NOT TESTED as device is already in correct container")

    @pytest.mark.create
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_configlet_apply(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = DeviceInventory(data=[CV_DEVICE])
        logging.info("Start CV query at {}".format(time_log()))
        resp = self.inventory.apply_configlets(user_inventory=user_inventory)
        logging.info("End of CV query at {}".format(time_log()))
        assert resp[0].results["success"]
        assert resp[0].results["changed"]
        assert int(resp[0].count) > 0

    @pytest.mark.skip(reason="No test environment to support test")
    @pytest.mark.create
    @pytest.mark.parametrize("CV_DEVICE_MOVE", get_devices_to_move())
    def test_device_deploy(self, CV_DEVICE, CV_DEVICE_MOVE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = DeviceInventory(data=[CV_DEVICE_MOVE])
        resp = self.inventory.deploy_device(user_inventory=user_inventory)
        assert resp[0].results["success"]
        assert resp[0].results["changed"]
        logging.info(
            "DEPLOYED configlet response is: {}".format(resp[0].results))

    @pytest.mark.create
    @pytest.mark.skip(reason="No test environment to support test")
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_device_manager(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = DeviceInventory(data=CV_DEVICE[FIELD_FQDN])
        logging.info("Start CV query at {}".format(time_log()))
        resp = self.inventory.manager(user_inventory=user_inventory)
        logging.info("End of CV query at {}".format(time_log()))
        logging.info("MANAGER response is: {}".format(resp))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_container_name(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = DeviceInventory(data=[CV_DEVICE])
        logging.info("Start CV query at {}".format(time_log()))
        for device in user_inventory.devices:
            result = self.inventory.get_device_container(
                device_lookup=device.fqdn)[FIELD_PARENT_NAME]
            cv_result = self.cvp.api.get_device_by_name(
                device.fqdn, search_by_hostname=ANSIBLE_CV_SEARCH_MODE)[FIELD_CONTAINER_NAME]
            assert result == cv_result
            logging.info(
                "Collection: {} - CV: {}".format(result, cv_result))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_container_id(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = DeviceInventory(data=[CV_DEVICE])
        logging.info("Start CV query at {}".format(time_log()))
        for device in user_inventory.devices:
            result = self.inventory.get_device_container(
                device_lookup=device.fqdn)[FIELD_PARENT_ID]
            cv_result = self.cvp.api.get_device_by_name(
                device.fqdn, search_by_hostname=ANSIBLE_CV_SEARCH_MODE)[FIELD_PARENT_ID]
            assert result == cv_result
            logging.info(
                "Collection: {} - CV: {}".format(result, cv_result))

    @pytest.mark.api
    @pytest.mark.parametrize("CV_DEVICE", get_devices())
    def test_get_device_by_sysmac(self, CV_DEVICE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = DeviceInventory(data=[CV_DEVICE])
        for device in user_inventory.devices:
            if FIELD_SYSMAC in device.info and device.info[FIELD_SYSMAC] is not None:
                self.inventory.search_by = FIELD_SYSMAC
                device_info = self.inventory.get_device_facts(
                    device_lookup=device.system_mac)
                assert device_info[FIELD_FQDN].split(".")[0] == device.fqdn
                assert device_info[FIELD_SYSMAC] == device.system_mac
                self.inventory.search_by = FIELD_FQDN
                logging.info("Data for device {} ({}) are correct".format(
                    device.fqdn, device.system_mac))
            else:
                pytest.skip("Skipped as device {} has no {} field".format(
                    device.fqdn, FIELD_SYSMAC))
