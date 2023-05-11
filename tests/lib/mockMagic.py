from tests.data.device_tools_unit import validate_router_bgp, return_validate_config_for_device, validate_intf, validate_true
from cvprac.cvp_client_errors import CvpApiError

def validate_config_for_device(device_mac, config):
    if config == validate_router_bgp['config']:
        return return_validate_config_for_device['return_validate_ruter_bgp']
    if config == validate_intf['config']:
        return return_validate_config_for_device['return_validate_intf']
    if config == validate_true['config']:
        return return_validate_config_for_device['return_validate_true']

def fail_json(msg, code=1):
    """
    mock method for AnsibleModule fail_json()
    """
    raise SystemExit(code)

def move_device_to_container(app_name, device, container, create_task):

    if container == "InvalidContainer":
        return {'data': {'status': 'failed', 'taskIds': []}}
    else:
        return {'data': {'status': 'success', 'taskIds': []}}
