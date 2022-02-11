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
from datetime import datetime
from ansible_collections.arista.cvp.plugins.module_utils.configlet_tools import CvConfigletTools, ConfigletInput
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult
from tests.lib.helpers import time_log, AnsibleModuleMock, setup_custom_logger, to_nice_json
from tests.lib.parametrize import generate_CvConfigletTools_content
from tests.lib.config import user_token, provision_cv
from tests.lib.cvaas_configlet import  SYSTEM_CONFIGLETS_TESTS
from tests.lib.utils import cvp_login, generate_test_ids_dict
from tests.lib.provisioner import CloudvisionProvisioner


# Set specific logging syntax
logger = setup_custom_logger('configlet_system')


# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #

@pytest.fixture(scope="class")
def CvContainerTools_Manager(request):
    if provision_cv:
        logger.info('Provision Cloudvision instance')
        request.cls.provisioner = CloudvisionProvisioner()
        request.cls.provisioner.configlets_provision(configlets=SYSTEM_CONFIGLETS_TESTS)
        logger.info('Provisioning done !')
    logger.info("Execute fixture to create class elements")
    requests.packages.urllib3.disable_warnings()
    request.cls.cvp = cvp_login()
    ansible_module = AnsibleModuleMock(check_mode=False)
    request.cls.cv_configlet = CvConfigletTools(cv_connection=request.cls.cvp, ansible_module=ansible_module)
    logger.info("CV connection instance done at {}.".format(time_log()))
    yield
    logging.warning('Killing Cloudvision instance')


