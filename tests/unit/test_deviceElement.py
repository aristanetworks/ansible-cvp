#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from __future__ import (absolute_import, division, print_function)
import sys
import logging
import pytest
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement, FIELD_CONFIGLETS, FIELD_CONTAINER_NAME, FIELD_PARENT_NAME
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SERIAL, FIELD_SYSMAC


CVP_DEVICES = [
    {
        "fqdn": "DC1-SPINE1.eve.emea.lab",
        "serialNumber": "ddddddd",
        "systemMacAddress": "0c:1d:c0:a3:86:f3",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ],
        "imageBundle": []
    },
    {
        "fqdn": "DC1-SPINE1",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ]
    },
    {
        "fqdn": "DC1-SPINE1",
        "parentContainerName": "DC1_SPINES"
    },
    {
        "fqdn": "DC1-SPINE1",
        "parentContainerName": "DC1_SPINES",
        "imageBundle": []
    }
]

CONTAINER_IDS = ['Tenant', 'container-1111-2222-3333-4444', 'container_222_ccc_rrr']

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

def get_device():
    return CVP_DEVICES


def get_container_ids():
    return CONTAINER_IDS

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
@pytest.mark.parametrize('DEVICE', get_device())
class TestDeviceElement():

    def test_get_fqdn(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.fqdn == DEVICE[FIELD_FQDN]
        logging.info('Data from device: {}'.format(device.info))

    def test_get_system_mac(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if FIELD_SYSMAC in DEVICE:
            assert device.system_mac == DEVICE[FIELD_SYSMAC]
            logging.info('Data from device: {}'.format(device.info))
        else:
            pytest.skip('Skipped as device has no {} configured'.format(FIELD_SYSMAC))

    def test_get_serial_number(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if FIELD_SERIAL in DEVICE:
            assert device.serial_number == DEVICE[FIELD_SERIAL]
            logging.info('Data from device: {}'.format(device.info))
        else:
            logging.warning('Device {} has no serial number set'.format(device.fqdn))

    def test_get_configlets(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if FIELD_CONFIGLETS in DEVICE:
            assert device.configlets == DEVICE[FIELD_CONFIGLETS]
            logging.info('Data from device: {}'.format(device.info))
        else:
            logging.warning(
                'Device {} has no serial number set'.format(device.fqdn))

    def test_set_systemMac(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        system_mac = 'newMacAddress'
        device.system_mac = system_mac
        assert device.system_mac == system_mac
        logging.info('Data from device: {}'.format(device.info))

    def test_get_container(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.container == DEVICE[FIELD_PARENT_NAME]
        logging.info('Device {} got correct container information from DeviceElement'.format(device.fqdn))

    @pytest.mark.parametrize('CONTAINER_ID', get_container_ids())
    def test_container_id(self, DEVICE, CONTAINER_ID):
        device = DeviceElement(data=DEVICE)
        device.parent_container_id = CONTAINER_ID
        assert device.parent_container_id == CONTAINER_ID
        logging.info('Container ID is set correctly')

    def test_get_configlets(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        if FIELD_CONFIGLETS in DEVICE:
            assert device.configlets == DEVICE[FIELD_CONFIGLETS]
            logging.info('DeviceElement returns correct configlets for {}'.format(device.fqdn))
        else:
            assert device.configlets == []
            logging.info(
                'DeviceElement returns correct empty list of configlets for {}'.format(device.fqdn))

    def test_display_info(self, DEVICE):
        device = DeviceElement(data=DEVICE)
        assert device.info[FIELD_FQDN] == DEVICE[FIELD_FQDN]
        if FIELD_SERIAL in DEVICE:
            assert device.info[FIELD_SERIAL] == DEVICE[FIELD_SERIAL]
        if FIELD_SYSMAC in DEVICE:
            assert device.info[FIELD_SYSMAC] == DEVICE[FIELD_SYSMAC]
        if FIELD_CONTAINER_NAME in DEVICE:
            assert device.info[FIELD_PARENT_NAME] == DEVICE[FIELD_PARENT_NAME]
        logging.info('Device information: {}'.format(device.info))
