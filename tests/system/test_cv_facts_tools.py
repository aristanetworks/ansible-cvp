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
from ansible_collections.arista.cvp.plugins.module_utils.facts_tools import CvFactsTools, FIELD_FACTS_DEVICE
from lib.helpers import time_log
from lib.config import user_token
from lib.utils import cvp_login
import logging
import pytest


# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #


@pytest.fixture(scope="class")
# @pytest.mark.parametrize("CVP_CONTAINER", get_user_container_definition())
def CvFactsTools_Manager(request):
    logging.info("Execute fixture to create class elements")
    requests.packages.urllib3.disable_warnings()
    request.cls.cvp = cvp_login()
    request.cls.inventory = CvFactsTools(cv_connection=request.cls.cvp)


# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #


@pytest.mark.usefixtures("CvFactsTools_Manager")
class TestCvContainerTools():

    @pytest.mark.api
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logging.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_get_container_name(self):
        result = self.inventory._get_container_name(key='undefined_container')
        assert result == 'Undefined'

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_get_container_name_incorrect(self):
        result = self.inventory._get_container_name(key='undefined_container2')
        assert result is None

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_devices(self):
        result = self.inventory.facts(scope=['devices'])
        assert FIELD_FACTS_DEVICE in result
        for dev in result[FIELD_FACTS_DEVICE]:
            assert 'parentContainerName' in dev.keys()
        logging.info('Device inventory result is: {0}'.format(result))

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_containers(self):
        result = self.inventory.facts(scope=['configlets'])
        logging.info(result)


@pytest.mark.usefixtures("CvFactsTools_Manager")
class TestCvContainerToolsAll():

    @pytest.mark.api
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logging.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_facts_all(self):
        result = self.inventory.facts()
        logging.info(result)
