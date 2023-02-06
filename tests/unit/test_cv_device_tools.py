from unittest.mock import call
import pytest
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import ModuleOptionValues
from tests.data.device_tools_unit import (validate_router_bgp,
    validate_intf, validate_true, device_data, EXP_WARN, EXP_WARN_IGNORE, EXP_ERROR, EXP_VALID)

@pytest.fixture
def setup(apply_mock, mock_cvpClient):
    """
    setup - setup method to apply mocks and patches
    """
    mock_ansible_module, mock__get_configlet_info = apply_mock(TestValidateConfig.MOCK_LIST)
    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)
    return mock__get_configlet_info, cv_tools

@pytest.mark.generic
class TestValidateConfig():
    """
    Contains unit tests for validate_config()
    """
    # list of paths to patch
    MOCK_LIST = [
        'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule',
        'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools._CvDeviceTools__get_configlet_info']
    user_topology = DeviceInventory(data=device_data)

    @pytest.mark.parametrize("validate_mode, expected_calls",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING, [call.fail_json(
                msg="Encountered 1 warnings during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_WARN)],
            id="warning_stop_on_warning"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR, [call.exit_json(
                msg="Encountered 1 warnings during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_WARN)],
            id="warning_stop_on_error"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE, EXP_WARN_IGNORE, id="warning_skip"
        ),
        ])
    def test_validate_config_warning(self, setup, validate_mode, expected_calls):
        """
        warning case with
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to fail
        """
        # call setup() to apply mocks/patches
        mock__get_configlet_info, cv_tools = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock__get_configlet_info.return_value=validate_intf
        result = cv_tools.validate_config(user_inventory=self.user_topology,
            validate_mode=validate_mode)
        if validate_mode == ModuleOptionValues.VALIDATE_MODE_IGNORE:
            assert result[0].results == expected_calls
        else:
            assert cv_tools._CvDeviceTools__ansible.mock_calls == expected_calls

    @pytest.mark.parametrize("validate_mode, expected_calls",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING, [call.fail_json(
                msg="Encountered 1 errors during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_ERROR)],
            id="error_stop_on_warning"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR, [call.fail_json(
                msg="Encountered 1 errors during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_ERROR)],
            id="error_stop_on_error"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE, [call.exit_json(
                msg="Encountered 1 errors during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_ERROR)], id="error_skip"
        ),
        ])
    def test_validate_config_error(self, setup, validate_mode, expected_calls):
        """
        error case
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to fail
        """
        # call setup() to apply mocks/patches
        mock__get_configlet_info, cv_tools = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock__get_configlet_info.return_value=validate_router_bgp
        cv_tools.validate_config(user_inventory=self.user_topology,
            validate_mode=validate_mode)
        assert cv_tools._CvDeviceTools__ansible.mock_calls == expected_calls

    @pytest.mark.parametrize("validate_mode, expected_result",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING, EXP_VALID, id="valid_stop_on_warning"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR, EXP_VALID, id="valid_stop_on_error"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE, EXP_VALID, id="valid_skip"
        ),
        ])
    def test_validate_config_valid(self, setup, validate_mode, expected_result):
        """
        valid case
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to pass
        """
        # call setup() to apply mocks/patches
        mock__get_configlet_info, cv_tools = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock__get_configlet_info.return_value=validate_true
        result = cv_tools.validate_config(user_inventory=self.user_topology,
            validate_mode=validate_mode)
        assert result[0].results == expected_result
