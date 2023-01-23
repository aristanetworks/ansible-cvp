#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from unittest.mock import call
import pytest
<<<<<<< HEAD
<<<<<<< HEAD
=======
from tests.lib import mockMagic
from ansible.module_utils.basic import AnsibleModule
>>>>>>> 7ca03e5 (Added docstrings and update code)
=======
>>>>>>> 384f2ed (Restructured pytest)
from tests.data.device_tools_unit import device_data, device_data_invalid
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools


# list of paths to patch
MOCK_LIST = [
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule',
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools._CvDeviceTools__get_device']

@pytest.fixture
def setup(apply_mock, mock_cvpClient):
    """
    setup - setup method to apply mocks and patches
    """
    mock_ansible_module, mock__get_device = apply_mock(MOCK_LIST)
    mock_ansible_module.fail_json.side_effect = mock_cvpClient.api.fail_json
    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)

    return mock_ansible_module, mock__get_device, cv_tools

@pytest.fixture
def setup(apply_mock, mock_cvprac):
    """
    setup - setup method to apply mocks and patches
    """
    mock_ansible_module, mock__get_device = apply_mock(TestState.MOCK_LIST)
    dummy_cvprac, mock_cvpClient = mock_cvprac
    mock_cvpClient.api.device_decommissioning.side_effect = dummy_cvprac.device_decommissioning
    mock_cvpClient.api.device_decommissioning_status_get_one.side_effect = dummy_cvprac.device_decommissioning_status_get_one
    mock_cvpClient.api.reset_device.side_effect = dummy_cvprac.reset_device
    mock_cvpClient.api.delete_device.side_effect = dummy_cvprac.delete_device
    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)

    return mock_ansible_module, mock__get_device, cv_tools


@pytest.mark.state
<<<<<<< HEAD
class TestDecommissionDevice():
    """
    Contains unit tests for decommission_device()
    """
=======
class TestState():
    """
    Contains unit tests for state: absent, factory_reset and provisioning_reset
    """
<<<<<<< HEAD

    def apply_mocks(self, mocker):  # mocker is a magicmock object which is used for patching
        mock_ansible_module = mock_m.apply_mock_patch(mocker,
                                                      'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule')
        # mocking __get_device from CvDeviceTools class
        mock__get_device = mock_m.apply_mock_patch(mocker, 'ansible_collections.arista.cvp.plugins.'
                                                           'module_utils.device_tools.CvDeviceTools.'
                                                           '_CvDeviceTools__get_device')
        return mock_ansible_module, mock__get_device
>>>>>>> 7ca03e5 (Added docstrings and update code)
=======
    # list of paths to patch
    MOCK_LIST = [
        'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule',
        'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools._CvDeviceTools__get_device']
>>>>>>> 384f2ed (Restructured pytest)

    @pytest.mark.parametrize(
        "device_data, expected, expected_fail_json_call_msg",
        [
            (device_data, True, ""),
<<<<<<< HEAD
<<<<<<< HEAD
            (device_data_invalid, False, "Device decommissioning failed due to Device does "
                                         "not exist or is not registered to decommission"),
        ],
    )
    def test_decommission_device(self, setup, device_data, expected, expected_fail_json_call_msg):
        """
        Tests decommission_device() method for state_absent
        if device_data['serialNumber'] is correct:
            expected = true
        else:
            expected = false and error_msg
        """
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools = setup
        mock__get_device.return_value = device_data[0]  # mocked for get_device_facts, device_data is in tests/datadevice_tools_unit.py
        if expected:
            result = cv_tools.decommission_device(user_inventory=user_topology)
            assert result[0].success == expected
            assert result[0].changed == expected
        else:
            with pytest.raises(SystemExit) as pytest_error:
                _ = cv_tools.decommission_device(user_inventory=user_topology)
            assert pytest_error.value.code == 1
=======
            # (device_data_invalid, False, expected_fail_json_call_msg="----"), getting fail for err_msg
=======
            (device_data_invalid, False, "Device decommissioning failed due to Device does "
                                         "not exist or is not registered to decommission"),  # getting fail for err_msg
>>>>>>> 384f2ed (Restructured pytest)
        ],
    )
    def test_state_absent(self, setup, device_data, expected, expected_fail_json_call_msg):
        """
        Tests decommission_device() method for state_absent

        if device_data['serialNumber'] is correct:
            expected = true
        else:
            expected = false and error_msg

        """
        # status = 'DECOMMISSIONING_STATUS_SUCCESS'
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools = setup
        mock__get_device.return_value = device_data[0]  # mocked for get_device_facts, device_info is in tests/datadevice_tools_unit.py
        # TODO: need to check cvp_api.get_device_by_serial output through lab for device_info
