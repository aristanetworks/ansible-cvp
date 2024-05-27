# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# error configlet
validate_router_bgp = {
    "config": "ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111",
    "key": "configlet_3f7f850a-f8e1-4d33-b3cd-e8dd90039a87",
    "name": "validate_ruter_bgp"
}

# warning configlet
validate_warning = {'config': 'interface Ethernet1\n   spanning-tree portfast',
    'key': 'configlet_59279a3b-bbea-4a89-b6c3-bdd759a82722',
    'name': 'validate_intf'}

# true configlet
validate_true = {
    'config': 'interface Ethernet1\n  description test_validate',
    'key': 'configlet_30869fe3-00f2-4c07-988b-ab9df54eb52f',
    'name': 'validate_test_true'}

# return value when input is validate_true
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

# return value when input is validate_intf
return_validate_warning = {'id': 'Arista-3-2526292741976',
 'jsonrpc': '2.0',
 'result': [{'messages': ['Copy completed successfully.'],
             'output': 'enter input line by line; when done enter one or more '
                       'control-d\n'
                       '\n'
                       '>    spanning-tree portfast\n'
                       '! portfast should only be enabled on ports connected '
                       'to a single host. Connecting hubs, concentrators, '
                       'switches, bridges, etc. to this interface when '
                       'portfast is enabled can cause temporary bridging '
                       'loops. Use with CAUTION. at line 2\n'
                       'Copy completed successfully.\n'},
            {'output': '! Command: show session-configuration named '
                       'capiVerify-548-4822d7eef34b11ed8018de0858b316c6\n'
                       '! device: leaf1 (cEOSLab, EOS-4.28.1F-27567444.4281F '
                       '(engineering build))\n'
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
                       '   spanning-tree portfast\n'
                       '!\n'
                       'interface Ethernet2\n'
                       '!\n'
                       'interface Ethernet3\n'
                       '!\n'
                       'interface Ethernet4\n'
                       '!\n'
                       'interface Ethernet5\n'
                       '!\n'
                       'interface Ethernet6\n'
                       '!\n'
                       'interface Management0\n'
                       '!\n'
                       'no ip routing\n'
                       '!\n'
                       'end\n',
             'warnings': ['Command: show session-configuration named '
                          'capiVerify-548-4822d7eef34b11ed8018de0858b316c6']}],
 'warningCount': 1,
 'warnings': ['! portfast should only be enabled on ports connected to a '
              'single host. Connecting hubs, concentrators, switches, bridges, '
              'etc. to this interface when portfast is enabled can cause '
              'temporary bridging loops. Use with CAUTION. at line 2']}

# return value when input is validate_ruter_bgp
return_validate_ruter_bgp = {'errorCount': 2,
 'errors': [{'error': "> ruter bgp 1111% Invalid input (at token 0: 'ruter') "
                      'at line 1',
             'lineNo': ' 1'},
            {'error': '>    neighbor 1.1.1.1 remote-bs 111% Invalid input (at '
                      "token 1: '1.1.1.1') at line 2",
             'lineNo': ' 2'}],
 'warningCount': 0,
 'warnings': []}

# validate_config_for_device() i/p to o/p matrix
return_validate_config_for_device = {
    'return_validate_true' : return_validate_true,
    'return_validate_warning' : return_validate_warning,
    'return_validate_ruter_bgp' : return_validate_ruter_bgp
}

# expected warning output
EXP_WARN = {'configlets_validated_count': 1,
    'configlets_validated_list': ['validate_warning_on_leaf1_validated'],
    'diff': {},
    'errors': [],
    'success': True,
    'taskIds': [],
    'warnings': [{'configlet_name': 'validate_warning',
                    'device': 'leaf1',
                    'warnings': ['! portfast should only be enabled on ports '
                                'connected to a single host. Connecting hubs, '
                                'concentrators, switches, bridges, etc. to this '
                                'interface when portfast is enabled can cause '
                                'temporary bridging loops. Use with CAUTION. at '
                                'line 2']}]}

# expected output for warning and error configlet for validate_mode=ignore
EXP_WARN_ERROR_IGNORE = {'changed': False,
 'configlets_validated': {'changed': False,
                          'configlets_validated_count': 1,
                          'configlets_validated_list': ['validate_warning_on_serialNumber_validated'],
                          'diff': {},
                          'errors': [],
                          'success': True,
                          'taskIds': [],
                          'warnings': [{'configlet_name': 'validate_warning',
                                        'device': 'leaf1',
                                        'warnings': ['! portfast should only '
                                                     'be enabled on ports '
                                                     'connected to a single '
                                                     'host. Connecting hubs, '
                                                     'concentrators, switches, '
                                                     'bridges, etc. to this '
                                                     'interface when portfast '
                                                     'is enabled can cause '
                                                     'temporary bridging '
                                                     'loops. Use with CAUTION. '
                                                     'at line 2']}]},
 'success': True,
 'taskIds': []}

# expected output for error configlet for validate_mode=ignore
EXP_ERROR_IGNORE = {'changed': False,
 'configlets_validated': {'changed': False,
                          'configlets_validated_count': 1,
                          'configlets_validated_list': ['validate_error_on_serialNumber_validated'],
                          'diff': {},
                          'errors': [{'configlet_name': 'validate_error',
                                      'device': 'leaf1',
                                      'errors': [{'error': '> ruter bgp 1111% '
                                                           'Invalid input (at '
                                                           "token 0: 'ruter') "
                                                           'at line 1',
                                                  'lineNo': ' 1'},
                                                 {'error': '>    neighbor '
                                                           '1.1.1.1 remote-bs '
                                                           '111% Invalid input '
                                                           '(at token 1: '
                                                           "'1.1.1.1') at line "
                                                           '2',
                                                  'lineNo': ' 2'}]}],
                          'success': True,
                          'taskIds': [],
                          'warnings': []},
 'success': True,
 'taskIds': []}


# expected output for error configlet for validate_mode=stop_on_warning/stop_on_error
EXP_ERROR = {'configlets_validated_count': 1,
    'configlets_validated_list': ['validate_error_on_leaf1_validated'],
    'diff': {},
    'errors': [{'configlet_name': 'validate_error',
                'device': 'leaf1',
                'errors': [{'error': '> ruter bgp 1111% Invalid input (at token '
                                    "0: 'ruter') at line 1",
                            'lineNo': ' 1'},
                            {'error': '>    neighbor 1.1.1.1 remote-bs 111% '
                                    "Invalid input (at token 1: '1.1.1.1') at "
                                    'line 2',
                            'lineNo': ' 2'}]}],
    'success': True,
    'taskIds': [],
    'warnings': []}

# expected output for valid configlet for validate_mode=ignore|stop_on_warning|stop_on_eror
EXP_VALID = {'changed': False,
 'configlets_validated': {'changed': False,
                          'configlets_validated_count': 1,
                          'configlets_validated_list': ['validate_valid_on_serialNumber_validated'],
                          'diff': {},
                          'errors': [],
                          'success': True,
                          'taskIds': [],
                          'warnings': []},
'success': True,
'taskIds': []}
