#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from __future__ import (absolute_import, division, print_function)
import logging
import pytest
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement
from ansible_collections.arista.cvp.plugins.module_utils.fields import ApiFields
from tests.lib.parametrize import generate_flat_data
from tests.lib.utils import generate_container_ids

@pytest.mark.generic
@pytest.mark.parametrize("DEVICE", generate_flat_data(type="device"))
class TestDeviceElement():

    def test_get_fqdn(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.fqdn == DEVICE[ApiFields.device.FQDN]
        logging.info("Data from device: {}".format(device.info))

    def test_get_system_mac(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if ApiFields.device.SYSMAC in DEVICE:
            assert device.system_mac == DEVICE[ApiFields.device.SYSMAC]
            logging.info("Data from device: {}".format(device.info))
        else:
            pytest.skip(
                "Skipped as device has no {} configured".format(ApiFields.device.SYSMAC))

    def test_get_serial_number(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if ApiFields.device.SERIAL in DEVICE:
            assert device.serial_number == DEVICE[ApiFields.device.SERIAL]
            logging.info("Data from device: {}".format(device.info))
        else:
            logging.warning(
                "Device {} has no serial number set".format(device.fqdn))

    def test_get_configlets(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if ApiFields.generic.CONFIGLETS in DEVICE:
            assert device.configlets == DEVICE[ApiFields.generic.CONFIGLETS]
            logging.info("Data from device: {}".format(device.info))
        else:
            logging.warning(
                "Device {} has no serial number set".format(device.fqdn))

    def test_set_systemMac(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        system_mac = "newMacAddress"
        device.system_mac = system_mac
        assert device.system_mac == system_mac
        logging.info("Data from device: {}".format(device.info))

    def test_get_container(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.container == DEVICE[ApiFields.generic.PARENT_CONTAINER_NAME]
        logging.info(
            "Device {} got correct container information from DeviceElement".format(device.fqdn))

    @pytest.mark.parametrize("CONTAINER_ID", generate_container_ids())
    def test_container_id(self, DEVICE, CONTAINER_ID):
        device = DeviceElement(data=DEVICE)
        device.parent_container_id = CONTAINER_ID
        assert device.parent_container_id == CONTAINER_ID
        logging.info("Container ID is set correctly")

    def test_get_configlets(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if ApiFields.generic.CONFIGLETS in DEVICE:
            assert device.configlets == DEVICE[ApiFields.generic.CONFIGLETS]
            logging.info(
                "DeviceElement returns correct configlets for {}".format(device.fqdn))
        else:
            assert device.configlets == []
            logging.info(
                "DeviceElement returns correct empty list of configlets for {}".format(device.fqdn))

    def test_display_info(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.info[ApiFields.device.FQDN] == DEVICE[ApiFields.device.FQDN]
        if ApiFields.device.SERIAL in DEVICE:
            assert device.info[ApiFields.device.SERIAL] == DEVICE[ApiFields.device.SERIAL]
        if ApiFields.device.SYSMAC in DEVICE:
            assert device.info[ApiFields.device.SYSMAC] == DEVICE[ApiFields.device.SYSMAC]
        if ApiFields.device.CONTAINER_NAME in DEVICE:
            assert device.info[ApiFields.generic.PARENT_CONTAINER_NAME] == DEVICE[ApiFields.generic.PARENT_CONTAINER_NAME]
        logging.info("Device information: {}".format(device.info))
