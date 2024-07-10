# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from unittest.mock import call
import pytest
from ansible_collections.arista.cvp.plugins.module_utils.validate_tools import CvValidationTools
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import ModuleOptionValues
from tests.data.validate_tools_unit import (
    EXP_WARN, EXP_WARN_ERROR_IGNORE, EXP_ERROR, EXP_ERROR_IGNORE, EXP_VALID)

@pytest.fixture
def setup(apply_mock, mock_cvpClient):
    """
    setup - setup method to apply mocks and patches
    """
    mock_ansible_module, mock_get_system_mac, mock_get_configlet_by_name = apply_mock(TestValidateConfig.MOCK_LIST)
    cv_validation = CvValidationTools(mock_cvpClient, mock_ansible_module)
    return mock_get_system_mac, mock_get_configlet_by_name, cv_validation

@pytest.mark.generic
class TestValidateConfig():
    """
    Contains unit tests for validate_config()
    """
    # list of paths to patch
    MOCK_LIST = [
        'ansible_collections.arista.cvp.plugins.module_utils.validate_tools.AnsibleModule',
        'ansible_collections.arista.cvp.plugins.module_utils.validate_tools.CvValidationTools.get_system_mac',
        'ansible_collections.arista.cvp.plugins.module_utils.validate_tools.CvValidationTools.get_configlet_by_name']
    # user_topology = DeviceInventory(data=device_data)

    @pytest.mark.parametrize("validate_mode, devices, expected_calls",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_warning']
            }],
            [call.fail_json(
                msg="Encountered 1 warnings during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_WARN)],
            id="warning_stop_on_warning_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_warning': 'interface Ethernet1\n   spanning-tree portfast'}
            }],
            [call.fail_json(
                msg="Encountered 1 warnings during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_WARN)],
            id="warning_stop_on_warning_local"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_warning']
            }],
            EXP_WARN_ERROR_IGNORE,
            id="warning_stop_on_error_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_warning': 'interface Ethernet1\n   spanning-tree portfast'}
            }],
            EXP_WARN_ERROR_IGNORE,
            id="warning_stop_on_warning_local"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_warning']
            }],
            EXP_WARN_ERROR_IGNORE,
            id="warning_ignore_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_warning': 'interface Ethernet1\n   spanning-tree portfast'}
            }],
            EXP_WARN_ERROR_IGNORE,
            id="warning_ignore_local"
        )])
    def test_validate_config_warning(self, setup, validate_mode, devices, expected_calls):
        """
        warning case with
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to fail
        """
        # call setup() to apply mocks/patches
        mock_get_system_mac, mock_get_configlet_by_name, cv_validation = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock_get_system_mac.return_value = ''
        mock_get_configlet_by_name.return_value = {
            'name': 'validate_warning',
            'config': 'interface Ethernet1\n   spanning-tree portfast'}
        result = cv_validation.manager(devices=devices,
            validate_mode=validate_mode)
        if validate_mode in [
            ModuleOptionValues.VALIDATE_MODE_IGNORE,
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR ]:
            assert result.content == expected_calls
        else:
            assert cv_validation._CvValidationTools__ansible.mock_calls == expected_calls

    @pytest.mark.parametrize("validate_mode, devices, expected_calls",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_error']
            }],
            [call.fail_json(
                msg="Encountered 1 errors during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_ERROR)],
            id="error_stop_on_warning_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_error': 'ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111'}
            }],
            [call.fail_json(
                msg="Encountered 1 errors during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_ERROR)],
            id="error_stop_on_warning_local"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_error']
            }],
            [call.fail_json(
                msg="Encountered 1 errors during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_ERROR)],
            id="error_stop_on_error_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_error': 'ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111'}
            }],
            [call.fail_json(
                msg="Encountered 1 errors during validation. Refer to 'configlets_validated' for more details.",
                configlets_validated=EXP_ERROR)],
            id="error_stop_on_error_local"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_error']
            }],
            EXP_ERROR_IGNORE,
            id="error_ignore_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_error': 'ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111'}
            }],
            EXP_ERROR_IGNORE,
            id="error_ignore_local"
        )
        ])
    def test_validate_config_error(self, setup, validate_mode, devices, expected_calls):
        """
        error case with
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to fail
        """
        # call setup() to apply mocks/patches
        mock_get_system_mac, mock_get_configlet_by_name, cv_validation = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock_get_system_mac.return_value = ''
        mock_get_configlet_by_name.return_value = {
            'name': 'validate_error',
            'config': 'ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111'}
        result = cv_validation.manager(devices=devices,
            validate_mode=validate_mode)
        if validate_mode in [
            ModuleOptionValues.VALIDATE_MODE_IGNORE ]:
            assert result.content == expected_calls
        else:
            assert cv_validation._CvValidationTools__ansible.mock_calls == expected_calls

    @pytest.mark.parametrize("validate_mode, devices, expected_calls",
        [pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_valid']
            }],
            EXP_VALID,
            id="valid_stop_on_warning_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_valid': 'interface Ethernet1\n  description test_validate'}
            }],
            EXP_VALID,
            id="valid_stop_on_warning_local"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_valid']
            }],
            EXP_VALID,
            id="valid_stop_on_error_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_valid': 'interface Ethernet1\n  description test_validate'}
            }],
            EXP_VALID,
            id="valid_stop_on_error_local"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'cvp_configlets': [
                'validate_valid']
            }],
            EXP_VALID,
            id="valid_ignore_cvp"
        ),
        pytest.param(
            ModuleOptionValues.VALIDATE_MODE_IGNORE,
            [{
            'device_name': 'leaf1',
            'search_type': 'serialNumber',
            'local_configlets': {'validate_valid': 'interface Ethernet1\n  description test_validate'}
            }],
            EXP_VALID,
            id="valid_ignore_local"
        )
        ])
    def test_validate_config_valid(self, setup, validate_mode, devices, expected_calls):
        """
        error case with
        mode=[stop_on_warning, stop_on_error, ignore]
        expected to fail
        """
        # call setup() to apply mocks/patches
        mock_get_system_mac, mock_get_configlet_by_name, cv_validation = setup
        # mock the return value of CvDeviceTools.get_configlet_info()
        mock_get_system_mac.return_value = ''
        mock_get_configlet_by_name.return_value = {
            'name': 'validate_valid',
            'config': 'interface Ethernet1\n  description test_validate'}
        result = cv_validation.manager(devices=devices,
            validate_mode=validate_mode)
        assert result.content == expected_calls
