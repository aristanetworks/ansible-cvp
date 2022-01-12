#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from __future__ import (absolute_import, division, print_function)
import requests
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.facts_tools import CvFactsTools, FIELD_FACTS_DEVICE, FIELD_FACTS_CONTAINER, FIELD_FACTS_CONFIGLET, FIELD_PARENT_NAME
from ansible_collections.arista.cvp.plugins.module_utils.schema_v3 import validate_cv_inputs, SCHEMA_CV_CONFIGLET, SCHEMA_CV_CONTAINER, SCHEMA_CV_DEVICE
from lib.helpers import time_log, AnsibleModuleMock, setup_custom_logger
from lib.config import user_token
from lib.utils import cvp_login, generate_test_ids_list
from lib.parametrize import mook_data
import logging
import pytest


# Set specific logging syntax
logger = setup_custom_logger('facts_v3_system')

# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #


@pytest.fixture(scope="class")
# @pytest.mark.parametrize("CVP_CONTAINER", get_user_container_definition())
def CvFactsTools_Manager(request):
    logger.info("Execute fixture to create class elements")
    requests.packages.urllib3.disable_warnings()
    request.cls.cvp = cvp_login()
    # ansible_module = AnsibleModuleMock(check_mode=False)
    # request.cls.inventory = CvFactsTools(cv_connection=request.cls.cvp, ansible_module=ansible_module)
    request.cls.inventory = CvFactsTools(cv_connection=request.cls.cvp)

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

# Required as moock_data is one more level for facts
def generate_flat_data(type: str, mode: str = "valid", fact: str = "device_ids"):
    """Returns the data based on type and mode

        Args:
            type (string): type of data. It can be 'device', 'container' or 'configlet'
            mode (string): mode can be 'valid' or 'invalid'
            fact (string): Fact type to get data. Can be 'devices'

        Returns:
            List: data based on mode and type
        """
    flat_data = []
    if (
        mode in mook_data
        and type in mook_data[mode]
        and fact in mook_data[mode][type]
    ):
        for fact_type in mook_data[mode][type][fact]:
            flat_data.append(fact_type)
    return flat_data



# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #


@pytest.mark.usefixtures("CvFactsTools_Manager")
class TestCvContainerToolsContainers():

    @pytest.mark.api
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_get_container_name(self):
        result = self.inventory._CvFactsTools__get_container_name(key='undefined_container')
        assert result == 'Undefined'
        logger.debug('Got response from module: {0}'.format(result))


    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_get_container_name_incorrect(self):
        result = self.inventory._CvFactsTools__get_container_name(key='undefined_container2')
        assert result is None
        logger.debug('Got response from module: {0}'.format(result))


    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_containers(self):
        result = self.inventory.facts(scope=['containers'])
        logger.debug('Got response from module: {0}'.format(result))
        assert FIELD_FACTS_CONTAINER in result
        assert validate_cv_inputs(user_json=result[FIELD_FACTS_CONTAINER], schema=SCHEMA_CV_CONTAINER)
        logger.info('output is valid against collection schema')



@pytest.mark.usefixtures("CvFactsTools_Manager")
class TestCvContainerToolsDevices():

    @pytest.mark.api
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("netid", generate_flat_data(type='facts', mode='valid', fact='device_ids'), ids=generate_test_ids_list)
    def test_get_device_configlet_correct(self, netid):
        result = self.inventory._CvFactsTools__device_get_configlets(netid=netid)
        assert result is not None
        assert len(result) >= 1
        logger.debug('Got response from module: {0}'.format(result))

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("netid", generate_flat_data(type='facts', mode='invalid', fact='device_ids'), ids=generate_test_ids_list)
    def test_get_device_configlet_incorrect(self, netid):
        result = self.inventory._CvFactsTools__device_get_configlets(netid=netid)
        assert result is not None
        assert len(result) == 0
        logger.debug('Got response from module: {0}'.format(result))

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_devices(self):
        result = self.inventory.facts(scope=['devices'])
        assert FIELD_FACTS_DEVICE in result
        for dev in result[FIELD_FACTS_DEVICE]:
            assert FIELD_PARENT_NAME in dev.keys()
        assert validate_cv_inputs(user_json=result[FIELD_FACTS_DEVICE], schema=SCHEMA_CV_DEVICE)
        logger.info('output is valid against collection schema')
        logger.debug('Got response from module: {0}'.format(result))


    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_fake(self):
        data = {
            'configlets_mappers': self.cvp.api.get_configlets_and_mappers()['data']
        }

        logger.debug(data['configlets_mappers']['configletMappers'])
        # configletIds = [mapper['configletId'] for mapper in self._cache['configlets_mappers']['configletMappers']]


@pytest.mark.usefixtures("CvFactsTools_Manager")
class TestCvContainerToolsConfiglets():

    @pytest.mark.api
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_configlets(self):
        result = self.inventory.facts(scope=['configlets'])
        assert 'cvp_configlets' in result
        assert validate_cv_inputs(user_json=result[FIELD_FACTS_CONFIGLET], schema=SCHEMA_CV_CONFIGLET)
        logger.info('output is valid against collection schema')
        logger.debug('Got response from module: {0}'.format(result))



@pytest.mark.usefixtures("CvFactsTools_Manager")
class TestCvContainerToolsAll():

    @pytest.mark.api
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_all(self):
        fact_sections = ['containers', 'devices', 'configlets']
        result = self.inventory.facts(scope=fact_sections)
        assert FIELD_FACTS_CONFIGLET in result
        assert FIELD_FACTS_CONTAINER in result
        assert FIELD_FACTS_DEVICE in result
        logger.debug('Got response from module: {0}'.format(result))