# ---------------------------------------------------------------------------- #
#   TESTS Management
# ---------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.configlet
@pytest.mark.usefixtures("CvContainerTools_Manager")
@pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
# Parametrize to build a ConfigletInput from list of configlet in SYSTEM_CONFIGLETS_TESTS. Only those set with is_present_expected to False
@pytest.mark.parametrize("test_configlet", SYSTEM_CONFIGLETS_TESTS, ids=generate_test_ids_dict)
@pytest.mark.parametrize("check_mode", [True, False], ids=['check_mode_on', 'check_mode_off'])
class Test_CvConfiglet_Unit():

    @pytest.mark.create
    @pytest.mark.delete
    @pytest.mark.dependency(name='authentication')
    def test_cv_connection(self, test_configlet, check_mode):
        requests.packages.urllib3.disable_warnings()
        logger.info("Class is connected to CV at {}".format(time_log()))
        assert True

    @pytest.mark.parametrize('non_string', [1, 100, True, False])
    def test_str_cleanup_no_str(self, test_configlet, check_mode, non_string):
        logger.info('Test str_cleanup with non-str input')
        res = self.cv_configlet._str_cleanup_line_ending(content=non_string)
        assert res is None
        logger.info('Result is None as expected')

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_configlet_data_from_cv(self, test_configlet, check_mode):
        # Set check mode
        self.cv_configlet._ansible.check_mode = check_mode
        # Work with API
        logger.info('Start to get configlet data from CV {}'.format(time_log()))
        cv_data = self.cv_configlet.get_configlet_data_cv(configlet_name=test_configlet['name'])
        logger.info('Got CV result')
        logger.info('Got all configlet data from CV {}'.format(time_log()))
        logger.debug('CV data for configlet {0} is {1}'.format(test_configlet['name'], to_nice_json(data=cv_data)))
        # Tests
        if test_configlet['is_present_expected']:
            logger.info('Configlet is expected to exist.')
            assert cv_data is not None
            assert type(cv_data) is dict
            logger.info('Configlet has correct format and has data')
        else:
            logger.warning('Configlet is NOT expected to exist.')
            assert cv_data is None
            logger.info('Configlet data is None')

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_configlet_is_present(self, test_configlet, check_mode):
        # Set check mode
        self.cv_configlet._ansible.check_mode = check_mode
        # Work with API
        logger.info('Check if configlet is present on Cloudvision')
        cv_configlet_is_present = self.cv_configlet.is_present(configlet_name=test_configlet['name'])
        logger.info('Got CV result')
        logger.info('Configlet is expected to be present: {}'.format(test_configlet['is_present_expected']))
        # Tests
        assert cv_configlet_is_present == test_configlet['is_present_expected']
        logger.info('State report is correct: {}'.format(cv_configlet_is_present))

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_str_compare(self, test_configlet, check_mode):
        # Set check mode
        self.cv_configlet._ansible.check_mode = check_mode
        # Generate Test data
        python_str_not_equal = (
            test_configlet['config'] != test_configlet['config_expected']
        )
        diff_data = self.cv_configlet._compare(
            fromText=test_configlet['config'],
            toText=test_configlet['config_expected']
            )
        logger.debug('Diff result is: {}'.format(diff_data))
        # Tests
        assert python_str_not_equal is diff_data[0]
        if diff_data[0]:
            logger.info('Diff is : {}'.format(to_nice_json(data=diff_data[1])))
        else:
            logger.info('No diff to display')

    @pytest.mark.create
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_create_configlet(self, test_configlet, check_mode):
        if test_configlet['is_present_expected']:
            logger.warning('Skipped as it is not designed for creation test')
            pytest.skip("Not covered by create scenario")
        # Set check mode
        self.cv_configlet._ansible.check_mode = check_mode
        # Work with API
        logger.info('Start to create configlet on CV')
        api_call = self.cv_configlet.create(to_create=[test_configlet], note='Created by pytest')
        logger.info('Got CV result')
        logger.info('Configlet created on CV')
        logger.debug('API result is: {}'.format(to_nice_json(data=api_call[0].results)))
        # Tests
        assert type(api_call[0] is CvApiResult)
        assert api_call[0].results['success'] is True
        assert api_call[0].results['changed'] is not check_mode

    @pytest.mark.create
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_update_configlet(self, test_configlet, check_mode):
        if test_configlet['is_present_expected'] is False:
            logger.warning('Skipped as it is not designed for update test')
            pytest.skip("Not covered by update scenario")
        # Set check mode
        self.cv_configlet._ansible.check_mode = check_mode
        # Work with API
        #   API Call 1
        logger.info('Start to get configlet data from CV')
        configlet_key = self.cv_configlet.get_configlet_data_cv(configlet_name=test_configlet['name'])['key']
        logger.info('Got CV result')
        #   API Call 2
        configlet = {'name':test_configlet['name'], 'key':configlet_key, 'config': test_configlet['config']}
        logger.info('Start to update configlet data')
        api_call = self.cv_configlet.update(to_update=[configlet], note='Updated by pytest - {}'.format(time_log()))
        logger.info('Got CV result')
        logger.debug('Update - API result is: {}'.format(to_nice_json(data=api_call[0].results)))
        # Tests
        assert type(api_call[0] is CvApiResult)
        assert api_call[0].results['success'] is True
        # Revert content only if check_mode is False
        if check_mode is False:
            configlet = {'name':test_configlet['name'], 'key':configlet_key, 'config': test_configlet['config_expected']}
            api_call = self.cv_configlet.update(to_update=[configlet], note='Updated by pytest - {}'.format(time_log()))
            logger.debug('Revert to expected - API result is: {}'.format(to_nice_json(data=api_call[0].results)))

    @pytest.mark.delete
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_delete_configlet(self, test_configlet, check_mode):
        if test_configlet['is_present_expected']:
            logger.warning('Skipped as it is not designed for delete test')
            pytest.skip("Not covered by delete scenario")
        # Set check mode
        self.cv_configlet._ansible.check_mode = check_mode
        # Work with API
        configlet_key = self.cv_configlet.get_configlet_data_cv(configlet_name=test_configlet['name'])['key']
        configlet = {'name':test_configlet['name'], 'key':configlet_key}
        logger.info('Start to delete configlet on CV')
        api_call = self.cv_configlet.delete(to_delete=[configlet])
        logger.info('Got CV result')
        logger.debug('API result is: {}'.format(to_nice_json(data=api_call[0].results)))
        # Tests
        assert type(api_call[0] is CvApiResult)
        assert api_call[0].results['success'] is not check_mode
        assert api_call[0].results['changed'] is not check_mode

    def test_closing_cv_instance(self, test_configlet, check_mode):
        requests.packages.urllib3.disable_warnings()
        logger.info("Object has been deleted {}".format(time_log()))
        assert True

