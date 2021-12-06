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
import logging
import pytest
from datetime import datetime
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.configlet_tools import CvConfigletTools, ConfigletInput
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult
from lib.helpers import time_log, AnsibleModuleMock
from lib.parametrize import generate_CvConfigletTools_content
from lib.config import user_token, server
from lib.cvaas_configlet import  SYSTEM_CONFIGLETS_TESTS
from lib.utils import cvp_login
from lib.provisioner import CloudvisionProvisioner


# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #


@pytest.fixture(scope="class")
def CvContainerTools_Manager(request):
    logging.info('Provision Cloudvision instance')
    provisioner = CloudvisionProvisioner(server=server, token=user_token)
    provisioner.provision_configlets(configlets=SYSTEM_CONFIGLETS_TESTS)
    logging.info("Execute fixture to create class elements")
    requests.packages.urllib3.disable_warnings()
    request.cls.cvp = cvp_login()
    ansible_module = AnsibleModuleMock(check_mode=False)
    request.cls.cv_configlet = CvConfigletTools(cv_connection=request.cls.cvp, ansible_module=ansible_module)


# ---------------------------------------------------------------------------- #
#   TESTS Management
# ---------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.usefixtures("CvContainerTools_Manager")
@pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
# Parametrize to build a ConfigletInput from list of configlet in SYSTEM_CONFIGLETS_TESTS. Only those set with is_present_expected to False
@pytest.mark.parametrize("test_configlet", SYSTEM_CONFIGLETS_TESTS, ids=['system-configlet-tests01', 'system-configlet-tests02', 'system-configlet-tests03', 'system-configlet-tests04'])
@pytest.mark.parametrize("check_mode", [True, False], ids=['check_mode_on', 'check_mode_off'])
class Test_CvConfiglet_Unit():

    @pytest.mark.dependency(name='authentication')
    def test_cv_connection(self, test_configlet, check_mode):
        requests.packages.urllib3.disable_warnings()
        logging.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_configlet_data_from_cv(self, test_configlet, check_mode):
        cv_data = self.cv_configlet.get_configlet_data_cv(configlet_name=test_configlet['name'])
        self.cv_configlet._ansible.check_mode = check_mode
        logging.debug('CV data for configlet {0} is {1}'.format(test_configlet['name'], cv_data))
        if test_configlet['is_present_expected']:
            logging.info('Configlet is expected to exist.')
            assert cv_data is not None
            assert type(cv_data) is dict
            logging.info('Configlet has correct format and has data')
        else:
            logging.warning('Configlet is NOT expected to exist.')
            assert cv_data is None
            logging.info('Configlet data is None')

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_configlet_is_present(self, test_configlet, check_mode):
        cv_configlet_is_present = self.cv_configlet.is_present(configlet_name=test_configlet['name'])
        self.cv_configlet._ansible.check_mode = check_mode
        logging.info('Configlet is expected to be present: {}'.format(test_configlet['is_present_expected']))
        assert cv_configlet_is_present == test_configlet['is_present_expected']
        logging.info('State report is correct: {}'.format(cv_configlet_is_present))

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_str_compare(self, test_configlet, check_mode):
        self.cv_configlet._ansible.check_mode = check_mode
        python_str_not_equal = (
            test_configlet['config'] != test_configlet['config_expected']
        )
        diff_data = self.cv_configlet._compare(
            fromText=test_configlet['config'],
            toText=test_configlet['config_expected']
            )
        logging.debug('Diff result is: {}'.format(diff_data))
        assert python_str_not_equal is diff_data[0]
        if diff_data[0]:
            logging.info('Diff is : {}'.format(diff_data[1]))
        else:
            logging.info('No diff to display')

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_create_configlet(self, test_configlet, check_mode):
        if test_configlet['is_present_expected']:
            logging.warning('Skipped as it is not designed for creation test')
            pytest.skip("Not covered by create scenario")
        self.cv_configlet._ansible.check_mode = check_mode
        # configlet = {test_configlet['name']: test_configlet['config']}
        api_call = self.cv_configlet.create(to_create=[test_configlet], note='Created by pytest')
        logging.debug('API result is: {}'.format(api_call[0].results))
        assert type(api_call[0] is CvApiResult)
        assert api_call[0].results['success'] is True
        assert api_call[0].results['changed'] is not check_mode

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_delete_configlet(self, test_configlet, check_mode):
        if test_configlet['is_present_expected']:
            logging.warning('Skipped as it is not designed for delete test')
            pytest.skip("Not covered by delete scenario")
        self.cv_configlet._ansible.check_mode = check_mode
        configlet_key = self.cv_configlet.get_configlet_data_cv(configlet_name=test_configlet['name'])['key']
        configlet = {'name':test_configlet['name'], 'key':configlet_key}
        api_call = self.cv_configlet.delete(to_delete=[configlet])
        logging.debug('API result is: {}'.format(api_call[0].results))
        assert type(api_call[0] is CvApiResult)
        assert api_call[0].results['success'] is not check_mode
        assert api_call[0].results['changed'] is not check_mode

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_update_configlet(self, test_configlet, check_mode):
        if test_configlet['is_present_expected'] is False:
            logging.warning('Skipped as it is not designed for update test')
            pytest.skip("Not covered by update scenario")
        now = datetime.now()
        self.cv_configlet._ansible.check_mode = check_mode
        configlet_key = self.cv_configlet.get_configlet_data_cv(configlet_name=test_configlet['name'])['key']
        configlet = {'name':test_configlet['name'], 'key':configlet_key, 'config': test_configlet['config']}
        api_call = self.cv_configlet.update(to_update=[configlet], note='Updated by pytest - {}'.format(now.strftime("%m/%d/%Y, %H:%M:%S")))
        logging.debug('Update - API result is: {}'.format(api_call[0].results))
        assert type(api_call[0] is CvApiResult)
        assert api_call[0].results['success'] is True
        # Revert content only if check_mode is False
        if check_mode is False:
            configlet = {'name':test_configlet['name'], 'key':configlet_key, 'config': test_configlet['config_expected']}
            api_call = self.cv_configlet.update(to_update=[configlet], note='Updated by pytest - {}'.format(now.strftime("%m/%d/%Y, %H:%M:%S")))
            logging.debug('Revert to expected - API result is: {}'.format(api_call[0].results))

