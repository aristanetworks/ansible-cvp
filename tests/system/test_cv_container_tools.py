#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from __future__ import (absolute_import, division, print_function)
import requests
import logging
import pytest
from ansible_collections.arista.cvp.plugins.module_utils.container_tools import ContainerInput, CvContainerTools
from tests.system.constants_data import STATIC_CONFIGLET_NAME_DETACH, STATIC_CONFIGLET_NAME_ATTACH
from tests.lib import mock, mock_ansible
from tests.lib.helpers import time_log
from tests.lib.config import user_token
from tests.lib.utils import cvp_login, get_container_name_id, get_unit_container, get_topology_user_input


# pytest - -html = report.html - -self-contained-html - -cov = . --cov-report = html - -color yes containerInputs.py - v


# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #


@pytest.fixture(scope="class")
# @pytest.mark.parametrize("CVP_CONTAINER", get_user_container_definition())
def CvContainerTools_Manager(request):
    logging.info("Execute fixture to create class elements")
    requests.packages.urllib3.disable_warnings()
    request.cls.cvp = cvp_login()
    request.cls.inventory = CvContainerTools(cv_connection=request.cls.cvp, ansible_module=mock_ansible.get_ansible_module())

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #


@pytest.mark.usefixtures("CvContainerTools_Manager")
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
    def test_get_container_info(self):
        requests.packages.urllib3.disable_warnings()
        container_info = self.inventory.get_container_info(
            container_name="Tenant")
        logging.info("Tenant container is {}".format(container_info))
        assert container_info["key"] == "root"
        logging.info("Tenant has a key set to {}".format(
            container_info["key"]))
        assert container_info["parentContainerId"] is None
        logging.info("Tenant has no parentContainer")

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("CV_CONTAINER", get_container_name_id())
    def test_get_container_id(self, CV_CONTAINER):
        requests.packages.urllib3.disable_warnings()
        contaier_id = self.inventory.get_container_id(
            container_name=CV_CONTAINER["name"])
        assert contaier_id == CV_CONTAINER["id"]
        logging.info("container id for {} is: {}".format(
            CV_CONTAINER["name"], contaier_id))

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("CV_CONTAINER", get_container_name_id())
    def test_container_exists(self, CV_CONTAINER):
        requests.packages.urllib3.disable_warnings()
        assert self.inventory.is_container_exists(
            container_name=CV_CONTAINER["name"])
        logging.info("Container {} exists".format(CV_CONTAINER))

    @pytest.mark.api
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("CV_CONTAINER", get_container_name_id())
    def test_is_empty(self, CV_CONTAINER):
        requests.packages.urllib3.disable_warnings()
        assert self.inventory.is_empty(
            container_name=CV_CONTAINER["name"]) is False
        logging.info("Container {} is empty".format(CV_CONTAINER))

    @pytest.mark.api
    @pytest.mark.create
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("UNIT_TEST", get_unit_container())
    def test_create_container(self, UNIT_TEST):
        requests.packages.urllib3.disable_warnings()
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST["name"])
        logging.debug("Is Container state present? {}".format(state))
        if state:
            logging.warning("NOT TESTED as container is already present on CV")
            pytest.skip("NOT TESTED as container is already present on CV")
        else:
            logging.info("Start creation process at {}".format(time_log()))
            result = self.inventory.create_container(
                container=UNIT_TEST["name"], parent=UNIT_TEST["parentContainerName"])
            logging.info("End of creation process at {}".format(time_log()))
            assert result.success is True
            logging.info(
                "Container PYTEST created under Tenant: {}".format(result.results))

    @pytest.mark.api
    @pytest.mark.create
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("UNIT_TEST", get_unit_container())
    def test_configlet_attach(self, UNIT_TEST):
        requests.packages.urllib3.disable_warnings()
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST["name"])
        logging.debug("Is Container state present ? {}".format(state))
        if state is False:
            logging.warning(
                "NOT TESTED as container is missing from CV")
            pytest.skip("NOT TESTED as container is missing from CV")
        else:
            logging.info(
                "Start configlet add process at {}".format(time_log()))
            result = self.inventory.configlets_attach(
                container=UNIT_TEST["name"], configlets=STATIC_CONFIGLET_NAME_ATTACH)
            logging.info(
                "End of configlet add process at {}".format(time_log()))
            assert result.success is True
            logging.info(
                "Configlets {} added to {}: {}".format(STATIC_CONFIGLET_NAME_ATTACH, UNIT_TEST["name"], result.results))

    @pytest.mark.api
    @pytest.mark.delete
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("UNIT_TEST", get_unit_container())
    def test_configlet_detach(self, UNIT_TEST):
        requests.packages.urllib3.disable_warnings()
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST["name"])
        logging.debug("Is Container state present ? {}".format(state))
        if state is False:
            logging.warning(
                "NOT TESTED as container is missing from CV")
            pytest.skip("NOT TESTED as container is missing from CV")
        else:
            logging.info(
                "Start configlet del process at {}".format(time_log()))
            result = self.inventory.configlets_detach(
                container=UNIT_TEST["name"], configlets=STATIC_CONFIGLET_NAME_DETACH)
            logging.info(
                "End of configlet del process at {}".format(time_log()))
            assert result.success is True
            logging.info(
                "Configlets {} added to {}: {}".format(STATIC_CONFIGLET_NAME_DETACH, UNIT_TEST["name"], result.results))

    @pytest.mark.api
    @pytest.mark.delete
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("UNIT_TEST", get_unit_container())
    def test_delete_container(self, UNIT_TEST):
        requests.packages.urllib3.disable_warnings()
        state = self.inventory.is_container_exists(
            container_name=UNIT_TEST["name"])
        logging.debug("Is Container state present ? {}".format(state))
        if state is False:
            logging.warning(
                "NOT TESTED as container is already removed from CV")
            pytest.skip("NOT TESTED as container is already removed from CV")
        else:
            logging.info("Start deletion process at {}".format(time_log()))
            result = self.inventory.delete_container(
                container=UNIT_TEST["name"], parent=UNIT_TEST["parentContainerName"])
            logging.info("End of deletion process at {}".format(time_log()))
            assert result.success is True
            logging.info(
                "Container {} deleted from cloudvision: {}".format(UNIT_TEST["name"], result.results))

    @pytest.mark.api
    @pytest.mark.delete
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("UNIT_TEST", get_unit_container())
    def test_get_configlet_from_container(self, UNIT_TEST):
        requests.packages.urllib3.disable_warnings()
        configlets = self.inventory.get_configlets(
            container_name="ansible-cvp-tests-1")
        assert len(configlets) > 0
        for configlet in configlets:
            assert configlet["name"] in [
               "cvaas-unit-test-01", "cvaas-unit-test-02", "leaf-1-unit-test"]
            logging.info(
                "CVP returned {} and it is in the expected list".format(configlet["name"]))
        logging.info("All returned configlets are in expected list")


