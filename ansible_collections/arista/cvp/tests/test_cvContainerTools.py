#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
from datetime import datetime
import sys
import logging
import pytest
sys.path.append("../../../../")
from ansible_collections.arista.cvp.plugins.module_utils.container_tools import ContainerInput, CvContainerTools
from cvprac.cvp_client import CvpClient
import requests

# pytest - -html = report.html - -self-contained-html - -cov = . --cov-report = html - -color yes containerInputs.py - v

USER_CONTAINERS = [
    {"PYTEST": {"parentContainerName": "Tenant"}, "Leafs": {"parentContainerName": "PYTEST"}, "Spines": {
        "parentContainerName": "PYTEST", "configlets": ["01TRAINING-01"]}, "POD01": {"parentContainerName": "Leafs"}}
]

CV_CONTAINERS_NAME_ID_LIST = [{'name': 'Tenant', 'id': 'root'}]

STATIC_CONFIGLET_NAME = ['01TRAINING-01']

TOPOLOGY_STATE = ['present', 'absent']

# Generic helpers
def time_log():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

def get_container_name_id():
    return CV_CONTAINERS_NAME_ID_LIST


def get_unit_container():
    result = list()
    for key, values in USER_CONTAINERS[0].items():
        values['name'] = key
        result.append(values)
    return [result[0]]


def get_topology_user_input():
    return USER_CONTAINERS

# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #

def cvp_login():
    requests.packages.urllib3.disable_warnings()
    logging.info('Start CV login process at {}'.format(time_log()))
    cvp_client = CvpClient()
    cvp_client.connect(
        nodes=['10.83.28.164'],
        username='ansible',
        password='interdata'
    )
    logging.info('End of CV login process at {}'.format(time_log()))
    logging.info('Connected to CVP')
    return cvp_client


@pytest.fixture(scope="class")
# @pytest.mark.parametrize('CVP_CONTAINER', get_user_container_definition())
def CvContainerTools_Manager(request):
    logging.info("Execute fixture to create class elements")
    request.cls.cvp = cvp_login()
    request.cls.inventory = CvContainerTools(cv_connection=request.cls.cvp)

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #

