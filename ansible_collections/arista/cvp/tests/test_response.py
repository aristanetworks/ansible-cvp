#!/usr/bin/python
# coding: utf-8 -*-


from __future__ import (absolute_import, division, print_function)
import sys
import pytest
sys.path.append("../../../../")
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse   # noqa # pylint: disable=unused-import


# @pytest.mark.parametrize("api_action_name", ["","a","action","action_test",])

@pytest.mark.parametrize("api_action_name", ["", "a", "action", "action_test", "action test"])
def test_api_result_creation(api_action_name):
    api_result = CvApiResult(action_name=api_action_name)
    assert api_result.name == api_action_name

def test_api_flags():
    api_result = CvApiResult(action_name='TEST_FLAG')
    assert api_result.changed is False
    assert api_result.success is False
    api_result.success = True
    api_result.changed = True
    assert api_result.changed
    assert api_result.success

def test_api_add_action():
    api_result = CvApiResult(action_name='TEST')
    assert api_result.count == 0
    api_result.add_entry(entry='action1')
    assert api_result.count == 1
    api_result.add_entry(entry='action2')
    assert api_result.count == 2
    api_result.add_entry(entry='action3')
    assert api_result.count == 3

def test_api_add_actions():
    api_result = CvApiResult(action_name='TEST')
    assert api_result.count == 0
    api_result.add_entries(entries=['action1', 'action2'])
    assert api_result.count == 2

def test_api_get_actions():
    api_result = CvApiResult(action_name='TEST')
    api_result.add_entries(entries=['action1', 'action2'])
    api_result.add_entry(entry='action3')
    assert len(api_result.list_changes) == 3
    for entry in api_result.list_changes:
        assert entry in ['action1', 'action2', 'action3']

def test_api_get_results():
    api_result = CvApiResult(action_name='TEST')
    api_result.success = True
    api_result.changed = True
    api_result.add_entries(entries=['action1', 'action2'])
    api_result.add_entry(entry='action3')
    assert api_result.results['success']
    assert api_result.results['changed']
    assert api_result.results['TEST_count'] == 3
    assert len(api_result.results['TEST_list']) == 3


@pytest.mark.parametrize("api_results_name", ["", "a", "action", "action_test", "action test"])
def test_manager_create(api_results_name):
    api_manager = CvManagerResult(builder_name=api_results_name)
    assert api_manager.name == api_results_name

def test_manager_flags():
    api_manager = CvManagerResult(builder_name='TEST_BUILDER')
    assert api_manager.changed is False
    assert api_manager.success is False

def test_manager_add_actions():
    ACTION_NAME = 'TEST'
    MANAGER_NAME = 'TEST_BUILDER'
    api_manager = CvManagerResult(builder_name=MANAGER_NAME)
    api_result = CvApiResult(action_name=ACTION_NAME)
    api_result.add_entries(entries=['action1', 'action2'])
    api_result.add_entry(entry='action3')
    api_result.success = True
    api_manager.add_change(change=api_result)
    assert api_manager.success
    assert int(api_manager.changes[MANAGER_NAME+'_count']) == 3
    assert api_manager.changes[MANAGER_NAME+'_list'] == [ACTION_NAME]

def test_ansible_response_creation():
    ansible_output = CvAnsibleResponse()
    assert ansible_output.content['success'] is False
    assert ansible_output.content['changed'] is False


def test_ansible_response_add():
    ansible_output = CvAnsibleResponse()
    api_action = CvApiResult(action_name='API_TEST')
    api_action.add_entry('Fake run')
    api_action.changed = True
    api_action.success = True
    api_manager = CvManagerResult(builder_name='API_BUILDER')
    api_manager.add_change(change=api_action)
    ansible_output.add_manager(api_manager=api_manager)
    assert ansible_output.content['success']
    assert ansible_output.content['changed']
    assert len(ansible_output.content['API_BUILDER']['API_BUILDER_list']) == 1
    assert len(ansible_output.content['API_BUILDER']['API_BUILDER_list']
               ) == ansible_output.content['API_BUILDER']['API_BUILDER_count']
    print('{}'.format(ansible_output.content))
