from tests.data.device_tools_unit import (validate_router_bgp, return_validate_config_for_device, validate_intf, validate_true, device_data)

device_decommissioning_result = {}


def fail_json(msg, code=1):
    """
    mock method for AnsibleModule fail_json()
    """
    raise SystemExit(code)


def validate_config_for_device(device_mac, config):
    if config == validate_router_bgp['config']:
        return return_validate_config_for_device['return_validate_ruter_bgp']
    if config == validate_intf['config']:
        return return_validate_config_for_device['return_validate_intf']
    if config == validate_true['config']:
        return return_validate_config_for_device['return_validate_true']


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
