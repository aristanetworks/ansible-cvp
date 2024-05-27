#!/usr/bin/python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import logging
import pytest
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse
from tests.lib.parametrize import generate_cv_response_api_action_name, generate_cv_response_result_manager_name

# TODO - use f-strings
# pylint: disable=consider-using-f-string

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #

@pytest.mark.generic
class TestCvReponseAction():
    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    def test_api_result_creation(self, api_results_name):
        api_result = CvApiResult(action_name=api_results_name)
        assert api_result.name == api_results_name

    @pytest.mark.generic
    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    def test_api_flags(self, api_results_name):
        api_result = CvApiResult(action_name=api_results_name)
        assert api_result.changed is False
        assert api_result.success is False
        api_result.success = True
        api_result.changed = True
        assert api_result.changed
        assert api_result.success
        logging.info("API struct result is {}".format(api_result.results))

    @pytest.mark.generic
    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    def test_api_add_action(self, api_results_name):
        api_result = CvApiResult(action_name=api_results_name)
        assert api_result.count == 0
        api_result.add_entry(entry="action1")
        assert api_result.count == 1
        api_result.add_entry(entry="action2")
        assert api_result.count == 2
        api_result.add_entry(entry="action3")
        assert api_result.count == 3
        logging.info("API struct result is {}".format(api_result.results))

    @pytest.mark.generic
    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    def test_api_add_actions(self, api_results_name):
        api_result = CvApiResult(action_name=api_results_name)
        assert api_result.count == 0
        api_result.add_entries(entries=["action1", "action2"])
        assert api_result.count == 2
        logging.info("API struct result is {}".format(api_result.results))

    @pytest.mark.generic
    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    def test_api_generate_cv_response_actions(self, api_results_name):
        api_result = CvApiResult(action_name=api_results_name)
        api_result.add_entries(entries=["action1", "action2"])
        api_result.add_entry(entry="action3")
        assert len(api_result.list_changes) == 3
        for entry in api_result.list_changes:
            assert entry in ["action1", "action2", "action3"]
        logging.info("API struct result is {}".format(api_result.results))

    @pytest.mark.generic
    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    def test_api_generate_cv_response_results(self, api_results_name):
        api_result = CvApiResult(action_name=api_results_name)
        api_result.success = True
        api_result.changed = True
        api_result.add_entries(entries=["action1", "action2"])
        api_result.add_entry(entry="action3")
        assert api_result.results["success"]
        assert api_result.results["changed"]
        assert api_result.results[api_results_name+"_count"] == 3
        assert len(api_result.results[api_results_name+"_list"]) == 3
        logging.info("API strct result is {}".format(api_result.results))


@pytest.mark.generic
class TestCvReponseManager():

    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    @pytest.mark.parametrize("management_name", generate_cv_response_result_manager_name())
    @pytest.mark.generic
    def test_manager_create(self, api_results_name, management_name):
        api_manager = CvManagerResult(builder_name=management_name)
        assert api_manager.name == management_name
        logging.info("API strct result is {}".format(api_manager.changes))

    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    @pytest.mark.parametrize("management_name", generate_cv_response_result_manager_name())
    @pytest.mark.generic
    def test_manager_flags(self, api_results_name, management_name):
        api_manager = CvManagerResult(builder_name="TEST_BUILDER")
        assert api_manager.changed is False
        assert api_manager.success is False
        logging.info("API Manager strct result is {}".format(
            api_manager.changes))

    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    @pytest.mark.parametrize("management_name", generate_cv_response_result_manager_name())
    @pytest.mark.generic
    def test_manager_add_actions(self, api_results_name, management_name):
        api_manager = CvManagerResult(builder_name=management_name)
        api_result = CvApiResult(action_name=api_results_name)
        api_result.add_entries(entries=["action1", "action2"])
        api_result.add_entry(entry="action3")
        api_result.success = True
        api_manager.add_change(change=api_result)
        assert api_manager.success
        assert int(api_manager.changes[management_name+"_count"]) == 3
        assert api_manager.changes[management_name +
                                   "_list"] == [api_results_name]
        logging.info("API Manager strct result is {}".format(
            api_manager.changes))


@pytest.mark.generic
class TestCvReponseAnsible():
    @pytest.mark.generic
    def test_ansible_response_creation(self):
        ansible_output = CvAnsibleResponse()
        assert ansible_output.content["success"] is False
        assert ansible_output.content["changed"] is False
        logging.info("Ansible response strct result is {}".format(
            ansible_output.content))

    @pytest.mark.parametrize("api_results_name", generate_cv_response_api_action_name())
    @pytest.mark.parametrize("management_name", generate_cv_response_result_manager_name())
    @pytest.mark.generic
    def test_ansible_response_add(self, api_results_name, management_name):
        ansible_output = CvAnsibleResponse()
        api_action = CvApiResult(action_name="API_TEST")
        api_action.add_entry("Fake run")
        api_action.changed = True
        api_action.success = True
        api_manager = CvManagerResult(builder_name="API_BUILDER")
        api_manager.add_change(change=api_action)
        ansible_output.add_manager(api_manager=api_manager)
        assert ansible_output.content["success"]
        assert ansible_output.content["changed"]
        assert len(
            ansible_output.content["API_BUILDER"]["API_BUILDER_list"]) == 1
        assert len(ansible_output.content["API_BUILDER"]["API_BUILDER_list"]
                   ) == ansible_output.content["API_BUILDER"]["API_BUILDER_count"]
        logging.info("Ansible response strct result is {}".format(
            ansible_output.content))
