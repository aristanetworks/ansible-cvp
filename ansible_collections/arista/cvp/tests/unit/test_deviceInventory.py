#!/usr/bin/python
# coding: utf-8 -*-


from __future__ import (absolute_import, division, print_function)
import sys
sys.path.append("../../../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement, DeviceInventory   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SERIAL, FIELD_SYSMAC   # noqa # pylint: disable=unused-import


CVP_DEVICES = [
    {
        "fqdn": "DC1-SPINE1.eve.emea.lab",
        "serialNumber": "ddddddd",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE1",
                "01TRAINING-01"
        ],
        "imageBundle": []
    },
    {
        "fqdn": "DC1-SPINE2.eve.emea.lab",
        "systemMacAddress": "yyyyyyy",
        "parentContainerName": "DC1_SPINES",
        "configlets": [
                "AVD_DC1-SPINE2",
                "01TRAINING-01"
        ]
    }
]


def test_create_object():
    inventory = DeviceInventory(data=CVP_DEVICES)
    fqdn_list = set([data[FIELD_FQDN] for data in CVP_DEVICES])
    for dev in inventory.devices:
        assert dev.fqdn in fqdn_list

def test_display_info():
    inventory = DeviceInventory(data=CVP_DEVICES)
    for device in inventory.devices:
        print('device info: {}'.format(device.info))

def test_device_schema():
    inventory = DeviceInventory(data=CVP_DEVICES)
    assert inventory.is_valid

def test_devices_iteration():
    inventory = DeviceInventory(data=CVP_DEVICES)
    assert len(CVP_DEVICES) == len(inventory.devices)

def test_get_by_default():
    inventory = DeviceInventory(data=CVP_DEVICES)
    for dev_data in CVP_DEVICES:
        dev_inventory = inventory.get_device(device_string=dev_data[FIELD_FQDN])
        assert dev_inventory is not None
        assert dev_data[FIELD_FQDN] == dev_inventory.fqdn

def test_get_by_fqdn():
    inventory = DeviceInventory(data=CVP_DEVICES)
    for dev_data in CVP_DEVICES:
        dev_inventory = inventory.get_device(device_string=dev_data[FIELD_FQDN], search_method=FIELD_FQDN)
        assert dev_data[FIELD_FQDN] == dev_inventory.fqdn

def test_get_by_fqdn_default():
    inventory = DeviceInventory(data=CVP_DEVICES, search_method=FIELD_FQDN)
    for dev_data in CVP_DEVICES:
        dev_inventory = inventory.get_device(device_string=dev_data[FIELD_FQDN])
        assert dev_data[FIELD_FQDN] == dev_inventory.fqdn

def test_get_by_system_mac():
    inventory = DeviceInventory(data=CVP_DEVICES)
    for dev_data in CVP_DEVICES:
        if FIELD_SYSMAC in dev_data:
            dev_inventory = inventory.get_device(
                device_string=dev_data[FIELD_SYSMAC], search_method=FIELD_SYSMAC)
            assert dev_data[FIELD_SYSMAC] == dev_inventory.system_mac
        else:
            assert True

def test_get_by_system_mac_default():
    inventory = DeviceInventory(data=CVP_DEVICES, search_method=FIELD_SYSMAC)
    for dev_data in CVP_DEVICES:
        if FIELD_SYSMAC in dev_data:
            dev_inventory = inventory.get_device(
                device_string=dev_data[FIELD_SYSMAC])
            assert dev_data[FIELD_SYSMAC] == dev_inventory.system_mac
        else:
            assert True

def test_get_by_unsupported_option():
    inventory = DeviceInventory(data=CVP_DEVICES)
    for dev_data in CVP_DEVICES:
        dev_inventory = inventory.get_device(
            device_string=dev_data[FIELD_FQDN],
            search_method='test')
        assert dev_data[FIELD_FQDN] == dev_inventory.fqdn
