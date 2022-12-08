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
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools
from ansible_collections.arista.cvp.plugins.module_utils.resources.modules.fields import ModuleOptionValues

# error configlet
validate_ruter_bgp = {'config': 'ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111',
            'containerCount': 0,
            'dateTimeInLongFormat': 1668634708856,
            'editable': True,
            'isAutoBuilder': '',
            'isDefault': 'no',
            'isDraft': False,
            'key': 'configlet_3f7f850a-f8e1-4d33-b3cd-e8dd90039a87',
            'name': 'validate_ruter_bgp',
            'netElementCount': 0,
            'note': '',
            'reconciled': False,
            'sslConfig': False,
            'type': 'Static',
            'typeStudioConfiglet': False,
            'user': 'cvpadmin',
            'visible': True
        }
# warning configlet
validate_intf = {'config': 'interface Ethernet10\n  description test\n!\n',
    'containerCount': 0,
    'dateTimeInLongFormat': 1668634684230,
    'editable': True,
    'isAutoBuilder': '',
    'isDefault': 'no',
    'isDraft': False,
    'key': 'configlet_59279a3b-bbea-4a89-b6c3-bdd759a82722',
    'name': 'validate_intf',
    'netElementCount': 0,
    'note': '',
    'reconciled': False,
    'sslConfig': False,
    'type': 'Static',
    'typeStudioConfiglet': False,
    'user': 'cvpadmin',
    'visible': True}
# device_data = [{'serialNumber': 'BAD032986065E8DC14CBB6472EC314A6', 'fqdn': 'tp-avd-leaf1', 'hostname': 'tp-avd-leaf1', 'parentContainerName': 'TP_LEAF1', 'configlets': ['validate_ruter_bgp']}, {'serialNumber': '0123F2E4462997EB155B7C50EC148767', 'fqdn': 'tp-avd-leaf2', 'hostname': 'tp-avd-leaf2', 'parentContainerName': 'TP_LEAF1', 'configlets': ['validate_intf']}]
# true configlet
validate_true = {'config': 'interface Ethernet1\n  description test_validate',
    'containerCount': 0,
    'dateTimeInLongFormat': 1668635365675,
    'editable': True,
    'isAutoBuilder': '',
    'isDefault': 'no',
    'isDraft': False,
    'key': 'configlet_30869fe3-00f2-4c07-988b-ab9df54eb52f',
    'name': 'validate_test_true',
    'netElementCount': 0,
    'note': '',
    'reconciled': False,
    'sslConfig': False,
    'type': 'Static',
    'typeStudioConfiglet': False,
    'user': 'cvpadmin',
    'visible': True}
return_validate_true = {'id': 'Arista-3-4135109651348942',
 'jsonrpc': '2.0',
 'result': [{'messages': ['Copy completed successfully.'],
             'output': 'enter input line by line; when done enter one or more '
                       'control-d\n'
                       'Copy completed successfully.\n'},
            {'output': '! Command: show session-configuration named '
                       'capiVerify-2101-4e2f8652701311eda2d2020000000000\n'
                       '! device: tp-avd-leaf1 (vEOS-lab, EOS-4.28.3M)\n'
                       '!\n'
                       '! boot system flash:/vEOS-lab-4.28.3M.swi\n'
                       '!\n'
                       'no aaa root\n'
                       '!\n'
                       'transceiver qsfp default-mode 4x10G\n'
                       '!\n'
                       'service routing protocols model ribd\n'
                       '!\n'
                       'spanning-tree mode mstp\n'
                       '!\n'
                       'interface Ethernet1\n'
                       '   description test_validate\n'
                       '!\n'
                       'interface Ethernet2\n'
                       '!\n'
                       'interface Ethernet3\n'
                       '!\n'
                       'interface Ethernet4\n'
                       '!\n'
                       'interface Ethernet5\n'
                       '!\n'
                       'interface Management1\n'
                       '!\n'
                       'no ip routing\n'
                       '!\n'
                       'end\n',
             'warnings': ['Command: show session-configuration named '
                          'capiVerify-2101-4e2f8652701311eda2d2020000000000']}],
 'warningCount': 0,
 'warnings': []}
