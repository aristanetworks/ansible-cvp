# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from unittest.mock import call
import pytest

from tests.data.device_tools_unit import device_data, device_data_invalid, current_container_info, cv_data, image_bundle
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from cvprac.cvp_client_errors import CvpApiError
from tests.lib.mockMagic import fail_json

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
    mock_ansible_module.fail_json.side_effect = fail_json
    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)
    return mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, mock_get_container_info

class TestMoveDevice():
    """
    Contains unit tests for move_device()
    """
    @pytest.mark.parametrize(
        "expected, test_flag",
        [
            (True, None), # success
            (False, 0),   # failure for same device and current container name
            (False, "current_container_none"), #current_container_info == None
            (False, "current_container_undefined"), #current_container_info == "undefined_container"
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
        :param test_flag: different conditions for success and failure.
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

        if test_flag == "current_container_none":
            mock_get_container_current.return_value = None
        elif test_flag == "current_container_undefined":
            mock_get_container_current.return_value = "undefined_container"

        result = cv_tools.move_device(user_inventory=user_topology)
        device_data[0]["systemMacAddress"] = '50:08:00:b1:5b:0b'
        device_data[0]["parentContainerName"] = "TP_LEAF1"

        assert result[0].success == expected
        assert result[0].changed == expected


    def test_move_device_cvp_api_error(self, setup, mock_cvpClient):
        """
        Test for CvpApiError.
        :param setup: fixture
        """

        device_data[0]["parentContainerName"] = "TP_LEAF2" # newContainerName and currentContainerName should be different.
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, mock_get_container_info = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        mock_cvpClient.api.move_device_to_container.side_effect = CvpApiError(msg="")

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.move_device(user_inventory=user_topology)
        device_data[0]["parentContainerName"] = "TP_LEAF1"
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg='Error to move device tp-avd-leaf2 to container TP_LEAF2')]
        assert mock_ansible_module.mock_calls == expected_call

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
        expected_call = [call.fail_json(msg="The target container 'TP_LEAF1' for the device 'tp-avd-leaf2' does not exist on CVP.")]
        assert mock_ansible_module.mock_calls == expected_call

class TestApplyBundle():
    """
    Contains unit tests for apply_bundle()
    """

    @pytest.mark.parametrize(
        "current_container_info",
        [
            {
                'name': 'undefined_container',
                'key': 'container_208aadc9-ecc0-4970-b524-6712a0baaade'
            },
        ],
    )
    def test_apply_bundle_with_undefined_container(self, setup, current_container_info):
        """
        Test when the device is in the undefined container
        """
        user_topology = DeviceInventory(data=device_data)
        _, _, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info

        result = cv_tools.apply_bundle(user_inventory=user_topology)
        assert not result

    def test_apply_bundle_with_same_image(self, setup):
        """
        Test when current_image_bundle and assigned_image_bundle are same
        :param setup: fixture

        if both image bundles are same, nothing to do.
        """
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info

        #setting same image_bundle names
        cv_data['imageBundle']['bundleName'] = device_data[0]['imageBundle']
        mock__get_device.return_value = cv_data

        result = cv_tools.apply_bundle(user_inventory=user_topology)

        # re-setting image_bundle name in cv_data
        cv_data['imageBundle']['bundleName'] = 'EOS-4.26.4M'

        assert result[0].success is False
        assert result[0].changed is False

    @pytest.mark.parametrize(
        "expected",
        [
            (True),    #  success
            (False),   # failure
        ],
    )
    def test_apply_bundle_with_different_image(self, setup, expected):
        """
        Test when current_image_bundle and assigned_image_bundle are different

        :param setup: fixture
        :param expected: output expected from apply_bundle

        """
        _, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data

        if not expected:
            # image_bundle is the bundle information we get from api call for get_image_bundle_by_name
            # removing node_id for failure test-case
            image_bundle['id'] = None

        user_topology = DeviceInventory(data=device_data)
        result = cv_tools.apply_bundle(user_inventory=user_topology)

        # resetting imageBundle id
        image_bundle['id'] = 'imagebundle_1658329041200536707'


        assert result[0].success == expected
        assert result[0].changed == expected

    def test_apply_bundle_check_mode_true(self, setup):
        """
        Test when check_mode is true
        :param setup: fixture

        """
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        cv_tools.check_mode = True

        result = cv_tools.apply_bundle(user_inventory=user_topology)
        assert result[0].success == True
        assert result[0].changed == False
        assert result[0].taskIds == ["check_mode"]

    def test_apply_bundle_cvp_api_error(self, setup, mock_cvpClient):
        """
        Test for CvpApiError.
        :param setup: fixture

        """
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        mock_cvpClient.api.apply_image_to_element.side_effect = CvpApiError(msg='Image bundle ID is not valid')

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.apply_bundle(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg='Error applying bundle to device tp-avd-leaf2: Image bundle ID is not valid')]
        assert mock_ansible_module.mock_calls == expected_call

    def test_apply_bundle_with_image_bundle_invalid(self, setup):
        """
        Test when provided imageBundle name is invalid and couldn't get image_bundle from CV
        :param setup: fixture

        """
        device_data[0]['imageBundle'] = 'Invalid_bundle_name'
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, _ = setup

        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.apply_bundle(user_inventory=user_topology)
        assert pytest_error.value.code == 1

        # resetting imageBundle
        device_data[0]['imageBundle'] = 'EOS-4.25.4M'

        expected_call = [call.fail_json(msg='Error applying bundle to device tp-avd-leaf2:'
                                            ' Invalid_bundle_name not found')]
        assert mock_ansible_module.mock_calls == expected_call


