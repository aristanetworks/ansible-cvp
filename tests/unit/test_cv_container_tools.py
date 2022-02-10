#!/usr/bin/python
# coding: utf-8 -*-

import logging
import pytest
import pprint
from ansible_collections.arista.cvp.plugins.module_utils.container_tools import CvContainerTools
from ansible_collections.arista.cvp.plugins.module_utils.resources.exceptions import AnsibleCVPApiError, AnsibleCVPNotFoundError
from tests.lib import mock, mock_ansible
from tests.data import container_tools_unit as data

LOGGER = logging.getLogger(__name__)


CVP_DATA_CONTAINERS_INIT = {
    'Tenant': {
        'name': 'Tenant',
        'key': 'root',
        'parentContainerId': None}
}

# ---------------------------------------------------------------------------- #
#   FIXTURES
# ---------------------------------------------------------------------------- #

@pytest.fixture
def cvp_database(request):
    database = mock.MockCVPDatabase()
    if hasattr(request, 'param'):
        database.devices.update(request.param.get('devices', []))
        database.containers.update(request.param.get('containers', []))
        database.configlets.update(request.param.get('configlets', []))
    LOGGER.info('Initial CVP state: %s', database)
    yield database
    LOGGER.info('Final CVP state: %s', database)


@pytest.fixture(params=[False], ids=['check mode off'])
def container_tools(request, cvp_database):
    cvp_client = mock.get_cvp_client(cvp_database)
    module = mock_ansible.get_ansible_module(check_mode=request.param)
    instance = CvContainerTools(cv_connection=cvp_client, ansible_module=module)
    yield instance
    LOGGER.debug('Mock calls: %s', pprint.pformat(cvp_client.mock_calls))


# ---------------------------------------------------------------------------- #
#   TEST CASES
# ---------------------------------------------------------------------------- #

# build_topology()
@pytest.mark.generic
@pytest.mark.parametrize("present, apply_mode, cvp_database, user_topology, expected_response", data.USER_TOPOLOGY, indirect=["cvp_database"])
def test_build_topology(container_tools, present, apply_mode, user_topology, expected_response):
    LOGGER.info('User topology: %s', user_topology)
    response = container_tools.build_topology(user_topology, present=present, apply_mode=apply_mode)
    assert response.content == expected_response


# get_container_id()
@pytest.mark.generic
@pytest.mark.parametrize("cvp_database, name, expected_id", data.TEST_CONTAINERS, indirect=["cvp_database"])
def test_get_container_id(container_tools, name, expected_id):
    container_id = container_tools.get_container_id(container_name=name)
    assert container_id == expected_id


@pytest.mark.generic
def test_get_container_id_not_found(container_tools):
    with pytest.raises(AnsibleCVPNotFoundError):
        container_tools.get_container_id(container_name='notExist')


@pytest.mark.generic
@pytest.mark.parametrize("cvp_database", [{'containers': {
    mock.MockCVPDatabase.BAD_KEY: {mock.MockCVPDatabase.BAD_KEY: 'container_1234abcd-1234-abcd-12ab-123456abcdef',
                                   'name': 'unit-test-1',
                                   'parentContainerId': 'root'}
}
}], indirect=["cvp_database"])
def test_get_container_id_bad_key(container_tools):
    with pytest.raises(AnsibleCVPApiError):
        # Use a special container name to mimic bad API response
        container_tools.get_container_id(container_name=mock.MockCVPDatabase.BAD_KEY)
