#!/usr/bin/python
# coding: utf-8 -*-

from unittest.mock import MagicMock, create_autospec
from cvprac.cvp_client import CvpClient, CvpApi
from ansible.module_utils.basic import AnsibleModule
from tests.lib.json_data import CVP_DATA_CONTAINERS

def get_container_by_name(arg):
    return CVP_DATA_CONTAINERS[arg]

CVP_MOCK_ATTRS = {
    'get_container_by_name.side_effect': get_container_by_name
}

class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass

def get_cvp_client() -> MagicMock:
    """
    Return a mock cpvrac.cvp_client.CvpClient instance.

    Returns
    -------
    MagicMock
        The mock cpvrac.cvp_client.CvpClient instance.
    """
    mock_client = create_autospec(CvpClient)
    mock_client.api = create_autospec(CvpApi)
    mock_client.api.configure_mock(**CVP_MOCK_ATTRS)
    return mock_client

def get_ansible_module():
    """
    Return a mock ansible.module_utils.basic.AnsibleModule instance.
    The test case could eventually verify that the module exited correcty by calling the `module.exit_json.assert_called()` method.

    Returns
    -------
    MagicMock
        The mock cpvrac.cvp_client.CvpClient instance.
    """
    mock_module = create_autospec(AnsibleModule)
    mock_module.fail_json.side_effect = AnsibleFailJson
    mock_module.check_mode = False
    return mock_module
