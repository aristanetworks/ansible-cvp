from tests.data.device_tools_unit import validate_router_bgp, return_validate_config_for_device, validate_intf, validate_true

def validate_config_for_device(device_mac, config):
    if config == validate_router_bgp['config']:
        return return_validate_config_for_device['return_validate_ruter_bgp']
    if config == validate_intf['config']:
        return return_validate_config_for_device['return_validate_intf']
    if config == validate_true['config']:
        return return_validate_config_for_device['return_validate_true']
