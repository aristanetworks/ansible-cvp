#!/usr/bin/python
# coding: utf-8 -*-

from unittest.mock import MagicMock, create_autospec
import pprint
import logging
from cvprac.cvp_client import CvpClient, CvpApi
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from tests.data import facts_unit

LOGGER = logging.getLogger(__name__)


class CvpNotFoundError(Exception):
    """Exception class to be raised when data is not found in mock CVP database"""
    pass


class MockCVPDatabase:
    """Class to mock CVP database being modified during tests"""

    # Fields in API data
    FIELD_COUNT_DEVICES = Api.container.COUNT_DEVICE
    FIELD_COUNT_CONTAINERS = Api.container.COUNT_CONTAINER
    FIELD_PARENT_ID = Api.generic.PARENT_CONTAINER_ID
    FIELD_PARENT_NAME = Api.generic.PARENT_CONTAINER_NAME
    FIELD_NAME = Api.generic.NAME
    FIELD_KEY = Api.generic.KEY
    FIELD_TOPOLOGY = Api.container.TOPOLOGY

    # Fields in mock database
    FIELD_CONTAINER_ATTACHED = 'containerAttached'

    # Data used in mock methods
    CONTAINER_KEY = 'container_1234abcd-1234-abcd-12ab-123456abcdef'
    BAD_KEY = 'badKey'

    CVP_DATA_CONTAINERS_INIT = {
        'Tenant': {
            'name': 'Tenant',
            'key': 'root',
            'parentContainerId': None}
    }

    # Data used to initiate the mock database
    # CVP_DATA_DEVICE_INIT = magickmock_data.MOCKDATA_DEVICES
    # CVP_DATA_CONTAINERS_INIT = magickmock_data.MOCKDATA_CONTAINERS
    # CVP_DATA_CONFIGLETS_MAPPERS_INIT = magickmock_data.MOCKDATA_CONFIGLET_MAPPERS
    # CVP_DATA_CONFIGLET_INIT = magickmock_data.MOCKDATA_CONFIGLETS

    def __init__(self, devices: dict = None, containers: list = None, configlets: list = None, configlets_mappers: dict = None, images: dict = None, image_bundles: dict = None):
        self.devices = devices if devices is not None else {}
        # self.containers = containers if containers is not None else {}
        self.containers = containers if containers is not None else MockCVPDatabase.CVP_DATA_CONTAINERS_INIT.copy()
        self.configlets = configlets if configlets is not None else {}
        self.configlets_mappers = configlets_mappers if configlets_mappers is not None else {}
        self.images = images if images is not None else {}
        self.image_bundles = image_bundles if image_bundles is not None else {}
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
        if name not in self.containers:
            return None
        if name == MockCVPDatabase.BAD_KEY:  # Special container name to mimic a wrong API key
            keys = [MockCVPDatabase.BAD_KEY, MockCVPDatabase.FIELD_NAME]
        else:
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

    def get_images(self):
        return self.images

    def get_image_bundles(self):
        return self.image_bundles

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
               f'\n ### Configlets ###\n{pprint.pformat(self.configlets)}' +\
               f'\n ### Images ###\n{pprint.pformat(self.images)}' +\
               f'\n ### Image Bundles ###\n{pprint.pformat(self.image_bundles)}'


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
    mock_client.api.get_images.side_effect = cvp_database.get_images
    mock_client.api.get_image_bundles.side_effect = cvp_database.get_image_bundles
    return mock_client
