#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint: disable=redefined-outer-name
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from unittest.mock import call
import pytest
from tests.data.device_tools_unit import validate_router_bgp, validate_intf, validate_true, device_data, EXP_WARN_WARN, EXP_ERROR, EXP_VALID
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import ModuleOptionValues

@pytest.fixture
def setup(apply_mock, mock_cvprac):
    """
    setup - setup method to apply mocks and patches
    """
    mock_ansible_module, mock__get_configlet_info = apply_mock(TestValidateConfig.MOCK_LIST)
    dummy_cvprac, mock_cvpClient = mock_cvprac
    mock_cvpClient.api.validate_config_for_device.side_effect = dummy_cvprac.validate_config_for_device
    user_topology = DeviceInventory(data=device_data)
    cv_tools = CvDeviceTools(mock_cvpClient, mock_ansible_module)
    return mock_ansible_module, mock__get_configlet_info, user_topology, cv_tools

@pytest.mark.generic
class TestValidateConfig():
    """
    Contains unit tests for validate_config()
    """

    # list of paths to patch
    MOCK_LIST = [
        'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule',
        'ansible_collections.arista.cvp.plugins.module_utils.device_tools.CvDeviceTools._CvDeviceTools__get_configlet_info']

    @pytest.mark.parametrize("validate_mode, expected_calls",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING, [call.fail_json(msg=EXP_WARN_WARN)], id="warning_stop_on_warning"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR, [call.exit_json(msg=EXP_WARN_WARN)], id="warning_stop_on_error"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE, [call.exit_json(msg=EXP_WARN_WARN)], id="warning_skip"
        ),
        ])
    def test_validate_config_warning(self, setup, validate_mode, expected_calls):
        """
        warning case with
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to fail
        """
        # call setup() to apply mocks/patches
        mock_ansible_module, mock__get_configlet_info, user_topology, cv_tools = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock__get_configlet_info.return_value=validate_intf
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=validate_mode)
        assert mock_ansible_module.mock_calls == expected_calls

    @pytest.mark.parametrize("validate_mode, expected_calls",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING, [call.fail_json(msg=EXP_ERROR)], id="error_stop_on_warning"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR, [call.fail_json(msg=EXP_ERROR)], id="error_stop_on_error"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE, [call.exit_json(msg=EXP_ERROR)], id="error_skip"
        ),
        ])
    def test_validate_config_error(self, setup, validate_mode, expected_calls):
        """
        error case
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to fail
        """
        # call setup() to apply mocks/patches
        mock_ansible_module, mock__get_configlet_info, user_topology, cv_tools = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock__get_configlet_info.return_value=validate_router_bgp
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=validate_mode)
        assert mock_ansible_module.mock_calls == expected_calls

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
        _, mock__get_configlet_info, user_topology, cv_tools = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock__get_configlet_info.return_value=validate_true
        result = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=validate_mode)
        assert result[0].results == expected_result