@pytest.mark.api
@pytest.mark.configlet
@pytest.mark.usefixtures("CvContainerTools_Manager")
@pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
# Parametrize to build a ConfigletInput from list of configlet in SYSTEM_CONFIGLETS_TESTS. Only those set with is_present_expected to False
class Test_CvConfiglet_Manager():

    @pytest.mark.create
    @pytest.mark.delete
    @pytest.mark.dependency(name='authentication')
    @pytest.mark.parametrize("configlet_inventory", generate_CvConfigletTools_content(configlet_inputs=SYSTEM_CONFIGLETS_TESTS, is_present_state=True), ids=['configlets-already-declared'])
    def test_cv_connection(self, configlet_inventory):
        requests.packages.urllib3.disable_warnings()
        logger.debug(str("Class is connected to CV"))
        assert True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("configlet_inventory", generate_CvConfigletTools_content(configlet_inputs=SYSTEM_CONFIGLETS_TESTS, is_present_state=True), ids=['configlets-already-declared'])
    def test_configlet_local_inventory(self, configlet_inventory):
        logger.debug('Local configlet input: \n{}'.format(configlet_inventory))
        assert True

    @pytest.mark.create
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("configlet_inventory", generate_CvConfigletTools_content(configlet_inputs=SYSTEM_CONFIGLETS_TESTS, is_present_state=False), ids=['configlets-to-create'])
    def test_apply_present_create(self, configlet_inventory):
        inventory = ConfigletInput(user_topology=configlet_inventory)
        assert inventory.is_valid
        logger.info('Configlet inventory is valid, continuing...')
        api_result = self.cv_configlet.apply(
            configlet_list=inventory.configlets,
            present=True,
            note='Updated by pytest - {}'.format(time_log()))
        logger.debug('API call response is: {}'.format(to_nice_json(data=api_result.content)))
        assert api_result.content['configlets_created']['success'] == True
        assert len(configlet_inventory) == int(api_result.content['configlets_created']['configlets_created_count'])

    @pytest.mark.create
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("configlet_inventory", generate_CvConfigletTools_content(configlet_inputs=SYSTEM_CONFIGLETS_TESTS, is_present_state=True), ids=['configlets-to-update'])
    def test_apply_present_update(self, configlet_inventory):
        inventory = ConfigletInput(user_topology=configlet_inventory)
        assert inventory.is_valid
        logger.info('Configlet inventory is valid, continuing...')
        api_result = self.cv_configlet.apply(
            configlet_list=inventory.configlets,
            present=True,
            note='Updated by pytest - {}'.format(time_log()))
        logger.debug('API call response is: {}'.format(to_nice_json(data=api_result.content)))
        assert api_result.content['configlets_updated']['success'] == True
        assert len(configlet_inventory) == int(api_result.content['configlets_updated']['configlets_updated_count'])

    @pytest.mark.delete
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.parametrize("configlet_inventory", generate_CvConfigletTools_content(configlet_inputs=SYSTEM_CONFIGLETS_TESTS, is_present_state=False), ids=['configlet-to-delete'])
    def test_apply_delete(self, configlet_inventory):
        self.provisioner.configlets_push(configlets=configlet_inventory)
        inventory = ConfigletInput(user_topology=configlet_inventory)
        assert inventory.is_valid
        logger.info('Configlet inventory is valid, continuing...')
        api_result = self.cv_configlet.apply(
            configlet_list=inventory.configlets,
            present=False,
            note='Updated by pytest - {}'.format(time_log()))
        logger.debug('API call response is: {}'.format(to_nice_json(data=api_result.content)))
        assert api_result.content['configlets_deleted']['success'] == True
        assert len(configlet_inventory) == int(api_result.content['configlets_deleted']['configlets_deleted_count'])

    def test_closing_cv_instance(self):
        requests.packages.urllib3.disable_warnings()
        logger.info("Object has been deleted {}".format(time_log()))
        assert True
