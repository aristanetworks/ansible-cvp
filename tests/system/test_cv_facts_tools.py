#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import requests
import sys
import pytest
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_PARENT_NAME, FIELD_CONFIGLETS
from ansible_collections.arista.cvp.plugins.module_utils.fields import FIELD_FACTS_DEVICE, FIELD_FACTS_CONFIGLET, FIELD_FACTS_CONTAINER
from ansible_collections.arista.cvp.plugins.module_utils.facts_tools import CvFactsTools
from ansible_collections.arista.cvp.plugins.module_utils.schema_v3 import validate_cv_inputs, SCHEMA_CV_CONFIGLET, SCHEMA_CV_CONTAINER, SCHEMA_CV_DEVICE
from lib.helpers import AnsibleModuleMock, setup_custom_logger
from lib.config import user_token
from lib.utils import cvp_login, generate_test_ids_dict
from lib.cvaas_facts import FACTS_CONTAINERS_TEST, FACT_DEVICE_TEST, FACT_FILTER_TEST


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
#   PYTEST
# ---------------------------------------------------------------------------- #

# -------------------
# Test Containers

@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.parametrize("test_container", FACTS_CONTAINERS_TEST, ids=generate_test_ids_dict)
@pytest.mark.api
class TestCvContainerToolsContainers():

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self, test_container):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_get_container_name(self, test_container):
        result = self.inventory._CvFactsTools__get_container_name(key=test_container['container_id'])
        logger.debug('Got response from module: {0}'.format(result))
        if test_container['is_present_expected']:
            assert result == test_container['name_expected']
        else:
            assert result is None
        logger.info('Got correct response from module')
        logger.debug('Got response from module: {0}'.format(result))


@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.api
class TestCvContainerToolsContainers():
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_containers(self):
        result = self.inventory.facts(scope=['containers'])
        logger.debug('Got response from module: {0}'.format(result))
        assert FIELD_FACTS_CONTAINER in result
        assert validate_cv_inputs(user_json=result[FIELD_FACTS_CONTAINER], schema=SCHEMA_CV_CONTAINER)
        logger.info('output is valid against collection schema')

# -------------------
# Test Devices

@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.parametrize("test_device", FACT_DEVICE_TEST, ids=generate_test_ids_dict)
@pytest.mark.api
class TestCvContainerToolsDevices():

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self, test_device):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_get_device_configlet_correct(self, test_device):
        result = self.inventory._CvFactsTools__device_get_configlets(netid=test_device['sysmac'])
        if test_device['is_present_expected']:
            assert len(result) == len(test_device['configlet_expected'])
        else:
            assert len(result) == 0
        assert result is not None
        logger.info('Got correct response from Cloudvision')
        logger.debug('Got response from module: {0}'.format(result))

@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.api
class TestCvContainerToolsDevicesFacts():


    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_devices(self):
        result = self.inventory.facts(scope=['devices'])
        # Test device section is present
        assert FIELD_FACTS_DEVICE in result
        assert len(result[FIELD_FACTS_DEVICE]) > 0
        logger.info('Facts have a correct %s section', str(FIELD_FACTS_DEVICE))

        # Test all devices have a parentContainerName
        for dev in result[FIELD_FACTS_DEVICE]:
            assert FIELD_PARENT_NAME in dev.keys()
        logger.info('all devices have a %s field', str(FIELD_PARENT_NAME))

        # Validate data with schema
        assert validate_cv_inputs(user_json=result[FIELD_FACTS_DEVICE], schema=SCHEMA_CV_DEVICE)
        logger.info('output is valid against collection schema')
        logger.debug('Got response from module: {0}'.format(result))


@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.parametrize("test_filter", FACT_FILTER_TEST, ids=generate_test_ids_dict)
@pytest.mark.api
class TestCvContainerToolsDevicesFilter():

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self, test_filter):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_devices_filter(self, test_filter):
        self.inventory._CvFactsTools__init_facts()
        result = self.inventory.facts(scope=['devices'], regex_filter=test_filter['filter'])

        assert len(result[FIELD_FACTS_DEVICE]) == len(test_filter['result_device_expected'])
        logger.info('filtered output is correct with %s', str(test_filter['filter']))

        assert validate_cv_inputs(user_json=result[FIELD_FACTS_DEVICE], schema=SCHEMA_CV_DEVICE)
        logger.info('output is valid against collection schema')
        logger.debug('Got response from module: {0}'.format(result))


# -------------------
# Test Configlets

@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.api
class TestCvContainerToolsConfiglets():

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True


    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_configlets(self):
        result = self.inventory.facts(scope=['configlets'])
        assert 'cvp_configlets' in result
        assert validate_cv_inputs(user_json=result[FIELD_FACTS_CONFIGLET], schema=SCHEMA_CV_CONFIGLET)
        logger.info('output is valid against collection schema')
        logger.debug('Got response from module: {0}'.format(result['cvp_configlets'].keys()))


@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.api
@pytest.mark.parametrize("test_filter", FACT_FILTER_TEST, ids=generate_test_ids_dict)
class TestCvContainerToolsConfiglets():

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self, test_filter):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_configlets_filter(self, test_filter):
        self.inventory._CvFactsTools__init_facts()
        result = self.inventory.facts(scope=['configlets'], regex_filter=test_filter['filter'])

        assert len(result[FIELD_FACTS_CONFIGLET]) == len(test_filter['result_configlet_expected'])
        logger.info('filtered output is correct with %s', str(test_filter['filter']))

        assert validate_cv_inputs(user_json=result[FIELD_FACTS_CONFIGLET], schema=SCHEMA_CV_CONFIGLET)
        logger.info('output is valid against collection schema')
        logger.debug('Got response from module: {0}'.format(result))


# -------------------
# Test All facts

@pytest.mark.usefixtures("CvFactsTools_Manager")
@pytest.mark.api
class TestCvContainerToolsAllFacts():

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_all(self):
        fact_sections = ['containers', 'devices', 'configlets']
        result = self.inventory.facts(scope=fact_sections)
        assert FIELD_FACTS_CONFIGLET in result
        assert FIELD_FACTS_CONTAINER in result
        assert FIELD_FACTS_DEVICE in result
        logger.debug('Got response from module: {0}'.format(result))