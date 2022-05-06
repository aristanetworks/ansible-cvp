#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

from __future__ import (absolute_import, division, print_function)
import logging
import pytest
from tests.lib.utils import cvp_login
from ansible_collections.arista.cvp.plugins.module_utils import api

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def api_client():
    client = cvp_login()
    return client


# ---------------------------------------------------------------------------- #
#   TESTS Management
# ---------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.dependency(name='authentication')
def test_get_configlets(api_client):
    r = api.get_configlets(api_client)
    assert 'data' in r


@pytest.mark.api
@pytest.mark.dependency(name='authentication')
def test_get_images(api_client):
    r = api.get_images(api_client)
    assert 'data' in r


@pytest.mark.api
@pytest.mark.dependency(name='authentication')
def test_get_containers(api_client):
    r = api.get_containers(api_client)
    assert 'data' in r


@pytest.mark.api
@pytest.mark.dependency(name='authentication')
def test_get_images_and_configlets(api_client):
    r = api.get_images_and_configlets(api_client)
    assert 'data' in r[0] and 'data' in r[1]


@pytest.mark.api
@pytest.mark.dependency(name='authentication')
def test_get_configlets_by_name(api_client):
    r1 = api.get_configlets(api_client)
    names = []
    for c in r1['data']:
        names.append(c['name'])
    r2 = api.get_configlets_by_name(api_client, names)
    assert r1['total'] == len(r2)


@pytest.mark.api
@pytest.mark.dependency(name='authentication')
def test_update_configlets(api_client):
    r1 = api.get_configlets(api_client)
    names = []
    for c in r1['data']:
        names.append(c['name'])
    r2 = api.get_configlets_by_name(api_client, names)
    configs = []
    for c in r2:
        configs.append({'name': c['name'],
                        'key': c['key'],
                        'config': c['config']})
    r3 = api.update_configlets(api_client, configs)
    assert r1['total'] == len(r3)


@pytest.mark.api
@pytest.mark.dependency(name='authentication')
def test_add_notes_to_configlets(api_client):
    r1 = api.get_configlets(api_client)
    names = []
    for c in r1['data']:
        names.append(c['name'])
    r2 = api.get_configlets_by_name(api_client, names)
    notes = []
    for c in r2:
        notes.append({'key': c['key'],
                      'note': c['note']})
    r3 = api.add_notes_to_configlets(api_client, notes)
    assert r1['total'] == len(r3)
