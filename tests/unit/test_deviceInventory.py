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
import pytest
import logging
sys.path.append(".")
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement, DeviceInventory   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SERIAL, FIELD_SYSMAC   # noqa # pylint: disable=unused-import


CVP_INVENTORY_VALID = [
    [{
        "fqdn": "DC1-SPINE1.eve.emea.lab",
        "serialNumber": "ddddddd",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ],
        "imageBundle": []
    }],
    [{
        "fqdn": "DC1-SPINE1",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ]
    }],
    [{
        "fqdn": "DC1-SPINE1",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES"
    }],
    [{
        "fqdn": "DC1-SPINE1",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "imageBundle": []
    }]
]

CVP_INVENTORY_INVALID = [
    [{
        "serialNumber": "ddddddd",
        "systemMacAddress": "ccccccc",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ],
        "imageBundle": []
    }]
]

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #


def get_valid_inventory():
    return CVP_INVENTORY_VALID

def get_invalid_inventory():
    return CVP_INVENTORY_INVALID

# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #

@pytest.mark.generic
class TestDeviceInventory():

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_create_object(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        fqdn_list = set([data[FIELD_FQDN] for data in DEVICE_INVENTORY])
        for dev in inventory.devices:
            assert dev.fqdn in fqdn_list

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_display_info(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for device in inventory.devices:
            logging.info('device info: {}'.format(device.info))

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_device_schema_is_valid(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        assert inventory.is_valid
        logging.info('Schema for {} is valid'.format(DEVICE_INVENTORY))

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_invalid_inventory())
    def test_device_schema_is_not_valid(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        assert inventory.is_valid is False
        logging.info('Schema for {} is NOT valid'.format(DEVICE_INVENTORY))

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_devices_iteration(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        assert len(DEVICE_INVENTORY) == len(inventory.devices)

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_get_by_default(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(device_string=dev_data[FIELD_FQDN])
            assert dev_inventory is not None
            assert dev_data[FIELD_FQDN] == dev_inventory.fqdn

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_get_by_fqdn(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(device_string=dev_data[FIELD_FQDN], search_method=FIELD_FQDN)
            assert dev_data[FIELD_FQDN] == dev_inventory.fqdn

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_get_by_fqdn_default(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY, search_method=FIELD_FQDN)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(device_string=dev_data[FIELD_FQDN])
            assert dev_data[FIELD_FQDN] == dev_inventory.fqdn

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_get_by_system_mac(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            if FIELD_SYSMAC in dev_data:
                dev_inventory = inventory.get_device(
                    device_string=dev_data[FIELD_SYSMAC], search_method=FIELD_SYSMAC)
                assert dev_data[FIELD_SYSMAC] == dev_inventory.system_mac
            else:
                pytest.skip('Skipped because {} is not in {}'.format(
                    FIELD_SYSMAC, dev_data))

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_get_by_system_mac_default(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY, search_method=FIELD_SYSMAC)
        for dev_data in DEVICE_INVENTORY:
            if FIELD_SYSMAC in dev_data:
                dev_inventory = inventory.get_device(
                    device_string=dev_data[FIELD_SYSMAC])
                assert dev_data[FIELD_SYSMAC] == dev_inventory.system_mac
            else:
                pytest.skip('Skipped because {} is not in {}'.format(FIELD_SYSMAC, dev_data))

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_get_unknown_device(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        dev_inventory = inventory.get_device(device_string='dev_data[FIELD_SYSMAC]')
        assert dev_inventory is None
        logging.info('Unknown device returns None')

    @pytest.mark.parametrize('DEVICE_INVENTORY', get_valid_inventory())
    def test_get_by_unsupported_option(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(
                device_string=dev_data[FIELD_FQDN],
                search_method='test')
            assert dev_data[FIELD_FQDN] == dev_inventory.fqdn
