<<<<<<< HEAD
<<<<<<< HEAD
from tests.data.device_tools_unit import (validate_router_bgp, return_validate_config_for_device, validate_intf, validate_true, device_data)
from unittest.mock import MagicMock
from cvprac.cvp_client_errors import CvpApiError
=======
from unittest.mock import create_autospec
from tests.data.device_tools_unit import device_data
from cvprac.cvp_client import CvpClient, CvpApi
>>>>>>> 7ca03e5 (Added docstrings and update code)
=======
from tests.data.device_tools_unit import device_data
>>>>>>> 384f2ed (Restructured pytest)

class MockCvpApi(MagicMock):
    def validate_config_for_device(self, device_mac, config):
        if config == validate_router_bgp['config']:
            return return_validate_config_for_device['return_validate_ruter_bgp']
        if config == validate_intf['config']:
            return return_validate_config_for_device['return_validate_intf']
        if config == validate_true['config']:
            return return_validate_config_for_device['return_validate_true']

    def device_decommissioning(self, device_id, request_id):
<<<<<<< HEAD
<<<<<<< HEAD
        """
        mock method for cvprac device_decommissioning()
        """
=======
        # TODO: need to check cvp_api.get_device_by_serial output for device_info
>>>>>>> 7ca03e5 (Added docstrings and update code)
=======
>>>>>>> 59617e4 (Class arrangement)
        if device_id == device_data[0]["serialNumber"]:
            self.result = {'value': {'key': {'requestId': request_id},
                                     'deviceId': device_id},
                           'time': '2022-02-12T02:58:30.765459650Z'}
        else:
            self.result = None

    def device_decommissioning_status_get_one(self, request_id):
        """
        mock method for cvprac device_decommissioning_status_get_one()
        """
        if self.result and self.result["value"]["key"]["requestId"]:
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

    def reset_device(self, app_name, device, create_task=True):
        """
        mock method for cvprac reset_device()
        """
        if 'parentContainerId' in device:
            from_id = device['parentContainerId']
        else:
<<<<<<< HEAD
            if device['parentContainerName']:
                from_id = device['parentContainerName']
            else:
                from_id = ''

        if create_task:
            if from_id and from_id == "Undefined":
                return {'data': {'status': 'fail', 'taskIds': []}}
            elif from_id and from_id != "Undefined":
                return {'data': {'taskIds': ['57'], 'status': 'success'}}
            else:
                raise CvpApiError(msg="Error resetting device")
=======
            if device['parentContainerName'] == "undefined":
                parent_cont = {'key': 'undefined'}  # need to check this data from CVP instace
            else:
                parent_cont = {'key': device['parentContainerName']}  # need to check this data from CVP instance

            from_id = parent_cont['key']

        if create_task:
            if from_id == "undefined":
                return {'data': {'status': 'fail', 'taskIds': []}}
            else:
                return {'data': {'taskIds': ['57'], 'status': 'success'}}
>>>>>>> 59617e4 (Class arrangement)
        else:
            return None

        #TODO: need to write testcase - if create_task returns None, raised issue #585 in ansible-cvp

    def delete_device(self, device_mac):
<<<<<<< HEAD
        """
        mock method for cvprac delete_device()
        """
        device_info = {}
        if not device_mac:
            raise CvpApiError(msg='Error removing device from provisioning')
=======
        device_macs = [device_mac]
        device_info = {}
        for dev_mac in device_macs:
            if dev_mac == device_data[0]['systemMacAddress']:
                device_info = device_data[0]

        if device_info is not None and 'serialNumber' in device_info:
<<<<<<< HEAD
            return {'result': 'success'}  # need to check this in lab
>>>>>>> 7ca03e5 (Added docstrings and update code)
        else:
<<<<<<< HEAD
            if device_mac == device_data[0]['systemMacAddress']:
                device_info = device_data[0]

            if device_info is not None and 'serialNumber' in device_info:
                return {'result': 'success'}
            else:
                return {'result': 'fail'}

    def fail_json(self, msg, code=1):
        """
        mock method for AnsibleModule fail_json()
        """
        raise SystemExit(code)
=======
            return {'result': 'fail'}  # need to check this in lab
>>>>>>> 384f2ed (Restructured pytest)
=======
            return {'result': 'success'}
        else:
            return {'result': 'fail'}
>>>>>>> 59617e4 (Class arrangement)
