#!/usr/bin/python
# coding: utf-8 -*-


from __future__ import (absolute_import, division, print_function)
import sys
sys.path.append("../../../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement, FIELD_CONFIGLETS
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SERIAL, FIELD_SYSMAC


CVP_DEVICE = {
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


def test_get_fqdn():
    device = DeviceElement(data=CVP_DEVICE)
    assert device.fqdn == CVP_DEVICE[FIELD_FQDN]


def test_get_system_mac():
    device = DeviceElement(data=CVP_DEVICE)
    assert device.system_mac == CVP_DEVICE[FIELD_SYSMAC]


def test_get_serial_number():
    device = DeviceElement(data=CVP_DEVICE)
    assert device.serial_number == CVP_DEVICE[FIELD_SERIAL]


def test_get_configlets():
    device = DeviceElement(data=CVP_DEVICE)
    assert device.configlets == CVP_DEVICE[FIELD_CONFIGLETS]


def test_set_systemMac():
    device = DeviceElement(data=CVP_DEVICE)
    system_mac = 'newMacAddress'
    device.system_mac = system_mac
    assert device.system_mac == system_mac
