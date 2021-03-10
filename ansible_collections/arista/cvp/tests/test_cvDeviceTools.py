#!/usr/bin/python
# coding: utf-8 -*-


from __future__ import (absolute_import, division, print_function)
import sys
sys.path.append("../../../../")
from cvprac.cvp_client import CvpClient
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SYSMAC, FIELD_ID
# from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult

# Hack to silent SSL warning
import ssl
import requests.packages.urllib3
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

CVP_DEVICES_INITIAL = [
    {
        "fqdn": "CV-ANSIBLE-EOS01",
        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE",
        "configlets": [
                "01TRAINING-01",
                "CV-EOS-ANSIBLE01"
        ],
        "imageBundle": []
    }
]

CVP_DEVICES_MOVE = [
    {
        "fqdn": "CV-ANSIBLE-EOS01",
        "serialNumber": "79AEA53101E7340AEC9AA4819D5E1F5B",
        "systemMacAddress": "50:8d:00:e3:78:aa",
        "parentContainerName": "ANSIBLE2",
        "configlets": [
                "01TRAINING-01",
                "CV-EOS-ANSIBLE01"
        ],
        "imageBundle": []
    }
]

CVP_DEVICES_DEPLOY = [
    {
        "fqdn": "CV-ANSIBLE-EOS02",
        "serialNumber": "",
        "systemMacAddress": "50:8d:00:91:64:59",
        "parentContainerName": "ANSIBLE",
        "configlets": [
                "01TRAINING-01",
                "CV-EOS-ANSIBLE02"
        ]
    }
]

# Get Data:
# curl - X GET - -header 'Accept: application/json' '\
# https://x.x.x.x/cvpservice/provisioning/searchTopology.do?queryParam=CV-ANSIBLE-EOS01&startIndex=0&endIndex=0'
DEVICE_NAME = 'DC1-SPINE1.eve.emea.lab'
DEVICE_CONTAINER = 'DC1_SPINES'
DEVICE_ID = '0c:1d:c0:a3:86:f3'
CONTAINER_ID = 'container_fd431ab2-25bb-4281-8bcc-c7249f55241b'

CHECK_MODE = True

def cvp_login():
    requests.packages.urllib3.disable_warnings()
    cvp_client = CvpClient()
    cvp_client.connect(
        nodes=['10.83.28.164'],
        username='ansible',
        password='interdata'
    )
    return cvp_client

CVP_CLIENT = cvp_login()

def test_create_object():
    # inventory = DeviceInventory(data=CVP_DEVICES)
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)  # noqa # pylint: disable=unused-variable

def test_search_by_getter_setter():
    # inventory = DeviceInventory(data=CVP_DEVICES)
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    assert cv_devices.search_by == FIELD_FQDN
    cv_devices.search_by = FIELD_SYSMAC
    assert cv_devices.search_by == FIELD_SYSMAC

def test_is_device_exists_by_fqdn():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    assert cv_devices.is_device_exist(device_lookup=DEVICE_NAME) is True

def test_device_is_not_present():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    assert cv_devices.is_device_exist(device_lookup='test') is False

def test_device_in_container():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    assert cv_devices.is_in_container(
        device_lookup=DEVICE_NAME, container_name=DEVICE_CONTAINER)

def test_device_not_in_container():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    assert cv_devices.is_in_container(
        device_lookup=DEVICE_NAME, container_name='DC12_SPINES') is False

def test_device_facts_default():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    device_facts = cv_devices.get_device_facts(device_lookup=DEVICE_NAME)
    assert device_facts is not None
    assert FIELD_FQDN in device_facts
    assert device_facts[FIELD_FQDN] == DEVICE_NAME

def test_get_device_id():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    device_facts = cv_devices.get_device_id(device_lookup=DEVICE_NAME)
    assert device_facts is not None
    assert device_facts == DEVICE_ID

def test_get_configlets():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    configlets = cv_devices.get_device_configlets(device_lookup=DEVICE_NAME)
    assert configlets is not None

def test_container_id():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    user_inventory = DeviceInventory(data=CVP_DEVICES_INITIAL)
    result = cv_devices.get_container_info(container_name=user_inventory.devices[0].container)
    assert result[FIELD_ID] == CONTAINER_ID

def test_device_move():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    user_inventory = DeviceInventory(data=CVP_DEVICES_MOVE)
    resp = cv_devices.move_device(user_inventory=user_inventory)
    assert resp[0].results['success']
    assert resp[0].results['changed']
    assert len(resp[0].results['taskIds']) > 0
    assert int(resp[0].count) > 0

def test_configlet_apply():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    user_inventory = DeviceInventory(data=CVP_DEVICES_INITIAL)
    resp = cv_devices.apply_configlets(user_inventory=user_inventory)
    assert resp[0].results['success']
    assert resp[0].results['changed']
    assert int(resp[0].count) > 0

def test_device_deploy():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    user_inventory = DeviceInventory(data=CVP_DEVICES_DEPLOY)
    resp = cv_devices.deploy_device(user_inventory=user_inventory)
    assert resp[0].results['success']
    assert resp[0].results['changed']
    print('DEPLOYED configlet response is: {}'.format(resp[0].results))


def test_device_manager():
    requests.packages.urllib3.disable_warnings()
    cv_devices = CvDeviceTools(cv_connection=CVP_CLIENT, check_mode=CHECK_MODE)
    user_inventory = DeviceInventory(data=CVP_DEVICES_INITIAL)
    resp = cv_devices.manager(user_inventory=user_inventory)
    # assert resp.results['success']
    # assert resp.results['changed']
    # assert 'device_deployed_count' in resp.results and int(
    #     resp.results['device_deployed_count']) > 0
    print('MANAGER response is: {}'.format(resp))
