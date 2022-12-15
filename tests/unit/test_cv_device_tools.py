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
from tests.lib import mockMagic
from tests.data.device_tools_unit import validate_ruter_bgp, validate_intf, validate_true
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import ModuleOptionValues

mock_m = mockMagic.MockModule()
mockCvpClient = mockMagic.MockCvpClient()
mockCvpApi = mockMagic.MockCvpApi()
mockCvpClient.mock_cvpClient.api.validate_config_for_device.side_effect = mockCvpApi.validate_config_for_device

device_data = [{
    'serialNumber': '0123F2E4462997EB155B7C50EC148767',
    'systemMacAddress': '50:08:00:b1:5b:0b',
    'key': '50:08:00:b1:5b:0b',
    'fqdn': 'tp-avd-leaf2',
    'hostname': 'tp-avd-leaf2',
    'parentContainerName': 'TP_LEAF1',
    'configlets': ['']}] # this is dummy device_data that has no effect

@pytest.mark.generic
class TestValidateConfig():

    # mocking
    def apply_mocks(self, mocker):
        mock_ansible_module = mock_m.apply_mock_patch(mocker,
        'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule')
        mock__get_configlet_info = mock_m.apply_mock_patch(mocker,
            'ansible_collections.arista.cvp.plugins.module_utils.device_tools.' \
                'CvDeviceTools._CvDeviceTools__get_configlet_info')
        return mock_ansible_module, mock__get_configlet_info

    def test_warning_stop_on_warning(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_intf
        # warning, mode=stop_on_warning; should fail
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING)
        expected_fail_json_call_msg = "{'warnings': [{'device': 'tp-avd-leaf2', 'warnings': ['! Interface does not exist. The configuration will not take effect until the module is inserted. at line 1']}], 'errors': []}"
        expected_call = [call.fail_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call


    def test_warning_stop_on_error(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_intf

        # warning, mode=stop_on_error; should NOT fail!
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR)
        expected_fail_json_call_msg = "{'warnings': [{'device': 'tp-avd-leaf2', 'warnings': ['! Interface does not exist. The configuration will not take effect until the module is inserted. at line 1']}], 'errors': []}"
        expected_call = [call.exit_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call

    def test_warning_skip(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_intf
        # warning, mode=skip; should NOT fail!
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_IGNORE)
        expected_fail_json_call_msg = "{'warnings': [{'device': 'tp-avd-leaf2', 'warnings': ['! Interface does not exist. The configuration will not take effect until the module is inserted. at line 1']}], 'errors': []}"
        expected_call = [call.exit_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call

    def test_error_stop_on_warning(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_ruter_bgp

        # error, mode=stop_on_warning; should fail!
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING)
        expected_fail_json_call_msg = '{\'warnings\': [], \'errors\': [{\'device\': \'tp-avd-leaf2\', \'errors\': [{\'error\': "> ruter bgp 1111% Invalid input (at token 0: \'ruter\') at line 1", \'lineNo\': \' 1\'}, {\'error\': ">    neighbor 1.1.1.1 remote-bs 111% Invalid input (at token 1: \'1.1.1.1\') at line 2", \'lineNo\': \' 2\'}]}]}'
        expected_call = [call.fail_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call

    def test_error_stop_on_error(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_ruter_bgp

        # error, mode=stop_on_error; should fail!
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR)
        expected_fail_json_call_msg = '{\'warnings\': [], \'errors\': [{\'device\': \'tp-avd-leaf2\', \'errors\': [{\'error\': "> ruter bgp 1111% Invalid input (at token 0: \'ruter\') at line 1", \'lineNo\': \' 1\'}, {\'error\': ">    neighbor 1.1.1.1 remote-bs 111% Invalid input (at token 1: \'1.1.1.1\') at line 2", \'lineNo\': \' 2\'}]}]}'
        expected_call = [call.fail_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call

    def test_error_skip(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_ruter_bgp

        # error, mode=SKIP; should NOT fail!
        _ = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_IGNORE)
        expected_fail_json_call_msg = '{\'warnings\': [], \'errors\': [{\'device\': \'tp-avd-leaf2\', \'errors\': [{\'error\': "> ruter bgp 1111% Invalid input (at token 0: \'ruter\') at line 1", \'lineNo\': \' 1\'}, {\'error\': ">    neighbor 1.1.1.1 remote-bs 111% Invalid input (at token 1: \'1.1.1.1\') at line 2", \'lineNo\': \' 2\'}]}]}'
        expected_call = [call.exit_json(msg=expected_fail_json_call_msg)]
        assert mock_ansible_module.mock_calls == expected_call

    def test_valid_stop_on_warning(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_true

        expected_result = {'changed': True,
            'diff': None,
            'success': True,
            'taskIds': [],
            'tp-avd-leaf2_validated_count': 1,
            'tp-avd-leaf2_validated_list': ["tp-avd-leaf2 validated against {'config': "
                                            "'interface Ethernet1\\n  description "
                                            "test_validate', 'containerCount': 0, "
                                            "'dateTimeInLongFormat': 1668635365675, "
                                            "'editable': True, 'isAutoBuilder': '', "
                                            "'isDefault': 'no', 'isDraft': False, 'key': "
                                            "'configlet_30869fe3-00f2-4c07-988b-ab9df54eb52f', "
                                            "'name': 'validate_test_true', "
                                            "'netElementCount': 0, 'note': '', "
                                            "'reconciled': False, 'sslConfig': False, "
                                            "'type': 'Static', 'typeStudioConfiglet': "
                                            "False, 'user': 'cvpadmin', 'visible': True}"]}

        # valid, mode=stop_on_warning; should NOT fail!
        result = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_STOP_ON_WARNING)
        assert result[0].results == expected_result

    def test_valid_stop_on_error(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_true

        expected_result = {'changed': True,
            'diff': None,
            'success': True,
            'taskIds': [],
            'tp-avd-leaf2_validated_count': 1,
            'tp-avd-leaf2_validated_list': ["tp-avd-leaf2 validated against {'config': "
                                            "'interface Ethernet1\\n  description "
                                            "test_validate', 'containerCount': 0, "
                                            "'dateTimeInLongFormat': 1668635365675, "
                                            "'editable': True, 'isAutoBuilder': '', "
                                            "'isDefault': 'no', 'isDraft': False, 'key': "
                                            "'configlet_30869fe3-00f2-4c07-988b-ab9df54eb52f', "
                                            "'name': 'validate_test_true', "
                                            "'netElementCount': 0, 'note': '', "
                                            "'reconciled': False, 'sslConfig': False, "
                                            "'type': 'Static', 'typeStudioConfiglet': "
                                            "False, 'user': 'cvpadmin', 'visible': True}"]}

        # valid, mode=stop_on_error; should NOT fail!
        result = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_STOP_ON_ERROR)
        assert result[0].results == expected_result

    def test_valid_skip(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(mockCvpClient.mock_cvpClient, mock_ansible_module)
        mock__get_configlet_info.return_value=validate_true

        expected_result = {'changed': True,
            'diff': None,
            'success': True,
            'taskIds': [],
            'tp-avd-leaf2_validated_count': 1,
            'tp-avd-leaf2_validated_list': ["tp-avd-leaf2 validated against {'config': "
                                            "'interface Ethernet1\\n  description "
                                            "test_validate', 'containerCount': 0, "
                                            "'dateTimeInLongFormat': 1668635365675, "
                                            "'editable': True, 'isAutoBuilder': '', "
                                            "'isDefault': 'no', 'isDraft': False, 'key': "
                                            "'configlet_30869fe3-00f2-4c07-988b-ab9df54eb52f', "
                                            "'name': 'validate_test_true', "
                                            "'netElementCount': 0, 'note': '', "
                                            "'reconciled': False, 'sslConfig': False, "
                                            "'type': 'Static', 'typeStudioConfiglet': "
                                            "False, 'user': 'cvpadmin', 'visible': True}"]}

        # valid, mode=skip; should NOT fail!
        result = cv_tools.validate_config(user_inventory=user_topology,
            validate_mode=ModuleOptionValues.VALIDATE_MODE_IGNORE)
        assert result[0].results == expected_result
