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
EXP_WARN_ERROR_IGNORE = {'changed': True,
 'configlets_validated': {'changed': True,
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
EXP_ERROR_IGNORE = {'changed': True,
 'configlets_validated': {'changed': True,
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
    'diff': None,
    'validate_test_true_on_tp-avd-leaf2_validated_count': 1,
    'validate_test_true_on_tp-avd-leaf2_validated_list': ['validate_test_true_validated_against_tp-avd-leaf2']
}

# mock data from CVP version 2022.1.1
device_data = [{
    'serialNumber': '0123F2E4462997EB155B7C50EC148767',
    'systemMacAddress': '50:08:00:b1:5b:0b',
    'key': '50:08:00:b1:5b:0b',
    'fqdn': 'tp-avd-leaf2',
    'hostname': 'tp-avd-leaf2',
    'parentContainerName': 'TP_LEAF1',
    'parentContainerId': 'TP_LEAF1',
    'configlets': [''],
    'imageBundle': 'EOS-4.25.4M',
}]  # this is dummy device_data that has no effect

device_data_invalid = [{
    'serialNumber': '0123F2E4462997EB155B7C50EC148768', # wrong serial number
    'systemMacAddress': '50:08:00:b1:5b:0a',  # wrong mac address
    'key': '50:08:00:b1:5b:0b',
    'fqdn': 'tp-avd-leaf2',
    'hostname': 'tp-avd-leaf2',
    'parentContainerName': 'Undefined',  # undefined parent container name
    'parentContainerId': 'Undefined',  # undefined parent container id
    'configlets': ['']}]

current_container_info = {
    'name': 'TP_LEAF1',
    'key': 'container_208aadc9-ecc0-4970-b524-6712a0baaade'
}

cv_data = {
     'modelName': '',
     'internalVersion': '4.28.1F',
     'systemMacAddress': '50:08:00:b1:5b:0b',
     'serialNumber': '0123F2E4462997EB155B7C50EC148767',
     'memTotal': 0,
     'bootupTimeStamp': 0.0,
     'memFree': 0,
     'version': '4.28.1F',
     'architecture': '',
     'internalBuildId': '',
     'hardwareRevision': '',
     'fqdn': 'tp-avd-leaf2',
     'key': '50:08:00:b1:5b:0b',
     'ztpMode': 'false',
     'type': 'netelement',
     'ipAddress': '192.168.0.12',
     'taskIdList': [],
     'isDANZEnabled': 'no',
     'isMLAGEnabled': 'no',
     'complianceIndication': 'WARNING',
     'tempAction': [],
     'complianceCode': '0010',
     'lastSyncUp': 0,
     'unAuthorized': False,
     'deviceInfo': None,
     'deviceStatus': 'Registered',
     'parentContainerId': 'container_7f14f7ee-4c3a-4c17-9101-4b6b2e1a3c68',
     'sslEnabledByCVP': False,
     'sslConfigAvailable': False,
     'dcaKey': '',
     'containerName': 'ATD_SPINES',
     'streamingStatus': 'active',
     'status': 'Registered',
     'mlagEnabled': 'no',
     'danzEnabled': 'no',
     'parentContainerKey': 'container_7f14f7ee-4c3a-4c17-9101-4b6b2e1a3c68',
     'bootupTimestamp': 0.0,
     'internalBuild': '',
     'imageBundle': {
        'macAddress': '00:1c:73:f1:7b:f6',
        'serialNumber': '7F75B66299C7E195ECC5DAA490511D47',
        'eosVersion': '4.28.1F',
        'fqdn': 'leaf4.atd.lab',
        'imageBundleMapper': {
            'imagebundle_1658329041200536707': {
                'name': '',
                'id': '00:1c:73:b8:26:81',
                'type': 'netelement'}
        },
        'ipAddress': '192.168.0.15',
        'bundleName': 'EOS-4.26.4M',
        'imageBundleId': 'imagebundle_1658329041200536707'
    }
}

# image_bundle returned by api call
image_bundle = {
    'id': 'imagebundle_1658329041200536707',
    'name': 'EOS-4.25.4M',
    'isCertifiedImage': 'true',
    'updatedTimeInLongFormat': 1658329041200,
    'appliedContainersCount': 1,
    'appliedDevicesCount': 1,
    'uploadedBy': 'cvp system',
    'images': [{'name': 'EOS-4.25.4M.swi',
                'sha512': '54e6874984a3a46b1371bd6c53196bbd622c922606b65d59ed3fa23e918a43d174d468ac9179146a4d1b00e7094c4755ea90c2df4ab94c562e745c14a402b491',
                'swiVarient': 'US',
                'imageSize': '931.9 MB',
                'version': '4.25.4M-22402993.4254M',
                'swiMaxHwepoch': '2',
                'isRebootRequired': 'true',
                'user': 'cvp system',
                'uploadedDateinLongFormat': 1658329024667,
                'isHotFix': 'false',
                'imageBundleKeys': ['imagebundle_1658329041200536707'],
                'key': 'EOS-4.25.4M.swi',
                'imageId': 'EOS-4.25.4M.swi',
                'imageFileName': 'EOS-4.25.4M.swi',
                'md5': '',
                'imageFile': ''},
               ]
}

