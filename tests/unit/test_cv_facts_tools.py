#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import logging
import pytest
import pprint
from ansible_collections.arista.cvp.plugins.module_utils.facts_tools import CvFactsTools
from ansible_collections.arista.cvp.plugins.module_utils.fields import FIELD_FACTS_DEVICE, FIELD_FACTS_CONFIGLET, FIELD_FACTS_CONTAINER
from tests.lib import mock
from tests.unit import data
from tests.lib.helpers import setup_custom_logger
from tests.lib.utils import generate_test_ids_dict, generate_test_ids_list
# from tests.lib.cvaas_facts import FACTS_CONTAINERS_TEST, FACT_DEVICE_TEST, FACT_FILTER_TEST

LOGGER = setup_custom_logger(__name__)

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE
# ---------------------------------------------------------------------------- #

def generate_flat_data_from_dict(data):
    """
    generate_flat_data Generate a flat list of dict

    Example
    -------
    >>> CUSTOMER_CVP_CONTAINER_TOPOLOGY = {"Tenant":{"name":"Tenant","key":"root","parentContainerId":"None"},"Undefined":{"name":"Undefined","key":"undefined_container","parentContainerId":"root"}}

    >>> result = generate_flat_data(CUSTOMER_CVP_CONTAINER_TOPOLOGY)

    >>> print(result)
    [{"name":"Tenant","key":"root","parentContainerId":"None"},{"name":"Undefined","key":"undefined_container","parentContainerId":"root"}]

    Parameters
    ----------
    data : dict
        Data to transform

    Returns
    -------
    list
        List extracted from the dict
    """
    return [dict(data[d].items()) for d in data]


# ---------------------------------------------------------------------------- #
#   FIXTURES
# ---------------------------------------------------------------------------- #

@pytest.fixture
def cvp_database():
    database = mock.MockCVPDatabase()
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

@pytest.mark.generic
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("container_def", generate_flat_data_from_dict(mock.MockCVPDatabase.CVP_DATA_CONTAINERS_INIT), ids=generate_test_ids_dict)
def test_CvFactsTools__get_container_name(fact_unit_tools, container_def):
    result = fact_unit_tools._CvFactsTools__get_container_name(key=container_def[mock.MockCVPDatabase.FIELD_KEY])
    LOGGER.debug('facts_tool response: %s', str(result))
    assert result == container_def['name']
    LOGGER.info('Container name for id %s is %s', str(container_def[mock.MockCVPDatabase.FIELD_KEY]), str(result))

@pytest.mark.generic
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.parametrize("configlet_def", mock.MockCVPDatabase.CVP_DATA_CONFIGLETS_MAPPERS_INIT['data']['configlets'], ids=generate_test_ids_list)
def test_CvFactsTools__configletIds_to_configletName(fact_unit_tools, configlet_def):
    LOGGER.info('** Sending request to get name for configlet ID: %s', str(configlet_def[mock.MockCVPDatabase.FIELD_KEY]))
    result = fact_unit_tools._CvFactsTools__configletIds_to_configletName(configletIds=[configlet_def[mock.MockCVPDatabase.FIELD_KEY]])
    LOGGER.info('** facts_tool response: %s', str(result))
    assert configlet_def['name'] in result
    LOGGER.info('Configlet name for id %s is %s', str(configlet_def[mock.MockCVPDatabase.FIELD_KEY]), str(result))

@pytest.mark.generic
@pytest.mark.usefixtures("fact_unit_tools")
@pytest.mark.usefixtures("cvp_database")
def test_CvFactsTools__configletIds_to_configletName_empty(fact_unit_tools):
    LOGGER.info('** Sending request to get name for configlet ID: None')
    result = fact_unit_tools._CvFactsTools__configletIds_to_configletName(configletIds=[])
    LOGGER.info('** facts_tool response: %s', str(result))
    assert  result == []
    LOGGER.info('Configlet name for id [] is %s', str(result))
