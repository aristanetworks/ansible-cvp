# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from tests.data.device_tools_unit import (image_bundle, device_data)
from tests.data.validate_tools_unit import (validate_router_bgp, return_validate_config_for_device,
                                          validate_warning, validate_true)

device_decommissioning_result = {}


def fail_json(msg, code=1):
    """
    mock method for AnsibleModule fail_json()
    """
    raise SystemExit(code)


def validate_config_for_device(device_mac, config):
    if config == validate_router_bgp['config']:
        return return_validate_config_for_device['return_validate_ruter_bgp']
    if config == validate_warning['config']:
        return return_validate_config_for_device['return_validate_warning']
    if config == validate_true['config']:
        return return_validate_config_for_device['return_validate_true']

def move_device_to_container(app_name, device, container, create_task):

    if container == "InvalidContainer":
        return {'data': {'status': 'failed', 'taskIds': []}}
    else:
        return {'data': {'status': 'success', 'taskIds': []}}

def get_image_bundle_by_name(name):
    """
    mock to get image_bundle
    """
    if name != 'Invalid_bundle_name':
        return image_bundle
    else:
        return None


def apply_image_to_element(image, element, name, id_type,
                           create_task=True):
    """
    mock for apply_image_to_element
    """
    if 'imageBundleKeys' in image_bundle:
        if image_bundle['imageBundleKeys']:
            node_id = image_bundle['imageBundleKeys'][0]

    if 'id' in image_bundle:
        node_id = image_bundle['id']

    if create_task:
        if node_id:
            return {'data': {'taskIds': ['57'], 'status': 'success'}}
        else:
            return {'data': {'taskIds': [], 'status': 'fail'}}
    else:
        return None


def remove_image_from_element(image, element, name, id_type):
    """
    mock for remove_image_from_element
    """
    if 'imageBundleKeys' in image_bundle:
        if image_bundle['imageBundleKeys']:
            node_id = image_bundle['imageBundleKeys'][0]

    if 'id' in image_bundle:
        node_id = image_bundle['id']

    if node_id:
        return {'data': {'taskIds': ['57'], 'status': 'success'}}
    else:
        return {'data': {'taskIds': [], 'status': 'fail'}}


def device_decommissioning(device_id, request_id):
    """
    mock method for cvprac device_decommissioning()
    """
    global device_decommissioning_result
    if device_id and device_id == device_data[0]["serialNumber"]:
        device_decommissioning_result = {'value': {'key': {'requestId': request_id},
                                 'deviceId': device_id},
                       'time': '2022-02-12T02:58:30.765459650Z'}
    else:
        device_decommissioning_result = None


def device_decommissioning_status_get_one(request_id):
    """
    mock method for cvprac device_decommissioning_status_get_one()
    the self.result is set by device_decommissioning when called first
    """
    if device_decommissioning_result:
        resp = {"result": {"value": {"key": {"requestId": request_id},
                                     "status": 'DECOMMISSIONING_STATUS_SUCCESS',
                                     "statusMessage": "Disabled TerminAttr, "
                                                      "waiting for device to be marked inactive"},
                           "time": "2022-02-04T19:41:46.376310308Z", "type": "INITIAL"}}

    else:
        resp = {"result": {"value": {"status": 'DECOMMISSIONING_STATUS_FAILURE',
                                     "error": "Device does not exist or is not registered to decommission"},
                           "time": "2022-02-04T19:41:46.376310308Z", "type": "INITIAL"}}

    return resp["result"]


def reset_device(app_name, device, create_task=True):
    """
    mock method for cvprac reset_device()
    """
    if 'parentContainerId' in device:
        from_id = device['parentContainerId']
    else:
        if device['parentContainerName']:
            from_id = device['parentContainerName']
        else:
            from_id = ''

    if create_task:
        if from_id and from_id != "Undefined":
            return {'data': {'taskIds': ['57'], 'status': 'success'}}
        else:
            return {'data': {'status': 'fail', 'taskIds': []}}
    else:
        return None


def delete_device(device_mac):
    """
    mock method for cvprac delete_device()
    """
    device_info = {}
    if device_mac == device_data[0]['systemMacAddress']:
        device_info = device_data[0]
    if device_info and 'serialNumber' in device_info:
        return {'result': 'success'}
    else:
        return {'result': 'fail'}
