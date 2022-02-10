from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import traceback
import logging
import random
import string
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
from ansible.module_utils.connection import Connection

try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger('arista.cvp.task_tools')
MODULE_LOGGER.info('Start task_tools module execution')


class CvTagTools():
    """
    CVTagTools Class to manage CloudVision tag related tasks
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module

    def get_serial_num(self, fqdn: str):
        device_details = self.__cv_client.api.get_device_by_name(fqdn)
        if "serialNumber" in device_details.keys():
            return device_details["serialNumber"]
        return " "


    def tasker(self, tags: list, remove: bool = True):
        """
        tasker Generic entry point to manage tag related tasks
        """
        ansible_response = CvAnsibleResponse()
        tag_manager = CvManagerResult(builder_name='actions_manager')

        # ansible_command_timeout = connection.get_option("persistent_command_timeout")
        # ansible_connect_timeout = connection.get_option("persistent_connect_timeout")

        """
        sample tags:
        [
            {
                'device': 'leaf1',
                'device_tags': [
                    {'name': 'test1Tag1', 'value': 'test1Val1'},
                    {'name': 'test1Tag2', 'value': 'test1Val2'}
                ],
                'interface_tags': [
                    {
                        'interface': 'Ethernet1',
                        'tags': [
                            {'name': 'test1Eth1tag1', 'value': 'test1Eth1Val1'},
                            {'name': 'test1Eth1tag2', 'value': 'test1Eth1Val2'}
                        ]
                    },
                    {
                        'interface': 'Ethernet2',
                        'tags': [
                            {'name': 'test1Eth2Tag3', 'value': 'test1Eth2Val3'},
                            {'name': 'test1Eth2Tag4', 'value': 'test1Eth2Val4'}
                        ]
                    }
                ]
            },
            {
                'device': 'leaf2',
                'device_tags': [
                    {'name': 'test1Tag3', 'value': 'test1Val3'},
                    {'name': 'test1Tag4', 'value': 'test1Val4'}
                ]
            }
        ]
        """

        # XXX: REMOVE THIS!!
        # import epdb; epdb.serve(port=8888)

        """
        create WS
        for each device:
            if device tags: for each device tags
                create tag
                assign tag to this device
            if intf tags: for each intf
                create tag
                assign tag to this intf on this device
        start WS build
        check WS build status
        while loop until build status == "BUILD_remove_SUCCESS"
            exit if timeout reached
        submit WS
        check status again??
        """

        # create workspace
        # XXX: cannot reuse the same name every time
        # 1. add a random number to the WS name?

        workspace_name_id = "AnsibleWorkspace"+''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        workspace_id = workspace_name_id
        workspace_name = workspace_name_id
        self.__cv_client.api.workspace_config(workspace_id, workspace_name)

        # create tags and assign tags
        # XXX: DELETE tags?
        for per_device in tags:
            device_name = per_device['device']
            # XXX: get serial number for this device
            device_id = self.get_serial_num(device_name)
            tag_type = per_device.keys()
            if 'device_tags' in tag_type:
                element_type = "ELEMENT_TYPE_DEVICE"
                interface_id = ""
                for dev_tags in per_device['device_tags']:
                    tag_name = dev_tags['name']
                    tag_val = dev_tags['value']
                    self.__cv_client.api.tag_config(element_type, workspace_id,
                                                    tag_name, tag_val,
                                                    remove=remove)
                    self.__cv_client.api.tag_assignment_config(element_type,
                                                               workspace_id,
                                                               tag_name,
                                                               tag_val,
                                                               device_id,
                                                               interface_id,
                                                               remove=remove)
            if 'interface_tags' in tag_type:
                element_type = "ELEMENT_TYPE_INTERFACE"
                for intf_tags in per_device['interface_tags']:
                    interface_id = intf_tags['interface']
                    for tag in intf_tags['tags']:
                        tag_name = tag['name']
                        tag_val = tag['value']
                        self.__cv_client.api.tag_config(element_type,
                                                        workspace_id,
                                                        tag_name, tag_val,
                                                        remove=remove)
                        self.__cv_client.api.tag_assignment_config(element_type,
                                                                   workspace_id,
                                                                   tag_name, tag_val,
                                                                   device_id, interface_id,
                                                                   remove=remove)

        ### Start build
        request = 'REQUEST_START_BUILD'
        reques_id = 'b1'
        description = 'testing cvprac build'
        self.__cv_client.api.workspace_config(workspace_id=workspace_id,
                                              display_name=workspace_name,
                                              description=description, request=request,
                                              request_id=reques_id)

        ### Check workspace build status and proceed only after it finishes building
        # XXX: timeout? ansible timeout!
        b = 0
        while b == 0:
            build_id = reques_id
            try:
                request = self.__cv_client.api.workspace_build_status(workspace_id,
                                                                      build_id)
            except CvpRequestError:
                continue
            if request['value']['state'] == 'BUILD_STATE_SUCCESS':
                b = b+1
            else:
                continue

        api_result = CvApiResult(action_name='tag_'+str(workspace_id))
        api_result.changed = True
        api_result.success = True

        ### Submit workspace
        # XXX: timeout=2-3sec!! send status back to user to check status on cvp side
        request = 'REQUEST_SUBMIT'
        request_id = 's1'
        self.__cv_client.api.workspace_config(workspace_id=workspace_id,
                                              display_name=workspace_name,
                                              description=description,
                                              request=request,
                                              request_id=request_id)

        tag_manager.add_change(api_result)
        ansible_response.add_manager(tag_manager)
        return ansible_response
