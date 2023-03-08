#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from unittest.mock import call
from copy import deepcopy
import pytest
from tests.data.device_tools_unit import device_data, current_container_info, cv_data
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
# from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import

# list of paths to patch
MOCK_LIST = [
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule',
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools._CvDeviceTools__get_device',
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools.get_container_current',
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools.get_container_info']

@pytest.fixture
def setup(apply_mock, mock_cvpClient):
    """
    setup - setup method to apply mocks and patches
    """
    mock_ansible_module, mock__get_device, mock_get_container_current, mock_get_container_info = apply_mock(MOCK_LIST)

    mock_ansible_module.fail_json.side_effect = mock_cvpClient.api.fail_json

    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module, 'serialNumber')

    return mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, mock_get_container_info


@pytest.mark.state_present
class TestMoveDevice():
    """
    Contains unit tests for move_device()
    """
    @pytest.mark.parametrize(
        "expected, test_flag",
        [
            (True, None), # success
            (False, 0),   # failure for same device and current container name
            (False, 1),   # failure for systemMacAddress = None
            (False, "InvalidContainer"), # failure when move_device_to_container method returns fail.
            (True, "check_mode"), # success if check_mode == True
        ],
    )

    def test_move_device(self, setup, expected, test_flag):
        """
        Tests for:
            device and current container names are different,
            device and current container names are same,
            systemMacAddress = None,
            move_device_to_container method returns fail,
            if check_mode == True.
        :param expected: output expected from move_device,
        :param setup: fixture,
        :param test_falg: conditions
        """

        if expected:
            device_data[0]["parentContainerName"] = "TP_LEAF2"
        else:
            if test_flag:
                device_data[0]["systemMacAddress"] = None

        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current, mock_get_container_info = setup
        mock__get_device.return_value = cv_data
        mock_get_container_current.return_value = current_container_info

        if test_flag == "InvalidContainer":
            mock_get_container_info.return_value = "InvalidContainer"

        if test_flag == "check_mode":
            cv_tools.check_mode = "True"

        result = cv_tools.move_device(user_inventory=user_topology)
        assert result[0].success == expected
        assert result[0].changed == expected

        device_data[0]["systemMacAddress"] = '50:08:00:b1:5b:0b'
        device_data[0]["parentContainerName"] = "TP_LEAF1"
    

    def test_move_device_cvp_api_error(self, setup):
        """
        Test for CvpApiError.
        :param setup: fixture
        """
        
        device_data[0]["parentContainerName"] = "TP_LEAF2"
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, mock_get_container_info = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data

        mock_get_container_info.return_value = "CvpApiError"
        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.move_device(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg='Error to move device tp-avd-leaf2 to container TP_LEAF2')]
        assert mock_ansible_module.mock_calls == expected_call
        device_data[0]["parentContainerName"] = "TP_LEAF1"

    def test_move_device_target_container_error(self, setup):
        """
        Test for target container is None.
        :param setup: fixture
        """
        
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, mock_get_container_info = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data

        mock_get_container_info.return_value = None
        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.move_device(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg=f"The target container 'TP_LEAF1' for the device 'tp-avd-leaf2' does not exist on CVP.")]
        assert mock_ansible_module.mock_calls == expected_call
        