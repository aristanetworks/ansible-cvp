# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
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
