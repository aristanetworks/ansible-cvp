from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import traceback
import logging
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
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

    def getSerialNum(self, fqdn: str):
        device_details = self.__cv_client.api.get_device_by_name(fqdn)
        if "serialNumber" in device_details.keys():
            return device_details["serialNumber"]
        return " "


    def tasker(self, tags: list):
        """
        tasker Generic entry point to manage tag related tasks
        """
        ansible_response = CvAnsibleResponse()
        tag_manager = CvManagerResult(builder_name='actions_manager')

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
        while loop until build status == "BUILD_STATE_SUCCESS"
            exit if timeout reached
        submit WS
        check status again??
        """

        # create workspace
        # XXX: cannot reuse the same name every time
        # 1. add a random number to the WS name?
        workspaceId = "XXAnsibleWorkspace5XX"
        workspaceName = "XXAnsibleWorkspace5XX"
        self.__cv_client.api.workspace_config(workspaceId, workspaceName)

        # create tags and assign tags
        # XXX: DELETE tags?
        for perDevice in tags:
            deviceName = perDevice['device']
            # XXX: get serial number for this device
            deviceId = self.getSerialNum(deviceName)
            tagtype = perDevice.keys()
            if 'device_tags' in tagtype:
                elementType = "ELEMENT_TYPE_DEVICE"
                interfaceId = ""
                for devTags in perDevice['device_tags']:
                    tagName = devTags['name']
                    tagVal = devTags['value']
                    self.__cv_client.api.tag_config(elementType, workspaceId,
                                                    tagName, tagVal)
                    self.__cv_client.api.tag_assignment_config(elementType,
                                                               workspaceId,
                                                               tagName,
                                                               tagVal,
                                                               deviceId,
                                                               interfaceId)
            if 'interface_tags' in tagtype:
                elementType = "ELEMENT_TYPE_INTERFACE"
                for intfTags in perDevice['interface_tags']:
                    interfaceId = intfTags['interface']
                    for tag in intfTags['tags']:
                        tagName = tag['name']
                        tagVal = tag['value']
                        self.__cv_client.api.tag_config(elementType,
                                                        workspaceId,
                                                        tagName, tagVal)
                        self.__cv_client.api.tag_assignment_config(elementType,
                                                                   workspaceId,
                                                                   tagName, tagVal,
                                                                   deviceId, interfaceId)

        ### Start build
        request = 'REQUEST_START_BUILD'
        requestId = 'b1'
        description = 'testing cvprac build'
        self.__cv_client.api.workspace_config(workspace_id=workspaceId,
                                              display_name=workspaceName,
                                              description=description, request=request,
                                              request_id=requestId)

        ### Check workspace build status and proceed only after it finishes building
        # XXX: timeout? ansible timeout!
        b = 0
        while b == 0:
            buildId = requestId
            try:
                request = self.__cv_client.api.workspace_build_status(workspaceId,
                                                                      buildId)
            except CvpRequestError:
                continue
            if request['value']['state'] == 'BUILD_STATE_SUCCESS':
                b = b+1
            else:
                continue

        api_result = CvApiResult(action_name='tag_'+str(workspaceId))
        api_result.changed = True
        api_result.success = True

        ### Submit workspace
        # XXX: timeout=2-3sec!! send status back to user to check status on cvp side
        request = 'REQUEST_SUBMIT'
        requestId = 's1'
        self.__cv_client.api.workspace_config(workspace_id=workspaceId,
            display_name=workspaceName, description=description,
            request=request, request_id=requestId)

        tag_manager.add_change(api_result)
        ansible_response.add_manager(tag_manager)
        return ansible_response
