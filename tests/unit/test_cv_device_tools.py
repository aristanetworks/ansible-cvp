from unittest.mock import call
import pytest
from tests.data.device_tools_unit import device_data, current_container_info, cv_data, image_bundle
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from tests.lib.mockMagic import fail_json
from cvprac.cvp_client_errors import CvpApiError

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
    mock_ansible_module.fail_json.side_effect = fail_json
    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)
    return mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current

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
        _, _, cv_tools, mock_get_container_current = setup
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
        _, mock__get_device, cv_tools, mock_get_container_current = setup
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
        _, mock__get_device, cv_tools, mock_get_container_current = setup
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
        _, mock__get_device, cv_tools, mock_get_container_current = setup
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
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current = setup
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
        mock_ansible_module, mock__get_device, cv_tools, mock_get_container_current = setup

        mock_get_container_current.return_value = current_container_info
        mock__get_device.return_value = cv_data

        with pytest.raises(SystemExit) as pytest_error:
            _ = cv_tools.apply_bundle(user_inventory=user_topology)
        assert pytest_error.value.code == 1

        expected_call = [call.fail_json(msg='Error applying bundle to device tp-avd-leaf2:'
                                            ' Invalid_bundle_name not found')]
        assert mock_ansible_module.mock_calls == expected_call

        # resetting imageBundle
        device_data[0]['imageBundle'] = 'EOS-4.25.4M'
