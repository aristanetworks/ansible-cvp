# error configlet
validate_router_bgp = {
    "config": "ruter bgp 1111\n   neighbor 1.1.1.1 remote-bs 111",
    "containerCount": 0,
    "dateTimeInLongFormat": 1668634708856,
    "editable": True,
    "isAutoBuilder": "",
    "isDefault": "no",
    "isDraft": False,
    "key": "configlet_3f7f850a-f8e1-4d33-b3cd-e8dd90039a87",
    "name": "validate_ruter_bgp",
    "netElementCount": 0,
    "note": "",
    "reconciled": False,
    "sslConfig": False,
    "type": "Static",
    "typeStudioConfiglet": False,
    "user": "cvpadmin",
    "visible": True,
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
    'return_validate_intf' : return_validate_intf,
    'return_validate_ruter_bgp' : return_validate_ruter_bgp
}

# expected warning output
EXP_WARN = {
    'warnings': [
        {'device': 'tp-avd-leaf2',
        'warnings': ['! Interface does not exist. The configuration will not take effect until the module is inserted. at line 1']
        }],
    'errors': [],
    'configlets_validated_count': 1,
    'configlets_validated_list': ['_on_tp-avd-leaf2_validated'],
    'diff': {},
    'success': True,
    'taskIds': []
}

# expected output for mode:ignore and warning configlet
EXP_WARN_IGNORE = {
    'success': True,
    'changed': True,
    'taskIds': [],
    'diff': None,
    'validate_intf_on_tp-avd-leaf2_validated_count': 1,
    'validate_intf_on_tp-avd-leaf2_validated_list': ['validate_intf_validated_against_tp-avd-leaf2']
}

# expected error output
EXP_ERROR = {
    'warnings': [],
    'errors': [
        {'device': 'tp-avd-leaf2',
        'errors': [
            {'error': "> ruter bgp 1111% Invalid input (at token 0: 'ruter') at line 1", 'lineNo': ' 1'},
            {'error': ">    neighbor 1.1.1.1 remote-bs 111% Invalid input (at token 1: '1.1.1.1') at line 2", 'lineNo': ' 2'}
        ]}
    ],
    'configlets_validated_count': 1,
    'configlets_validated_list': ['_on_tp-avd-leaf2_validated'],
    'diff': {},
    'success': True,
    'taskIds': []
}

# expected valid output
EXP_VALID = {
    'success': True,
    'changed': True,
    'taskIds': [],
    'diff': None,
    'validate_test_true_on_tp-avd-leaf2_validated_count': 1,
    'validate_test_true_on_tp-avd-leaf2_validated_list': ['validate_test_true_validated_against_tp-avd-leaf2']
}

# mock device data
device_data = [{
    'serialNumber': '0123F2E4462997EB155B7C50EC148767',
    'systemMacAddress': '50:08:00:b1:5b:0b',
    'key': '50:08:00:b1:5b:0b',
    'fqdn': 'tp-avd-leaf2',
    'hostname': 'tp-avd-leaf2',
    'parentContainerName': 'TP_LEAF1',
    'parentContainerId': 'TP_LEAF1',
<<<<<<< HEAD
    'configlets': [''],
    'imageBundle': 'EOS-4.25.4M',
}]  # this is dummy device_data that has no effect
=======
    'configlets': ['']}]  # this is dummy device_data that has no effect
>>>>>>> c035398 (Added unittests for CvpApiError)

device_data_invalid = [{
    'serialNumber': '0123F2E4462997EB155B7C50EC148768', # wrong serial number
    'systemMacAddress': '50:08:00:b1:5b:0a',  # wrong mac address
    'key': '50:08:00:b1:5b:0b',
    'fqdn': 'tp-avd-leaf2',
    'hostname': 'tp-avd-leaf2',
<<<<<<< HEAD
    'parentContainerName': 'Undefined',  # undefined parent container name
=======
    'parentContainerName': 'Undefined',
>>>>>>> c035398 (Added unittests for CvpApiError)
    'parentContainerId': 'Undefined',  # undefined parent container id
    'configlets': ['']}]
<<<<<<< HEAD
<<<<<<< HEAD
=======


>>>>>>> 7ca03e5 (Added docstrings and update code)
=======
>>>>>>> 384f2ed (Restructured pytest)