<<<<<<< HEAD
        result = cv_tools.decommission_device(user_inventory=user_topology)
        assert result[0].success == expected
        assert result[0].changed == expected
        if not expected:
>>>>>>> 7ca03e5 (Added docstrings and update code)
=======
        if expected:
            result = cv_tools.decommission_device(user_inventory=user_topology)
            assert result[0].success == expected
            assert result[0].changed == expected
        else:
            _ = cv_tools.decommission_device(user_inventory=user_topology)
>>>>>>> 384f2ed (Restructured pytest)
            expected_call = [call.fail_json(msg=expected_fail_json_call_msg)]
            assert mock_ansible_module.mock_calls == expected_call

@pytest.mark.state
class TestResetDevice():
    """
    Contains unit tests for reset_device()
    """
    @pytest.mark.parametrize(
        "device_data, expected",
        [
            (device_data, True),
            (device_data_invalid, False),
        ],
    )
<<<<<<< HEAD
<<<<<<< HEAD
    def test_reset_device(self, setup, device_data, expected):
        """
        Tests reset_device method for state factory_reset
        device_data: dummy_device_data
=======
    def test_state_factory_reset(self, mocker, device_data, expected):
=======
    def test_state_factory_reset(self, setup, device_data, expected):
>>>>>>> 384f2ed (Restructured pytest)
        """
        Tests reset_device method for state factory_reset

        device_data: dummy_device_data

>>>>>>> 7ca03e5 (Added docstrings and update code)
        if device_data['parentContainerName'] is "undefined":
            expected = false
        else:
            expected = true
        """
        user_topology = DeviceInventory(data=device_data)
        _, _, cv_tools = setup
        result = cv_tools.reset_device(user_inventory=user_topology)
        assert result[0].success == expected
        assert result[0].changed == expected
        if expected:
            assert result[0].taskIds == ['57']

    @pytest.mark.parametrize(
        "device_data, expected_fail_json_call_msg",
        [
            (device_data_invalid, "Error resetting device"),
        ],
    )
    def test_reset_device_cvp_api_error(self, setup, device_data, expected_fail_json_call_msg):
        """
        Tests reset_device method with CvpApiError
        device_data: dummy_device_data
        if not device_data['parentContainerName']:
            fail_json() raises SystemExit
        """
        device_data_error = device_data.copy()
        device_data_error[0]['parentContainerName'] = None
        user_topology = DeviceInventory(data=device_data_error)
        mock_ansible_module, _, cv_tools = setup
        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.reset_device(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call


@pytest.mark.state
class TestDeleteDevice():
    """
    Contains unit tests for delete_device()
    """
    @pytest.mark.parametrize(
        "device_data, expected",
        [
            (device_data, True),
            (device_data_invalid, False),
        ],
    )
<<<<<<< HEAD
<<<<<<< HEAD
    def test_delete_device(self, setup, device_data, expected):
        """
        Tests delete_device method for state provisioning_reset
        device_data: dummy_device_data
        if device_data['systemMacAddress'] is correct:
            expected = true
        elif device_data['systemMacAddress'] is incorrect:
            expected = false
        """

=======
    def test_state_provisioning_reset(self, mocker, device_data, expected):
=======
    def test_state_provisioning_reset(self, setup, device_data, expected):
>>>>>>> 384f2ed (Restructured pytest)
        """
        Tests reset_device method for state provisioning_reset

        device_data: dummy_device_data

        if device_data['systemMacAddress'] is correct:
            expected = true
        else:
            expected = false
        """
<<<<<<< HEAD
        # mock_ansible_module = self.apply_mocks(mocker)
>>>>>>> 7ca03e5 (Added docstrings and update code)
        user_topology = DeviceInventory(data=device_data)
        _, _, cv_tools = setup
=======
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools = setup
>>>>>>> 384f2ed (Restructured pytest)
        result = cv_tools.delete_device(user_inventory=user_topology)
        assert result[0].success == expected
        assert result[0].changed == expected

    @pytest.mark.parametrize(
        "device_data,expected_fail_json_call_msg",
        [
            (device_data_invalid, "Error removing device from provisioning")
        ],
    )
    def test_delete_device_cvp_api_error(self, setup, device_data, expected_fail_json_call_msg):
        device_data_error = device_data.copy()
        device_data_error[0]['systemMacAddress'] = None
        user_topology = DeviceInventory(data=device_data_error)
        mock_ansible_module, _, cv_tools = setup

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.delete_device(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call