@pytest.mark.usefixtures("CvContainerTools_Manager")
@pytest.mark.api
class TestCvContainerTools():
    def test_cv_connection(self):
        logging.debug(str('Class is connected to CV'))
        assert True

    @pytest.mark.api
    def test_get_container_info(self):
        requests.packages.urllib3.disable_warnings()
        container_info = self.inventory.get_container_info(container_name='Tenant')
        logging.info('Tenant container is {}'.format(container_info))
        assert container_info['key'] == 'root'
        logging.info('Tenant has a key set to {}'.format(container_info['key']))
        assert container_info['parentContainerId'] is None
        logging.info('Tenant has no parentContainer')

    @pytest.mark.parametrize('CV_CONTAINER', get_container_name_id())
    @pytest.mark.api
    def test_get_container_id(self, CV_CONTAINER):
        contaier_id = self.inventory.get_container_id(container_name=CV_CONTAINER['name'])
        assert contaier_id == CV_CONTAINER['id']
        logging.info('container id for {} is: {}'.format(CV_CONTAINER['name'], contaier_id))

    @pytest.mark.parametrize('CV_CONTAINER', get_container_name_id())
    @pytest.mark.api
    def test_container_exists(self, CV_CONTAINER):
        assert self.inventory.is_container_exists(container_name=CV_CONTAINER['name'])
        logging.info('Container {} exists'.format(CV_CONTAINER))

    @pytest.mark.parametrize('CV_CONTAINER', get_container_name_id())
    @pytest.mark.api
    def test_is_empty(self, CV_CONTAINER):
        assert self.inventory.is_empty(container_name=CV_CONTAINER['name']) is False
        logging.info('Container {} is empty'.format(CV_CONTAINER))


    @pytest.mark.parametrize('UNIT_TEST', get_unit_container())
    @pytest.mark.api
    @pytest.mark.create
    def test_create_container(self, UNIT_TEST):
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST['name'])
        logging.debug('Is Container state present? {}'.format(state))
        if state:
            logging.warning('NOT TESTED as container is already present on CV')
            pytest.skip("NOT TESTED as container is already present on CV")
        else:
            logging.info('Start creation process at {}'.format(time_log()))
            result = self.inventory.create_container(
                container=UNIT_TEST['name'], parent=UNIT_TEST['parentContainerName'])
            logging.info('End of creation process at {}'.format(time_log()))
            assert result.success is True
            logging.info(
                'Container PYTEST created under Tenant: {}'.format(result.results))


    @pytest.mark.parametrize('UNIT_TEST', get_unit_container())
    @pytest.mark.api
    @pytest.mark.create
    def test_configlet_attach(self, UNIT_TEST):
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST['name'])
        logging.debug('Is Container state present ? {}'.format(state))
        if state is False:
            logging.warning(
                'NOT TESTED as container is missing from CV')
            pytest.skip("NOT TESTED as container is missing from CV")
        else:
            logging.info('Start configlet add process at {}'.format(time_log()))
            result = self.inventory.configlets_attach(container=UNIT_TEST['name'], configlets=STATIC_CONFIGLET_NAME)
            logging.info(
                'End of configlet add process at {}'.format(time_log()))
            assert result.success is True
            logging.info(
                'Configlets {} added to {}: {}'.format(STATIC_CONFIGLET_NAME, UNIT_TEST['name'], result.results))

    @pytest.mark.parametrize('UNIT_TEST', get_unit_container())
    @pytest.mark.api
    @pytest.mark.delete
    def test_configlet_detach(self, UNIT_TEST):
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST['name'])
        logging.debug('Is Container state present ? {}'.format(state))
        if state is False:
            logging.warning(
                'NOT TESTED as container is missing from CV')
            pytest.skip("NOT TESTED as container is missing from CV")
        else:
            logging.info(
                'Start configlet del process at {}'.format(time_log()))
            result = self.inventory.configlets_detach(
                container=UNIT_TEST['name'], configlets=STATIC_CONFIGLET_NAME)
            logging.info(
                'End of configlet del process at {}'.format(time_log()))
            assert result.success is True
            logging.info(
                'Configlets {} added to {}: {}'.format(STATIC_CONFIGLET_NAME, UNIT_TEST['name'], result.results))

    @pytest.mark.parametrize('UNIT_TEST', get_unit_container())
    @pytest.mark.api
    @pytest.mark.delete
    def test_delete_container(self, UNIT_TEST):
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST['name'])
        logging.debug('Is Container state present ? {}'.format(state))
        if state is False:
            logging.warning('NOT TESTED as container is already removed from CV')
            pytest.skip("NOT TESTED as container is already removed from CV")
        else:
            logging.info('Start deletion process at {}'.format(time_log()))
            result = self.inventory.delete_container(
                container=UNIT_TEST['name'], parent=UNIT_TEST['parentContainerName'])
            logging.info('End of deletion process at {}'.format(time_log()))
            assert result.success is True
            logging.info(
                'Container {} deleted from cloudvision: {}'.format(UNIT_TEST['name'], result.results))


@pytest.mark.usefixtures("CvContainerTools_Manager")
@pytest.mark.api
@pytest.mark.create
@pytest.mark.filterwarnings('ignore::urllib3.exceptions.InsecureRequestWarning')
class TestCvContainerToolsTopology():

    # def teardown(self):
    #     # Sleep between test method in current class
    #     # Set to 30 seconds
    #     time.sleep(30)

    def test_cv_connection(self):
        logging.debug(str('Class is connected to CV'))
        assert True

    @pytest.mark.parametrize('USER_INPUT', get_topology_user_input())
    @pytest.mark.api
    @pytest.mark.create
    def test_build_topology(self, USER_INPUT):
        user_inventory = ContainerInput(user_topology=USER_INPUT)
        logging.info('Start of topology build process at {}'.format(time_log()))
        result = self.inventory.build_topology(
            user_topology=user_inventory, present=True)
        logging.info('End of topology build process at {}'.format(time_log()))
        # assert result.success is True
        assert result.success is True
        logging.info(
            'Topology build result is: {}'.format(result.content))

    @pytest.mark.parametrize('USER_INPUT', get_topology_user_input())
    @pytest.mark.api
    @pytest.mark.delete
    # @pytest.mark.topology
    def test_remove_topology(self, USER_INPUT):
        user_inventory = ContainerInput(user_topology=USER_INPUT)
        logging.info(
            'Start of topology del process at {}'.format(time_log()))
        result = self.inventory.build_topology(
            user_topology=user_inventory, present=False)
        logging.info('End of topology del process at {}'.format(time_log()))
        assert result.success is True
        logging.info(
            'Topology del result is: {}'.format(result.content))
