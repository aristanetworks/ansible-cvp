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
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from tests.lib.parametrize import generate_inventory_data


@pytest.mark.generic
class TestDeviceInventory():

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_create_object(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        fqdn_list = {data[Api.device.FQDN] for data in DEVICE_INVENTORY}
        for dev in inventory.devices:
            assert dev.fqdn in fqdn_list

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_display_info(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for device in inventory.devices:
            logging.info("device info: {}".format(device.info))

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_device_schema_is_valid(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        assert inventory.is_valid
        logging.info("Schema for {} is valid".format(DEVICE_INVENTORY))

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device", mode="invalid"))
    def test_device_schema_is_not_valid(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        assert inventory.is_valid is False
        logging.info("Schema for {} is NOT valid".format(DEVICE_INVENTORY))

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_devices_iteration(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        assert len(DEVICE_INVENTORY) == len(inventory.devices)

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_get_by_default(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(
                device_string=dev_data[Api.device.FQDN])
            assert dev_inventory is not None
            assert dev_data[Api.device.FQDN] == dev_inventory.fqdn

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_get_by_fqdn(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(
                device_string=dev_data[Api.device.FQDN], search_method=Api.device.FQDN)
            assert dev_data[Api.device.FQDN] == dev_inventory.fqdn

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_get_by_fqdn_default(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(
            data=DEVICE_INVENTORY, search_method=Api.device.FQDN)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(
                device_string=dev_data[Api.device.FQDN])
            assert dev_data[Api.device.FQDN] == dev_inventory.fqdn

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_get_by_system_mac(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            if Api.device.SYSMAC in dev_data:
                dev_inventory = inventory.get_device(
                    device_string=dev_data[Api.device.SYSMAC], search_method=Api.device.SYSMAC)
                assert dev_data[Api.device.SYSMAC] == dev_inventory.system_mac
            else:
                pytest.skip("Skipped because {} is not in {}".format(
                    Api.device.SYSMAC, dev_data))

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_get_by_system_mac_default(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(
            data=DEVICE_INVENTORY, search_method=Api.device.SYSMAC)
        for dev_data in DEVICE_INVENTORY:
            if Api.device.SYSMAC in dev_data:
                dev_inventory = inventory.get_device(
                    device_string=dev_data[Api.device.SYSMAC])
                assert dev_data[Api.device.SYSMAC] == dev_inventory.system_mac
            else:
                pytest.skip("Skipped because {} is not in {}".format(
                    Api.device.SYSMAC, dev_data))

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_get_unknown_device(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        dev_inventory = inventory.get_device(
            device_string="dev_data[Api.device.SYSMAC]")
        assert dev_inventory is None
        logging.info("Unknown device returns None")

    @pytest.mark.parametrize("DEVICE_INVENTORY", generate_inventory_data(type="device"))
    def test_get_by_unsupported_option(self, DEVICE_INVENTORY):
        inventory = DeviceInventory(data=DEVICE_INVENTORY)
        for dev_data in DEVICE_INVENTORY:
            dev_inventory = inventory.get_device(
                device_string=dev_data[Api.device.FQDN],
                search_method="test")
            assert dev_data[Api.device.FQDN] == dev_inventory.fqdn
