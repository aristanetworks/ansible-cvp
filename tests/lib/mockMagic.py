from tests.data.device_tools_unit import validate_router_bgp, return_validate_config_for_device, validate_intf, validate_true, device_data, image_bundle


def validate_config_for_device(device_mac, config):
    if config == validate_router_bgp['config']:
        return return_validate_config_for_device['return_validate_ruter_bgp']
    if config == validate_intf['config']:
        return return_validate_config_for_device['return_validate_intf']
    if config == validate_true['config']:
        return return_validate_config_for_device['return_validate_true']


def get_image_bundle_by_name(self, name):
    """
    mock to get image_bundle
    """
    if device_data[0]['imageBundle'] != 'Invalid_bundle_name':
        return image_bundle
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


def fail_json(msg, code=1):
    """
    mock method for AnsibleModule fail_json()
    """
    raise SystemExit(code)
