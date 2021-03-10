#!/usr/bin/python
# coding: utf-8 -*-


from __future__ import (absolute_import, division, print_function)
import sys
import pytest
sys.path.append("../../../../")
from cvprac.cvp_client import CvpClient   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult   # noqa # pylint: disable=unused-import


# @pytest.mark.parametrize("api_action_name", ["","a","action","action_test",])

@pytest.mark.parametrize("api_action_name", ["", "a", "action", "action_test", "action test"])
def test_api_result_creation(api_action_name):
    api_result = CvApiResult(action_name=api_action_name)
    assert api_result.name == api_action_name

def test_api_flags():
    api_result = CvApiResult(action_name='TEST_FLAG')
    assert api_result.changed is not False
    assert api_result.success is not False
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
