#!/usr/bin/python
# coding: utf-8 -*-

import logging
import pytest
import pprint
from ansible_collections.arista.cvp.plugins.module_utils.container_tools import CvContainerTools
from tests.lib import mock
from tests.unit import data

LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------- #
#   FIXTURES
# ---------------------------------------------------------------------------- #

@pytest.fixture
def cvp_database():
    database = mock.MockCVPDatabase()
    yield database
    LOGGER.info('Final CVP state: %s', database)


@pytest.fixture(params=[False], ids=['check mode off'])  # Fixture parameter is Ansible check_mode
def container_tools(request, cvp_database):
    cvp_client = mock.get_cvp_client(cvp_database)
    module = mock.get_ansible_module(check_mode=request.param)
    instance = CvContainerTools(cv_connection=cvp_client, ansible_module=module)
    LOGGER.info('Initial CVP state: %s', cvp_database)
    yield instance
    LOGGER.debug('Mock calls: %s', pprint.pformat(cvp_client.mock_calls))


# ---------------------------------------------------------------------------- #
#   TEST CASES
# ---------------------------------------------------------------------------- #

# build_topology()
@pytest.mark.generic
@pytest.mark.parametrize("present, apply_mode, cvp_data, user_topology, expected_response", data.USER_TOPOLOGY)
def test_build_topology(cvp_database, container_tools, present, apply_mode, cvp_data, user_topology, expected_response):
    cvp_database.devices.update(cvp_data.get('devices', []))
    cvp_database.containers.update(cvp_data.get('containers', []))
    cvp_database.configlets.update(cvp_data.get('configlets', []))
    LOGGER.info('Initial CVP state: %s', cvp_database)
    LOGGER.info('User topology: %s', user_topology)
    response = container_tools.build_topology(user_topology, present=present, apply_mode=apply_mode)
    assert response.content == expected_response
