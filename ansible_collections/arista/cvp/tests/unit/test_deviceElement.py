#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import sys
import logging
import pytest
sys.path.append("../../../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement, FIELD_CONFIGLETS
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SERIAL, FIELD_SYSMAC


CVP_DEVICES = [
    {
        "fqdn": "DC1-SPINE1.eve.emea.lab",
        "serialNumber": "ddddddd",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ],
        "imageBundle": []
    }
]

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

def get_device():
    return CVP_DEVICES

# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #


@pytest.fixture(scope="class")
# @pytest.mark.parametrize('CVP_CONTAINER', get_user_container_definition())
def DeviceElement_Manager(request):
    logging.info("Execute fixture to create class elements")


# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #


@pytest.mark.usefixtures("DeviceElement_Manager")
@pytest.mark.generic
class TestDeviceElement():

    @pytest.mark.parametrize('DEVICE', get_device())
    def test_get_fqdn(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.fqdn == DEVICE[FIELD_FQDN]
        logging.info('Data from device: {}'.format(device.info))

    @pytest.mark.parametrize('DEVICE', get_device())
    def test_get_system_mac(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.system_mac == DEVICE[FIELD_SYSMAC]
        logging.info('Data from device: {}'.format(device.info))

    @pytest.mark.parametrize('DEVICE', get_device())
    def test_get_serial_number(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.serial_number == DEVICE[FIELD_SERIAL]
        logging.info('Data from device: {}'.format(device.info))

    @pytest.mark.parametrize('DEVICE', get_device())
    def test_get_configlets(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.configlets == DEVICE[FIELD_CONFIGLETS]
        logging.info('Data from device: {}'.format(device.info))

    @pytest.mark.parametrize('DEVICE', get_device())
    def test_set_systemMac(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        system_mac = 'newMacAddress'
        device.system_mac = system_mac
        assert device.system_mac == system_mac
        logging.info('Data from device: {}'.format(device.info))
