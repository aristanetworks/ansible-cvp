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
from tests.data.device_tools_unit import device_data, current_container_info, cv_data, image_bundle
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools


# list of paths to patch
MOCK_LIST = [
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule',
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools._CvDeviceTools__get_device',
    'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools.get_container_current']

@pytest.fixture
def setup(apply_mock, mock_cvpClient):
    """
    setup - setup method to apply mocks and patches
    """
    mock_ansible_module, mock__get_device, mock_get_container_current = apply_mock(MOCK_LIST)

    mock_ansible_module.fail_json.side_effect = mock_cvpClient.api.fail_json

    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)

    return mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current


@pytest.mark.state_present
class TestDetachBundle():
    """
    Contains unit tests for detach_bundle()
    """
    @pytest.mark.parametrize(
        "expected",
        [
            (True),    #  success
            (False),   # failure
        ],
    )
    def test_detach_bundle(self, setup, expected):
        """
        Test device.image_bundle is None and check_mode is false

        :param setup: fixture
        :param expected: output expected from detach_bundle()

        """
        device_data[0]['imageBundle'] = None
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        if not expected:
            # removing node_id for failure test-case
            image_bundle['id'] = None

        result = cv_tools.detach_bundle(user_inventory=user_topology)
        assert result[0].success == expected
        assert result[0].changed == expected

        # resetting imageBundle id
        image_bundle['id'] = 'imagebundle_1658329041200536707'
        device_data[0]['imageBundle'] = 'EOS-4.25.4M'

    def test_detach_bundle_curent_image_none(self, setup):
        """
        Test when current_image_bundle is none
        :param setup: fixture

        if current_image_bundle, returns empty list
        """
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current = setup
        mock_get_container_current.return_value = current_container_info

        mock__get_device.return_value = None

        result = cv_tools.detach_bundle(user_inventory=user_topology)
        assert not result

    def test_detach_bundle_device_image_none(self, setup):
        """
        Test when device.image_bundle is not None
        :param setup: fixture

        if device.image_bundle is not None, result_data have default values
        """
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current = setup
        mock_get_container_current.return_value = current_container_info

        mock__get_device.return_value = cv_data

        result = cv_tools.detach_bundle(user_inventory=user_topology)
        assert result[0].success == False
        assert result[0].changed == False

    def test_detach_bundle_cvp_api_error(self, setup):
        """
        Test for CvpApiError.
        :param setup: fixture

        if image_bundle['id'] = 'error_id', raises CvpApiError
        """
        device_data[0]['imageBundle'] = None
        user_topology = DeviceInventory(data=device_data)
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        image_bundle['id'] = 'error_id'

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.detach_bundle(user_inventory=user_topology)
        assert pytest_error.value.code == 1
        expected_call = [call.fail_json(msg='Error removing bundle from device tp-avd-leaf2: Image bundle ID is not valid')]
        assert mock_ansible_module.mock_calls == expected_call

        # resetting imageBundle
        image_bundle['id'] = 'imagebundle_1658329041200536707'

    def test_detach_bundle_check_mode_true(self, setup):
        """
        if cv_tools.check_mode is True, result_data is updated
        """
        device_data[0]['imageBundle'] = None
        user_topology = DeviceInventory(data=device_data)
        _, mock__get_device, cv_tools, mock_get_container_current = setup
        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data
        cv_tools.check_mode =True

        result = cv_tools.detach_bundle(user_inventory=user_topology)
        assert result[0].success == True
        assert result[0].changed == False
        assert result[0].taskIds == ['check_mode']

        # resetting imageBundle
        device_data[0]['imageBundle'] = 'EOS-4.25.4M'