return_validate_intf = {'id': 'Arista-3-3551555206824559',
 'jsonrpc': '2.0',
 'result': [{'messages': ['Copy completed successfully.'],
             'output': 'enter input line by line; when done enter one or more '
                       'control-d\n'
                       '\n'
                       '> interface Ethernet10\n'
                       '\n'
                       '! Interface does not exist. The configuration will not '
                       'take effect until the module is inserted. at line 1\n'
                       'Copy completed successfully.\n'},
            {'output': '! Command: show session-configuration named '
                       'capiVerify-2084-9ca297ba6ac411ed9eda020000000000\n'
                       '! device: tp-avd-leaf2 (vEOS-lab, EOS-4.28.2F)\n'
                       '!\n'
                       '! boot system flash:/vEOS-lab-4.28.2F.swi\n'
                       '!\n'
                       'no aaa root\n'
                       '!\n'
                       'transceiver qsfp default-mode 4x10G\n'
                       '!\n'
                       'service routing protocols model ribd\n'
                       '!\n'
                       'spanning-tree mode mstp\n'
                       '!\n'
                       'interface Ethernet1\n'
                       '!\n'
                       'interface Ethernet2\n'
                       '!\n'
                       'interface Ethernet3\n'
                       '!\n'
                       'interface Ethernet4\n'
                       '!\n'
                       'interface Ethernet5\n'
                       '!\n'
                       'interface Ethernet10\n'
                       '   description test\n'
                       '!\n'
                       'interface Management1\n'
                       '!\n'
                       'no ip routing\n'
                       '!\n'
                       'end\n',
             'warnings': ['Command: show session-configuration named '
                          'capiVerify-2084-9ca297ba6ac411ed9eda020000000000']}],
 'warningCount': 1,
 'warnings': ['! Interface does not exist. The configuration will not take '
              'effect until the module is inserted. at line 1']}
return_validate_ruter_bgp = {'errorCount': 2,
 'errors': [{'error': "> ruter bgp 1111% Invalid input (at token 0: 'ruter') "
                      'at line 1',
             'lineNo': ' 1'},
            {'error': '>    neighbor 1.1.1.1 remote-bs 111% Invalid input (at '
                      "token 1: '1.1.1.1') at line 2",
             'lineNo': ' 2'}],
 'warningCount': 0,
 'warnings': []}
return_validate_config_for_device = {
    'return_validate_true' : return_validate_true,
    'return_validate_intf' : return_validate_intf,
    'return_validate_ruter_bgp' : return_validate_ruter_bgp
}

device_data = [{
    'serialNumber': '0123F2E4462997EB155B7C50EC148767',
    'systemMacAddress': '50:08:00:b1:5b:0b',
    'key': '50:08:00:b1:5b:0b',
    'fqdn': 'tp-avd-leaf2',
    'hostname': 'tp-avd-leaf2',
    'parentContainerName': 'TP_LEAF1',
    'configlets': ['']}] # this is dummy device_data that has no effect

class MockCvpApi():
    def validate_config_for_device(self, device_mac, config):
        if config == validate_ruter_bgp['config']:
            return return_validate_config_for_device['return_validate_ruter_bgp']
        if config == validate_intf['config']:
            return return_validate_config_for_device['return_validate_intf']
        if config == validate_true['config']:
            return return_validate_config_for_device['return_validate_true']

class MockCvpClient():
    def __init__(self):
        self.api = MockCvpApi()


@pytest.mark.generic
class TestValidateConfig():

    # mocking
    def apply_mocks(self, mocker):
        ansible_module = 'ansible_collections.arista.cvp.plugins.module_utils.device_tools.AnsibleModule'
        mock_ansible_module = mocker.patch(ansible_module)
        # __get_configlet_info is name mangled into _CvDeviceTools__get_configlet_info
        get_configlet_info = 'ansible_collections.arista.cvp.plugins.module_utils.device_tools.' \
            'CvDeviceTools._CvDeviceTools__get_configlet_info'
        mock__get_configlet_info = mocker.patch(get_configlet_info)
        return mock_ansible_module, mock__get_configlet_info

    def test_warning_stop_on_warning(self, mocker):
        mock_ansible_module, mock__get_configlet_info = self.apply_mocks(mocker)
        user_topology = DeviceInventory(data=device_data)
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
        cv_tools = CvDeviceTools(MockCvpClient(), mock_ansible_module)
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