@pytest.mark.usefixtures("CvContainerTools_Manager")
@pytest.mark.filterwarnings("ignore::urllib3.exceptions.InsecureRequestWarning")
class TestCvContainerToolsTopology():

    @pytest.mark.api
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
    def test_cv_connection(self):
        requests.packages.urllib3.disable_warnings()
        logging.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.api
    @pytest.mark.parametrize("USER_INPUT", get_topology_user_input())
    @pytest.mark.parametrize("APPLY_MODE", ["strict", "loose"])
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_build_topology(self, USER_INPUT, APPLY_MODE):
        requests.packages.urllib3.disable_warnings()
        user_inventory = ContainerInput(user_topology=USER_INPUT)
        logging.info(
            "Start of topology build process at {}".format(time_log()))
        result = self.inventory.build_topology(
            user_topology=user_inventory, present=True, apply_mode=APPLY_MODE)
        logging.info("End of topology build process at {}".format(time_log()))
        # assert result.success is True
        assert result.success is True
        logging.info(
            "Topology build result is: {}".format(result.content))

    @pytest.mark.api
    @pytest.mark.parametrize("USER_INPUT", get_topology_user_input())
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_remove_topology(self, USER_INPUT):
        requests.packages.urllib3.disable_warnings()
        user_inventory = ContainerInput(user_topology=USER_INPUT)
        logging.info(
            "Start of topology del process at {}".format(time_log()))
        result = self.inventory.build_topology(
            user_topology=user_inventory, present=False)
        logging.info("End of topology del process at {}".format(time_log()))
        assert result.success is True
        logging.info(
            "Topology del result is: {}".format(result.content))