class TestDetachBundle():
    """
    Contains unit tests for detach_bundle()
    """
    @pytest.mark.parametrize(
        "expected_result",
        [
            (True),    #  success
            (False),   # failure
        ],
    )
    def test_detach_bundle(self, setup, expected_result):
        """
        Test device.image_bundle is None and check_mode is false

        :param setup: fixture
        :param expected: output expected from detach_bundle()

        """
        device_data[0]['imageBundle'] = None
        _, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        if not expected_result:
            # removing node_id for failure test-case
            image_bundle['id'] = None

        user_topology = DeviceInventory(data=device_data)
        result = cv_tools.detach_bundle(user_inventory=user_topology)

        # resetting imageBundle id
        image_bundle['id'] = 'imagebundle_1658329041200536707'
        device_data[0]['imageBundle'] = 'EOS-4.25.4M'

        assert result[0].success == expected_result
        assert result[0].changed == expected_result


    def test_detach_bundle_curent_image_none(self, setup):
        """
        Test when current_image_bundle is none
        :param setup: fixture

        if current_image_bundle, returns empty list
        """
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info

        mock__get_device.return_value = None

        result = cv_tools.detach_bundle(user_inventory=user_topology)
        assert not result

    def test_detach_bundle_device_image_not_none(self, setup):
        """
        Test when device.image_bundle is not None
        :param setup: fixture

        if device.image_bundle is not None, result_data have default values
        """
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info

        mock__get_device.return_value = cv_data

        result = cv_tools.detach_bundle(user_inventory=user_topology)
        assert result[0].success == False
        assert result[0].changed == False

    def test_detach_bundle_cvp_api_error(self, setup, mock_cvpClient):
        """
        Test for CvpApiError.
        :param setup: fixture
        """
        device_data[0]['imageBundle'] = None
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        mock_cvpClient.api.remove_image_from_element.side_effect = CvpApiError(msg="Image bundle ID is not valid")

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.detach_bundle(user_inventory=user_topology)

        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg='Error removing bundle from device tp-avd-leaf2: Image bundle ID is not valid')]
        assert mock_ansible_module.mock_calls == expected_call


    def test_detach_bundle_check_mode_true(self, setup):
        """
        if cv_tools.check_mode is True, result_data is updated
        """
        device_data[0]['imageBundle'] = None
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current, _ = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        cv_tools.check_mode =True

        result = cv_tools.detach_bundle(user_inventory=user_topology)

        # resetting imageBundle
        device_data[0]['imageBundle'] = 'EOS-4.25.4M'

        assert result[0].success == True
        assert result[0].changed == False
        assert result[0].taskIds == ['check_mode']


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
        mock_ansible_module, mock__get_device, cv_tools, _, _ = setup
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
        mock_ansible_module, mock__get_device, cv_tools, _, _ = setup

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
        _, _, cv_tools, _, _ = setup
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
        _, _, cv_tools, _, _ = setup
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
        mock_ansible_module, _, cv_tools, _, _ = setup
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
        _, _, cv_tools, _, _ = setup
        result = cv_tools.delete_device(user_inventory=user_topology)
        assert result[0].success == expected_result
        assert result[0].changed == expected_result

    def test_delete_device_cvp_api_error(self, setup, mock_cvpClient):
        """
        device_data: dummy_device_data
        """
        user_topology = DeviceInventory(data=device_data_invalid)
        mock_ansible_module, _, cv_tools, _, _ = setup
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
        _, _, cv_tools, _, _ = setup
        cv_tools.check_mode = True

        result = cv_tools.delete_device(user_inventory=user_topology)
        assert result[0].success
        assert not result[0].changed
        assert result[0].taskIds == ["check_mode"]
