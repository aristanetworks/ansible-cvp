#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import pytest
import pprint
from ansible_collections.arista.cvp.plugins.module_utils.facts_tools import CvFactsTools
from tests.lib import mock, mock_ansible
from tests.data import facts_unit
from tests.lib.parametrize import generate_list_from_dict
from tests.lib.helpers import setup_custom_logger
from tests.lib.utils import generate_test_ids_dict

LOGGER = setup_custom_logger(__name__)

# ---------------------------------------------------------------------------- #
#   FIXTURES
# ---------------------------------------------------------------------------- #

@pytest.fixture
def cvp_database():
    database = mock.MockCVPDatabase(
        devices=facts_unit.MOCKDATA_DEVICES,
        configlets=facts_unit.MOCKDATA_CONFIGLETS,
        containers=facts_unit.MOCKDATA_CONTAINERS,
        configlets_mappers=facts_unit.MOCKDATA_CONFIGLET_MAPPERS
    )
    yield database
    LOGGER.debug('Final CVP state: %s', database)


@pytest.fixture()
def fact_unit_tools(request, cvp_database):
    cvp_client = mock.get_cvp_client(cvp_database)
    instance = CvFactsTools(cv_connection=cvp_client)
    LOGGER.debug('Initial CVP state: %s', cvp_database)
    yield instance
    LOGGER.debug('Mock calls: %s', pprint.pformat(cvp_client.mock_calls))


# ---------------------------------------------------------------------------- #
#   TEST CASES
# ---------------------------------------------------------------------------- #

# CvFactsTools.__get_container_name

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("container_def", generate_list_from_dict(facts_unit.MOCKDATA_CONTAINERS), ids=generate_test_ids_dict)
def test_CvFactsTools__get_container_name(fact_unit_tools, container_def):
    result = fact_unit_tools._CvFactsTools__get_container_name(key=container_def[mock.MockCVPDatabase.FIELD_KEY])
    LOGGER.info('facts_tool response: %s', str(result))
    assert result == container_def['name']
    LOGGER.info('Container name for id %s is %s', str(container_def[mock.MockCVPDatabase.FIELD_KEY]), str(result))

# CvFactsTools.__configletIds_to_configletName

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("configlet_def", facts_unit.MOCKDATA_CONFIGLET_MAPPERS['data']['configlets'], ids=generate_test_ids_dict)
def test_CvFactsTools__configletIds_to_configletName(fact_unit_tools, configlet_def):
    LOGGER.info('** Sending request to get name for configlet ID: %s', str(configlet_def[mock.MockCVPDatabase.FIELD_KEY]))
    result = fact_unit_tools._CvFactsTools__configletIds_to_configletName(configletIds=[configlet_def[mock.MockCVPDatabase.FIELD_KEY]])
    LOGGER.info('** facts_tool response: %s', str(result))
    assert configlet_def['name'] in result
    LOGGER.info('Configlet name for id %s is %s', str(configlet_def[mock.MockCVPDatabase.FIELD_KEY]), str(result))

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
def test_CvFactsTools__configletIds_to_configletName_empty(fact_unit_tools):
    LOGGER.info('** Sending request to get name for configlet ID: None')
    result = fact_unit_tools._CvFactsTools__configletIds_to_configletName(configletIds=[])
    LOGGER.info('** facts_tool response: %s', str(result))
    assert result == []
    LOGGER.info('Configlet name for id [] is %s', str(result))

