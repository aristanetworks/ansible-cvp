from unittest.mock import call
import pytest
from tests.data.device_tools_unit import device_data, device_data_invalid
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from tests.lib.mockMagic import fail_json
from cvprac.cvp_client_errors import CvpApiError

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
    mock_ansible_module.fail_json.side_effect = fail_json
    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)

    return mock_ansible_module, mock__get_device, cv_tools

class TestDecommissionDevice():
    """
    Contains unit tests for decommission_device()
    """

    @pytest.mark.parametrize(
        "device_data, flag, expected_call",
        [
            (device_data, True, ""),
            (device_data_invalid, False, [call.fail_json(msg="Device decommissioning failed due to Device does "
                                         "not exist or is not registered to decommission")]),
        ],
    )
    def test_decommission_device(self, setup, device_data, flag, expected_call):
        """
        Tests decommission_device() method for state_absent

        flag: used to decide on failure or success of decommission_device

        if device_data['serialNumber'] is correct:
            result = success
        else:
            result = failure with error_msg
        """
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools = setup
        mock__get_device.return_value = device_data[0]  # mocked for get_device_facts, device_data is in tests/data/device_tools_unit.py

        if flag:
            #valid user_topology input
            result = cv_tools.decommission_device(user_inventory=user_topology)
            assert result[0].success
            assert result[0].changed
        else:
            #invalid user_topology input with wrong serial_number
            with pytest.raises(SystemExit) as pytest_error:
                _ = cv_tools.decommission_device(user_inventory=user_topology)
            assert pytest_error.value.code == 1
            assert mock_ansible_module.mock_calls == expected_call

    def test_decommission_device_cvp_api_error(self, setup, mock_cvpClient):
        """
        Tests decommission_device() method for state_absent

        if device_data['serialNumber'] is None:
            raise CvpApiError and fail_json() raises SystemExit
        """
        user_topology = DeviceInventory(data=device_data_invalid)
        mock_ansible_module, mock__get_device, cv_tools = setup

        # mocked for get_device_facts, device_data is in tests/data/device_tools_unit.py
        mock__get_device.return_value = device_data[0]
        mock_cvpClient.api.device_decommissioning.side_effect = CvpApiError("Error decommissioning device")
        #user_topology input with serial_number None
        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.decommission_device(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg="Error decommissioning device")]
        assert mock_ansible_module.mock_calls == expected_call

    def test_decommission_device_check_mode_true(self, setup):
        """
        Tests decommission_device() method with check_mode true
        """
        user_topology = DeviceInventory(data=device_data)
        _, _, cv_tools = setup
        cv_tools.check_mode = True

        result = cv_tools.decommission_device(user_inventory=user_topology)
        assert result[0].success
        assert not result[0].changed
        assert result[0].taskIds == ["check_mode"]

class TestResetDevice():
    """
    Contains unit tests for reset_device()
    """
    @pytest.mark.parametrize(
        "device_data, expected_result, task_ids",
        [
            (device_data, True, ['57']),
            (device_data_invalid, False, ''),
        ],
    )
    def test_reset_device(self, setup, device_data, expected_result, task_ids):
        """
        Tests reset_device() method for state factory_reset

        device_data: dummy_device_data
        task_ids: list of task_ids created when the reset_device is successful

        if device_data['parentContainerName'] is "undefined":
            expected_result = false
        else:
            expected_result = true
            task_ids = ['57']
        """
        user_topology = DeviceInventory(data=device_data)
        _, _, cv_tools = setup
        result = cv_tools.reset_device(user_inventory=user_topology)
        assert result[0].success == expected_result
        assert result[0].changed == expected_result
        if result[0].taskIds:
            assert result[0].taskIds == task_ids


    def test_reset_device_cvp_api_error(self, setup, mock_cvpClient):
        """
        Tests reset_device method with CvpApiError

        device_data: dummy_device_data
        """
        user_topology = DeviceInventory(data=device_data_invalid)
        mock_ansible_module, _, cv_tools = setup
        mock_cvpClient.api.reset_device.side_effect = CvpApiError("Error decommissioning device")

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.reset_device(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg="Error resetting device")]
        assert mock_ansible_module.mock_calls == expected_call

class TestDeleteDevice():
    """
    Contains unit tests for delete_device()
    """
    @pytest.mark.parametrize(
        "device_data, expected_result",
        [
            (device_data, True),
            (device_data_invalid, False),
        ],
    )
    def test_delete_device(self, setup, device_data, expected_result):
        """
        Tests delete_device method for state provisioning_reset

        device_data: dummy_device_data
        if device_data['systemMacAddress'] is correct:
            expected_result = true
        elif device_data['systemMacAddress'] is incorrect:
            expected_result = false
        """

        user_topology = DeviceInventory(data=device_data)
        _, _, cv_tools = setup
        result = cv_tools.delete_device(user_inventory=user_topology)
        assert result[0].success == expected_result
        assert result[0].changed == expected_result

    def test_delete_device_cvp_api_error(self, setup, mock_cvpClient):
        """
        device_data: dummy_device_data
        """
        user_topology = DeviceInventory(data=device_data_invalid)
        mock_ansible_module, _, cv_tools = setup
        mock_cvpClient.api.delete_device.side_effect = CvpApiError("Error decommissioning device")

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.delete_device(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg="Error removing device from provisioning")]
        assert mock_ansible_module.mock_calls == expected_call

    def test_delete_device_check_mode_true(self, setup):
        """
        Tests delete_device() method with check_mode true
        """
        user_topology = DeviceInventory(data=device_data)
        _, _, cv_tools = setup
        cv_tools.check_mode = True

        result = cv_tools.delete_device(user_inventory=user_topology)
        assert result[0].success
        assert not result[0].changed
        assert result[0].taskIds == ["check_mode"]
