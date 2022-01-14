#!/usr/bin/python
# coding: utf-8 -*-

from unittest.mock import MagicMock, create_autospec
import pprint
import logging
from cvprac.cvp_client import CvpClient, CvpApi
from ansible.module_utils.basic import AnsibleModule

LOGGER = logging.getLogger(__name__)


class CvpNotFoundError(Exception):
    """Exception class to be raised when data is not found in mock CVP database"""
    pass


class MockCVPDatabase:
    """Class to mock CVP database being modified during tests"""

    # Fields in API data
    FIELD_COUNT_DEVICES = 'childNetElementCount'
    FIELD_COUNT_CONTAINERS = 'childContainerCount'
    FIELD_PARENT_ID = 'parentContainerId'
    FIELD_NAME = 'name'
    FIELD_KEY = 'key'
    FIELD_TOPOLOGY = 'topology'

    # Fields in mock database
    FIELD_CONTAINER_ATTACHED = 'containerAttached'

    # Data used in mock methods
    CONTAINER_KEY = 'container_1234abcd-1234-abcd-12ab-123456abcdef'

    # Data used to initiate the mock database
    CVP_DATA_CONTAINERS_INIT = {
        "Tenant": {
            "key": "root",
            "name": "Tenant",
            "createdBy": "cvp system",
            "createdOn": 1620698150131,
            "mode": "expand"
        },
        "Undefined":{
            "key": "undefined_container",
            "name": "Undefined",
            "createdBy": "cvp system",
            "createdOn": 1620698150262,
            "mode": "expand"
        },
        "ansible-tests": {
            "key": "container_41eeb2a0-f3a2-46a5-ad19-4c37226138ba",
            "name": "ansible-tests",
            "createdBy": "konika.chaurasiya",
            "createdOn": 1640612980169,
            "mode": "expand"
        },
        "CVPRAC_ConfCont_TEST": {
            "key": "container_5230d9c2-e1df-4708-98e0-52122c6b3bd1",
            "name": "CVPRAC_ConfCont_TEST",
            "createdBy": "cvpadmin",
            "createdOn": 1641986183577,
            "mode": "expand"
        },
        "CVPRACTEST": {
            "key": "container_5a885aa1-21d8-4aa0-8115-d8aed0fa99e8",
            "name": "CVPRACTEST",
            "createdBy": "cvpadmin",
            "createdOn": 1641986191996,
            "mode": "expand"
        }
    }

    CVP_DATA_CONFIGLETS_MAPPERS_INIT = {
        "data": {
            "configlets": [
                {
                    "key": "configlet_0b5f1972-bb04-4d31-931d-baf7061caa13",
                    "name": "spine-2-unit-test",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "cvpadmin",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1640858616983,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_214adb74-6b6f-4300-b97b-973a2f56fde6",
                    "name": "AVD_DC1-SPINE2",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825216848,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_8776af60-cb0d-464a-bbea-bd5d1a61b05e",
                    "name": "AVD_DC1-BL1A",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825218329,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_02ba3a16-85ec-4a33-abfc-3946cb809acd",
                    "name": "AVD_DC1-L2LEAF1A",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825220513,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_00a60642-c1d8-47d4-b579-0c1b828dc350",
                    "name": "system-configlet-tests02",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "gigi-api-test",
                    "note": "Updated by pytest - 01/05/2022, 14:40:22.825578",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1641393624491,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_f594f11d-b847-42d3-8190-b579226b8a52",
                    "name": "AVD_DC1-SVC3A",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825219789,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_31a9330c-0199-4779-9ad3-476d0ae69adc",
                    "name": "leaf-2-unit-test",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "cvpadmin",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1640777487575,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_a1c76e8b-fbb3-4623-9850-c8b45b68a5b6",
                    "name": "test_configlet",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "cvpadmin",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1641986660419,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_30c0a882-ea12-4fd1-bec2-2721b7884229",
                    "name": "AVD_DC1-BL1B",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825221205,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_a830b64b-6af5-4935-b79f-86a70fa02703",
                    "name": "AVD_DC1-SVC3B",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825211705,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_206fee79-c304-470b-b758-19b4f3ebe672",
                    "name": "spine-1-unit-test",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "cvpadmin",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1640858241678,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_4e4caa60-ebc1-439e-94bc-ec9856853258",
                    "name": "AVD_DC1-LEAF1A",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825219057,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_21b1f772-b84b-40d4-af59-af44e1305307",
                    "name": "system-configlet-tests01",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "gigi-api-test",
                    "note": "Updated by pytest - 01/05/2022, 14:40:22.825578",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1641393623762,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_42bf5617-803e-4156-a018-7f9134c7dd65",
                    "name": "AVD_DC1-LEAF2A",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825212718,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_8f2f3722-ca21-4e96-8b1b-21108ce9dbd1",
                    "name": "AVD_DC1-SPINE4",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825217629,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_b7afbd9e-a474-4a83-b199-473b4cb4be70",
                    "name": "leaf-1-unit-test",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "cvpadmin",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1641360608681,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "SYS_TelemetryBuilderV2_1620698150484",
                    "name": "SYS_TelemetryBuilderV2",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "cvp system",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1620698150484,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Builder",
                    "editable": "false",
                    "sslConfig": "false",
                    "visible": "false",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_15f965c5-3928-4ac5-bacc-d252e3d45d36",
                    "name": "AVD_DC1-SPINE3",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825214901,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_b7ab6e9b-4794-4dee-a85b-f9205ae2451f",
                    "name": "AVD_DC1-L2LEAF2A",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825210851,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_7a0026f5-76e7-4885-875a-c8402835e0ea",
                    "name": "test_device_configlet",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "cvpadmin",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1641897119804,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_15e30e30-1450-492c-bebc-0fc607df6377",
                    "name": "cvaas-unit-test-02",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "tgrimonet",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1634117725635,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_244170a4-a460-4c68-b1de-646e94ff8a42",
                    "name": "AVD_DC1-SPINE1",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825214128,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_020f0e7d-1c35-49f4-a889-7ba7c705ab4a",
                    "name": "AVD_DC1-LEAF2B",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825215901,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_c49ba47e-a077-44e2-95ce-8484f3f25f5f",
                    "name": "container-configlet-1",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "guillaume.vilar",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1638541658184,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_58d95e33-b646-4c14-8f2d-f0c16197193d",
                    "name": "cvaas-unit-test-01",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "tgrimonet",
                    "note": "",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1634116019441,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                },
                {
                    "key": "configlet_5ad217e6-4eb9-4fd7-97d9-32ad39275635",
                    "name": "AVD_DC1-L2LEAF2B",
                    "reconciled": "false",
                    "configl": "alias mock show ip route",
                    "user": "github-ci-ansible-avd",
                    "note": "Managed by Ansible",
                    "containerCount": 0,
                    "netElementCount": 0,
                    "dateTimeInLongFormat": 1637825213443,
                    "isDefault": "no",
                    "isAutoBuilder": "",
                    "type": "Static",
                    "editable": "true",
                    "sslConfig": "false",
                    "visible": "true",
                    "isDraft": "false",
                    "typeStudioConfiglet": "false"
                }
            ],
            "configletBuilders":
            [
                {
                    "key": "SYS_TelemetryBuilderV2_1620698150484",
                    "configletBuilderId": "SYS_TelemetryBuilderV2_1620698150484",
                    "formList":
                        [
                            {
                                "fieldId": "vrf",
                                "fieldLabel": "Management VRF",
                                "type": "Text box",
                                "value": "default",
                                "depends": "",
                                "validation":
                                    {
                                        "mandatory": "false"
                                    },
                                "dataValidation": "",
                                "helpText": "VRF on which to stream telemetry data to CloudVision",
                                "configletBuilderId": "SYS_TelemetryBuilderV2_1620698150484",
                                "orderId": 0,
                                "key": "SYS_TelemetryBuilderV2_1620698150604",
                                "dataValidationErrorExist": "false",
                                "previewValue": ""
                            }
                        ],
                    "mainScript":
                        {
                            "data": "",
                            "sessionId": ""
                        },
                    "draft": "false"
                }
            ],
            "generatedConfigletMappers": [],
            "configletMappers": [
                {
                    "key": "configletMapper_8025a582-f648-465f-a0a5-e50f4bd832be",
                    "configletId": "configlet_a1c76e8b-fbb3-4623-9850-c8b45b68a5b6",
                    "type": "container",
                    "objectId": "container_41eeb2a0-f3a2-46a5-ad19-4c37226138ba",
                    "containerId": "",
                    "appliedBy": "cvpadmin",
                    "configletType": "Static",
                    "appliedDateInLongFormat": 1640858175937,
                    "isDraft": "false",
                    "deviceId": ""
                },
                {
                    "key": "configletMapper_a102df0f-f8e4-4902-a5a7-f74e663ca604",
                    "configletId": "configlet_a1c76e8b-fbb3-4623-9850-c8b45b68a5b6",
                    "type": "netelement",
                    "objectId": "50:00:00:03:37:66",
                    "containerId": "container_41eeb2a0-f3a2-46a5-ad19-4c37226138ba",
                    "appliedBy": "konika.chaurasiya",
                    "configletType": "Static",
                    "appliedDateInLongFormat": 1641795883888,
                    "isDraft": "false",
                    "deviceId": "24666013EF2271599935B4A894F356E1"
                },
                {
                    "key": "configletMapper_82d094fb-a591-4c4e-901c-42845f2732a9",
                    "configletId": "configlet_58d95e33-b646-4c14-8f2d-f0c16197193d",
                    "type": "netelement",
                    "objectId": "50:00:00:d5:5d:c0",
                    "containerId": "",
                    "appliedBy": "gigi-api-test",
                    "configletType": "Static",
                    "appliedDateInLongFormat": 1641393717170,
                    "isDraft": "false",
                    "deviceId": "A2BC886CB9408A0453A3CFDD9C251999"
                },
                {
                    "key": "configletMapper_fe2750f9-0c44-4ccd-8187-c8eb5ea78095",
                    "configletId": "configlet_b7afbd9e-a474-4a83-b199-473b4cb4be70",
                    "type": "netelement",
                    "objectId": "50:00:00:d5:5d:c0",
                    "containerId": "",
                    "appliedBy": "gigi-api-test",
                    "configletType": "Static",
                    "appliedDateInLongFormat": 1641393716965,
                    "isDraft": "false",
                    "deviceId": "A2BC886CB9408A0453A3CFDD9C251999"
                },
                {
                    "key": "configletMapper_784f0623-9293-4bdd-9c02-c5111e613cbf",
                    "configletId": "configlet_31a9330c-0199-4779-9ad3-476d0ae69adc",
                    "type": "netelement",
                    "objectId": "50:00:00:d5:5d:c0",
                    "containerId": "",
                    "appliedBy": "gigi-api-test",
                    "configletType": "Static",
                    "appliedDateInLongFormat": 1641393717068,
                    "isDraft": "false",
                    "deviceId": "A2BC886CB9408A0453A3CFDD9C251999"
                },
                {
                    "key": "configletMapper_ab27a641-2583-44d2-9103-a981213bfec7",
                    "configletId": "configlet_7a0026f5-76e7-4885-875a-c8402835e0ea",
                    "type": "netelement",
                    "objectId": "50:00:00:d5:5d:c0",
                    "containerId": "",
                    "appliedBy": "gigi-api-test",
                    "configletType": "Static",
                    "appliedDateInLongFormat": 1641393716871,
                    "isDraft": "false",
                    "deviceId": "A2BC886CB9408A0453A3CFDD9C251999"
                },
                {
                    "key": "configletMapper_98bbb61a-c5f4-45be-bb98-5a146e325302",
                    "configletId": "configlet_a1c76e8b-fbb3-4623-9850-c8b45b68a5b6",
                    "type": "netelement",
                    "objectId": "50:00:00:d5:5d:c0",
                    "containerId": "container_41eeb2a0-f3a2-46a5-ad19-4c37226138ba",
                    "appliedBy": "cvpadmin",
                    "configletType": "Static",
                    "appliedDateInLongFormat": 1641895623109,
                    "isDraft": "false",
                    "deviceId": "A2BC886CB9408A0453A3CFDD9C251999"
                }
            ]
        }
    }

    CVP_DATA_CONFIGLET_INIT = CVP_DATA_CONFIGLETS_MAPPERS_INIT['data']['configlets']

    def __init__(self, devices: dict = None, containers: dict = None, configlets: dict = None, configlets_mappers: dict = None):
        self.devices = devices if devices is not None else {}
        self.containers = containers if containers is not None else MockCVPDatabase.CVP_DATA_CONTAINERS_INIT.copy()
        self.configlets = configlets if configlets is not None else MockCVPDatabase.CVP_DATA_CONFIGLET_INIT.copy()
        self.configlets_mappers = configlets_mappers if configlets_mappers is not None else MockCVPDatabase.CVP_DATA_CONFIGLETS_MAPPERS_INIT.copy()
        self.taskIdCounter = 0

    def _get_container_by_key(self, key: str) -> dict:
        for container in self.containers.values():
            if container.get(MockCVPDatabase.FIELD_KEY) == key:
                return container
        raise CvpNotFoundError(f'Container with key {key} not found')

    def _count_container_child(self, id: str) -> int:
        count = 0
        for container in self.containers.values():
            if container[MockCVPDatabase.FIELD_PARENT_ID] == id:
                count += 1
        return count

    def _get_response(self, tasksTriggered: bool) -> dict:
        if tasksTriggered:
            response = {'data': {'status': 'success', 'taskIds': [self.taskIdCounter]}}
            self.taskIdCounter += 1
        else:
            response = {'data': "No tasks triggered"}
        return response

    def get_container_by_name(self, name) -> dict:
        """Mock cvprac.cvp_client.CvpApi.get_container_by_name() method"""
        # get_container_by_name() returns None if the container does not exist
        if name not in self.containers:
            return None
        keys = [MockCVPDatabase.FIELD_KEY, MockCVPDatabase.FIELD_NAME]
        return {k: v for k, v in self.containers[name].items() if k in keys}

    def add_container(self, container_name, parent_name, parent_key):
        """Mock cvprac.cvp_client.CvpApi.add_container() method"""
        if parent_name not in self.containers:
            raise CvpNotFoundError(f'Container {parent_name} not found')
        self.containers[container_name] = {MockCVPDatabase.FIELD_NAME: container_name,
                                           MockCVPDatabase.FIELD_KEY: MockCVPDatabase.CONTAINER_KEY,
                                           MockCVPDatabase.FIELD_PARENT_ID: parent_key}
        return self._get_response(True)

    def filter_topology(self, node_id='root', fmt='topology', start=0, end=0):
        """Mock cvprac.cvp_client.CvpApi.filter_topology() method"""
        if fmt != MockCVPDatabase.FIELD_TOPOLOGY or start != 0 or end != 0:
            raise NotImplementedError('Mock filter_topology() called with unsupported arguments')
        container = self._get_container_by_key(node_id)
        return {MockCVPDatabase.FIELD_TOPOLOGY: {
            MockCVPDatabase.FIELD_NAME: container[MockCVPDatabase.FIELD_NAME],
            MockCVPDatabase.FIELD_KEY: container[MockCVPDatabase.FIELD_KEY],
            MockCVPDatabase.FIELD_PARENT_ID: container[MockCVPDatabase.FIELD_PARENT_ID],
            MockCVPDatabase.FIELD_COUNT_CONTAINERS: self._count_container_child(container[MockCVPDatabase.FIELD_KEY]),
            MockCVPDatabase.FIELD_COUNT_DEVICES: 0
        }
        }

    def apply_configlets_to_container(self, app_name, container,
                                      new_configlets, create_task=True):
        """Mock cvprac.cvp_client.CvpApi.apply_configlets_to_container() method"""
        # We do not handle tasks here
        if not create_task:
            raise NotImplementedError('Mock apply_configlets_to_container() called with unsupported arguments')
        if container[MockCVPDatabase.FIELD_NAME] not in self.containers:
            raise CvpNotFoundError(f'Container {container[MockCVPDatabase.FIELD_NAME]} not found')
        for configlet in new_configlets:
            if configlet[MockCVPDatabase.FIELD_NAME] not in self.configlets:
                raise CvpNotFoundError(f'Configlet {configlet[MockCVPDatabase.FIELD_NAME]} not found')
            self.configlets[configlet[MockCVPDatabase.FIELD_NAME]][MockCVPDatabase.FIELD_CONTAINER_ATTACHED].append(container[MockCVPDatabase.FIELD_NAME])
        return self._get_response(True)

    def get_containers(self, start=0, end=0) -> dict:
        if start or end:
            raise NotImplementedError('Mock get_containers() called with unsupported arguments')
        keys = [MockCVPDatabase.FIELD_KEY, MockCVPDatabase.FIELD_NAME]
        return {
            'data': [
                {k: v for k, v in self.containers[container].items() if k in keys}
                for container in self.containers
            ]
        }

    def get_configlets_and_mappers(self):
        """
        get_configlets_and_mappers Return Mapping for configlets
        """
        return self.configlets_mappers

    def __eq__(self, other):
        return self.devices == other.devices and \
            self.containers == other.containers and \
            self.configlets == other.configlets

    def __str__(self):
        return f'\n ### Devices ###\n{pprint.pformat(self.devices)}' + \
               f'\n ### Containers ###\n{pprint.pformat(self.containers)}' + \
               f'\n ### Configlets ###\n{pprint.pformat(self.configlets)}'


