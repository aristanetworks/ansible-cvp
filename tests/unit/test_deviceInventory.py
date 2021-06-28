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
import unittest
import pytest
import logging
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement, DeviceInventory   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SERIAL, FIELD_SYSMAC   # noqa # pylint: disable=unused-import
from lib.json_data import schema_valid, search_methods



class TestDeviceInventory(unittest.TestCase):
    def setUp(self):
        self.device_inventory = schema_valid['device']

    def test_create_object(self):
        for index, inventory_data in enumerate(self.device_inventory):
            logging.debug('Run over inventory index {}'.format(index))
            inventory = DeviceInventory(data=inventory_data)
            fqdn_list = set([data[FIELD_FQDN] for data in inventory_data])
            for dev in inventory.devices:
                logging.debug('  Found device: {}'.format(dev.fqdn))
                self.assertIn(dev.fqdn, fqdn_list)
        logging.info('All devices are correctly extracted from inventory')

    def test_display_info(self):
        for index, inventory_data in enumerate(self.device_inventory):
            logging.debug('Run over inventory index {}'.format(index))
            inventory = DeviceInventory(data=inventory_data)
            for dev in inventory.devices:
                logging.info('device info: {}'.format(dev.info))
        logging.info('All devices are correctly extracted from inventory')

    def test_devices_iteration(self):
        for index, inventory_data in enumerate(self.device_inventory):
            logging.debug('Run over inventory index {}'.format(index))
            # logging.warning('Size of JSON obj: {}'.format())
            inventory = DeviceInventory(data=inventory_data)
            self.assertEqual(len(inventory_data), len(inventory.devices))
            logging.debug('  Inventory has {} device(s)'.format(len(inventory.devices)))

    def test_get_by_default(self):
        for index, inventory_data in enumerate(self.device_inventory):
            logging.debug('Run over inventory index {}'.format(index))
            for dev_data in inventory_data:
                inventory = DeviceInventory(data=inventory_data)
                dev_inventory = inventory.get_device(device_string=dev_data[FIELD_FQDN])
                self.assertIsNotNone(dev_inventory)
                self.assertEqual(dev_data[FIELD_FQDN], dev_inventory.fqdn)

    def test_get_specific(self):
        for search_method in search_methods:
            logging.info('Test search using {} method'.format(search_method) )
            for index, inventory_data in enumerate(self.device_inventory):
                logging.debug('  Run over inventory index {}'.format(index))
                for dev_data in inventory_data:
                    if search_method in dev_data.keys():
                        inventory = DeviceInventory(data=inventory_data)
                        dev_inventory = inventory.get_device(
                            device_string=dev_data[search_method],
                            search_method=search_method)
                        self.assertIsNotNone(dev_inventory)
                        self.assertEqual(dev_data[search_method], dev_inventory.info[search_method])

    def test_get_by_unsupported(self):
        for index, inventory_data in enumerate(self.device_inventory):
            logging.debug('Run over inventory index {}'.format(index))
            for dev_data in inventory_data:
                inventory = DeviceInventory(data=inventory_data)
                dev_inventory = inventory.get_device(
                    device_string=dev_data[FIELD_FQDN],
                    search_method='test')
                self.assertIsNotNone(dev_inventory)
                self.assertEqual(dev_data[FIELD_FQDN], dev_inventory.fqdn)

    def test_get_by_nonexisting(self):
        for index, inventory_data in enumerate(self.device_inventory):
            logging.debug('Run over inventory index {}'.format(index))
            for index in enumerate(inventory_data):
                inventory = DeviceInventory(data=inventory_data)
                dev_inventory = inventory.get_device(device_string='ansibel')
                self.assertIsNone(dev_inventory)
        logging.info('All nonexisting devices returned NONE')
