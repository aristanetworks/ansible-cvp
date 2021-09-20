#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from __future__ import (absolute_import, division, print_function)
import pytest
import logging
from datetime import datetime
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from cvprac.cvp_client import CvpClient
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceInventory, CvDeviceTools, FIELD_CONTAINER_NAME, FIELD_SERIAL
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SYSMAC, FIELD_ID, FIELD_PARENT_NAME, FIELD_PARENT_ID
# from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult
import config
from data import CVP_DEVICES

# Hack to silent SSL warning
import ssl
import requests.packages.urllib3
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

CHECK_MODE = True

# Generic helpers

def time_log():
    now = datetime.now()
    return now.strftime('%H:%M:%S.%f')

# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #

def cvp_login():
    requests.packages.urllib3.disable_warnings()
    cvp_client = CvpClient()
    logging.info('Start CV login process at {}'.format(time_log()))
    cvp_client.connect(
        nodes=[config.server],
        username=config.username,
        password=config.password
    )
    logging.info('End of CV login process at {}'.format(time_log()))
    logging.info('Connected to CVP')
    return cvp_client


@pytest.fixture(scope="class")
def CvDeviceTools_Manager(request):
    logging.info("Execute fixture to create class elements")
    request.cls.cvp = cvp_login()
    request.cls.inventory = CvDeviceTools(cv_connection=request.cls.cvp)

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #

@pytest.mark.usefixtures("CvDeviceTools_Manager")
class TestCvDeviceToolsGeneric():

    # def teardown(self):
    #     # Sleep between test method in current class
    #     # Set to 30 seconds
    #     time.sleep(5)

    def test_cvp_connection(self):
        assert True
        logging.info('Connected to CVP')

    @pytest.mark.api
    def test_search_by_getter_setter(self):
        self.inventory.search_by = FIELD_SYSMAC
        assert self.inventory.search_by == FIELD_SYSMAC
        logging.info('Setter & Getter for search_by using {} is valid'.format(FIELD_SYSMAC))
        self.inventory.search_by = FIELD_FQDN
        assert self.inventory.search_by == FIELD_FQDN
        logging.info(
            'Setter & Getter for search_by using {} is valid'.format(FIELD_FQDN))

    @pytest.mark.api
    def test_check_mode_getter_setter(self):
        self.inventory.check_mode = True
        assert self.inventory.check_mode is True
        logging.info('Setter & Getter for search_by using {} is valid'.format(FIELD_SYSMAC))
        self.inventory.check_mode = False
        assert self.inventory.check_mode is False
        logging.info(
            'Setter & Getter for check_mode is valid')