# CvFactsTools.__device_get_configlets

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("device_def", facts_unit.MOCKDATA_DEVICES, ids=generate_test_ids_dict)
def test_CvFactsTools__device_get_configlets_with_configlets(fact_unit_tools, device_def):
    LOGGER.info('** Sending request to get configlets name for device name: %s', str(device_def['hostname']))
    result = fact_unit_tools._CvFactsTools__device_get_configlets(netid=device_def['systemMacAddress'])
    LOGGER.info('** facts_tool response: %s', str(result))
    if device_def['systemMacAddress'] in [x['objectId'] for x in facts_unit.MOCKDATA_CONFIGLET_MAPPERS['data']['configletMappers']]:
        assert len(result) > 0
        LOGGER.info('Device name %s has configlets %s attached', str(device_def['hostname']), str(result))
    else:
        pytest.skip("skipping DEVICES with no configlet")

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("device_def", facts_unit.MOCKDATA_DEVICES, ids=generate_test_ids_dict)
def test_CvFactsTools__device_get_configlets_no_configlet(fact_unit_tools, device_def):
    LOGGER.info('** Sending request to get configlets name for device name: %s', str(device_def['hostname']))
    result = fact_unit_tools._CvFactsTools__device_get_configlets(netid=device_def['systemMacAddress'])
    LOGGER.info('** facts_tool response: %s', str(result))
    if device_def['systemMacAddress'] not in [x['objectId'] for x in facts_unit.MOCKDATA_CONFIGLET_MAPPERS['data']['configletMappers']]:
        assert len(result) == 0
        LOGGER.info('Device has no configlet configured as expected')
    else:
        pytest.skip("skipping DEVICES with configlet(s)")

# CvFactsTools.__device_get_configlets

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("container_def", generate_list_from_dict(facts_unit.MOCKDATA_CONTAINERS), ids=generate_test_ids_dict)
def test_CvFactsTools__device_get_configlets_with_configlets(fact_unit_tools, container_def):
    LOGGER.info('** Sending request to get configlets name for device name: %s', str(container_def[mock.MockCVPDatabase.FIELD_NAME]))
    result = fact_unit_tools._CvFactsTools__containers_get_configlets(container_id=container_def[mock.MockCVPDatabase.FIELD_KEY])
    LOGGER.info('** facts_tool response: %s', str(result))
    if container_def[mock.MockCVPDatabase.FIELD_KEY] in [(x['objectId'], x['containerId']) for x in facts_unit.MOCKDATA_CONFIGLET_MAPPERS['data']['configletMappers']]:
        assert len(result) > 0
        LOGGER.info('Container name for id %s has configlets %s attached', str(container_def[mock.MockCVPDatabase.FIELD_NAME]), str(result))
    else:
        pytest.skip("skipping CONTAINER with no configlet")

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("container_def", generate_list_from_dict(facts_unit.MOCKDATA_CONTAINERS), ids=generate_test_ids_dict)
def test_CvFactsTools__device_get_configlets_with_no_configlets(fact_unit_tools, container_def):
    LOGGER.info('** Sending request to get configlets name for device name: %s', str(container_def[mock.MockCVPDatabase.FIELD_NAME]))
    result = fact_unit_tools._CvFactsTools__containers_get_configlets(container_id=container_def[mock.MockCVPDatabase.FIELD_KEY])
    LOGGER.info('** facts_tool response: %s', str(result))
    if container_def[mock.MockCVPDatabase.FIELD_KEY] in [(x['objectId'], x['containerId']) for x in facts_unit.MOCKDATA_CONFIGLET_MAPPERS['data']['configletMappers']]:
        assert len(result) == 0
        LOGGER.info('Container name %s has no configlets %s attached', str(container_def[mock.MockCVPDatabase.FIELD_NAME]), str(result))
    else:
        pytest.skip("skipping CONTAINER with configlet(s)")


# CvFactsTools.__device_update_info

@pytest.mark.generic
@pytest.mark.facts
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("device_def", facts_unit.MOCKDATA_DEVICES, ids=generate_test_ids_dict)
def test_CvFactsTools__device_get_configlets_no_configlet(fact_unit_tools, device_def):
    LOGGER.info('** Sending request to get update device info for: %s', str(device_def['hostname']))
    result = fact_unit_tools._CvFactsTools__device_update_info(device=device_def)
    LOGGER.info('Updated device information: %s', str(result))
    assert mock.MockCVPDatabase.FIELD_PARENT_NAME in result
    if device_def['parentContainerKey'] != '':
        assert result[mock.MockCVPDatabase.FIELD_PARENT_NAME] in [x['name'] for x in generate_list_from_dict(facts_unit.MOCKDATA_CONTAINERS)]
        LOGGER.info('Device is attached to container %s', str(result[mock.MockCVPDatabase.FIELD_PARENT_NAME]))
    else:
        LOGGER.warning('Device is not attached to any container')