@pytest.mark.api
@pytest.mark.usefixtures("CvContainerTools_Manager")
@pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
# Parametrize to build a ConfigletInput from list of configlet in SYSTEM_CONFIGLETS_TESTS. Only those set with is_present_expected to False
@pytest.mark.parametrize("configlet_inventory", generate_CvConfigletTools_content(configlet_inputs=SYSTEM_CONFIGLETS_TESTS), ids=['configlet-not-already-declared'])
@pytest.mark.parametrize("check_mode", [True, False], ids=['check_mode_on', 'check_mode_off'])
class Test_CvConfiglet_Manager():

    @pytest.mark.dependency(name='authentication')
    def test_cv_connection(self, configlet_inventory, check_mode):
        requests.packages.urllib3.disable_warnings()
        logging.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_configlet_local_inventory(self, configlet_inventory, check_mode):
        logging.debug('Local configlet input: \n{}'.format(configlet_inventory))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_apply_present(self, configlet_inventory, check_mode):
        now = datetime.now()
        inventory = ConfigletInput(user_topology=configlet_inventory)
        assert inventory.is_valid
        logging.info('Configlet inventory is valid, continuing...')
        self.cv_configlet._ansible.check_mode = check_mode
        api_result = self.cv_configlet.apply(
            configlet_list=inventory.configlets,
            present=True,
            note='Updated by pytest - {}'.format(time_log()))
        logging.info('API call response is: {}'.format(api_result.content))
        # TODO: Should have assert test and not just test API execution
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_apply_delete(self, configlet_inventory, check_mode):
        now = datetime.now()
        inventory = ConfigletInput(user_topology=configlet_inventory)
        assert inventory.is_valid
        logging.info('Configlet inventory is valid, continuing...')
        self.cv_configlet._ansible.check_mode = check_mode
        api_result = self.cv_configlet.apply(
            configlet_list=inventory.configlets,
            present=False,
            note='Updated by pytest - {}'.format(time_log()))
        logging.info('API call response is: {}'.format(api_result.content))
        # TODO: Should have assert test and not just test API execution
        assert True