def get_cvp_client(cvp_database) -> MagicMock:
    """
    Return a mock cpvrac.cvp_client.CvpClient instance.

    Returns
    -------
    MagicMock
        The mock cpvrac.cvp_client.CvpClient instance.
    """

    mock_client = create_autospec(CvpClient)
    mock_client.api = create_autospec(CvpApi)
    mock_client.api.get_container_by_name.side_effect = cvp_database.get_container_by_name
    mock_client.api.add_container.side_effect = cvp_database.add_container
    mock_client.api.filter_topology.side_effect = cvp_database.filter_topology
    mock_client.api.apply_configlets_to_container.side_effect = cvp_database.apply_configlets_to_container
    mock_client.api.get_containers.side_effect = cvp_database.get_containers
    mock_client.api.get_configlets_and_mappers.side_effect = cvp_database.get_configlets_and_mappers
    return mock_client


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def fail_json(msg: str = None):
    raise AnsibleFailJson(msg)


def get_ansible_module(check_mode: bool = False):
    """
    Return a mock ansible.module_utils.basic.AnsibleModule instance.
    The test case could eventually verify that the module exited correcty by calling the `module.exit_json.assert_called()` method.

    Returns
    -------
    MagicMock
        The mock cpvrac.cvp_client.CvpClient instance.
    """
    mock_module = create_autospec(AnsibleModule)
    mock_module.fail_json.side_effect = fail_json
    mock_module.check_mode = check_mode
    return mock_module
