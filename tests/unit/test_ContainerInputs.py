#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import sys
from datetime import datetime
import logging
import pytest
sys.path.append("../")
sys.path.append("../../")
from ansible_collections.arista.cvp.plugins.module_utils.container_tools import ContainerInput, FIELD_PARENT_NAME


# pytest - -html = report.html - -self-contained-html - -cov = . --cov-report = html - -color yes containerInputs.py - v

CVP_CONTAINERS_3_LEVELS = {"DC2": {"parentContainerName": "Tenant"}, "Leafs": {"parentContainerName": "DC2"}, "Spines": {
    "parentContainerName": "DC2", "configlets": ["01TRAINING-01"]}, "POD01": {"parentContainerName": "Leafs"}}

CVP_CONTAINERS_2_LEVELS = {"DC2": {"parentContainerName": "Tenant"}, "Leafs": {
    "parentContainerName": "DC2"}, "Spines": {"parentContainerName": "DC2", "configlets": ["01TRAINING-01"]}}

CVP_CONTAINERS_1_LEVELS = {"DC2": {"parentContainerName": "Tenant"}}

CVP_CONTAINERS_01 = {"DC-2": {"parentContainerName": "Tenant"}, "Leafs": {
    "parentContainerName": "DC-2"}}


# Generic helpers
def time_log():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

def get_cv_container_definition():
    return [CVP_CONTAINERS_1_LEVELS, CVP_CONTAINERS_2_LEVELS, CVP_CONTAINERS_3_LEVELS, CVP_CONTAINERS_01]


# ---------------------------------------------------------------------------- #
#   FIXTURES Management
# ---------------------------------------------------------------------------- #

@pytest.fixture()
@pytest.mark.parametrize('CVP_CONTAINER', get_cv_container_definition())
def ContainerInput_Creation(request, CVP_CONTAINER):
    logging.info("Execute fixture to create class elements")
    request.cls.inventory = ContainerInput(user_topology=CVP_CONTAINER)
    yield
    logging.info("Execute fixture to close object")

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #

@pytest.mark.parametrize('CVP_CONTAINER', get_cv_container_definition())
@pytest.mark.usefixtures("ContainerInput_Creation")
@pytest.mark.generic
class TestContainerInput():
    def test_display_input(self, CVP_CONTAINER):
        logging.debug(str(CVP_CONTAINER))
        assert True

    def test_is_valid(self, CVP_CONTAINER):
        assert self.inventory.is_valid
        logging.info('Format is valid against JSON schema')

    def test_get_parent_root(self, CVP_CONTAINER):
        for cnt_name, cnt in CVP_CONTAINER.items():
            parent_name = self.inventory.get_parent(container_name=cnt_name)
            assert parent_name == cnt[FIELD_PARENT_NAME]
            logging.info(
                'Get correct parent name for sub-root container: {} under {}'.format(cnt_name, parent_name))

    def test_ordered_list(self, CVP_CONTAINER):
        ordered_list = self.inventory.ordered_list_containers
        for entry_name, entry in CVP_CONTAINER.items():
            assert entry_name in ordered_list
            logging.info('{} is in list of containers: {}'.format(entry_name, ordered_list))
            if entry['parentContainerName'] != 'Tenant':
                assert ordered_list.index(entry_name) > ordered_list.index(
                    entry['parentContainerName'])
                logging.info('Parent container {} is configured before container {}'.format(entry['parentContainerName'], entry_name))

    def test_ordered_list_root(self, CVP_CONTAINER):
        ordered_list = self.inventory.ordered_list_containers
        for entry_name, entry in CVP_CONTAINER.items():
            if entry['parentContainerName'] == 'Tenant':
                assert ordered_list.index(entry_name) == 0
                logging.info('Container {} is attached to root container {}'.format(
                    entry_name, entry['parentContainerName']))

    def test_has_configlets(self, CVP_CONTAINER):
        for entry_name, entry in CVP_CONTAINER.items():
            if 'configlets' in entry.keys():
                assert self.inventory.has_configlets(container_name=entry_name)
                logging.info('Container {} has configlets as expected'.format(entry_name))
            else:
                assert self.inventory.has_configlets(container_name=entry_name) is False
                logging.info(
                    'Container {} has NO configlets as expected'.format(entry_name))

    def test_get_configlets(self, CVP_CONTAINER):
        for entry_name, entry in CVP_CONTAINER.items():
            if 'configlets' in entry.keys():
                assert self.inventory.get_configlets(container_name=entry_name) == entry['configlets']
                logging.info('Container {} has following configlets: {}'.format(
                    entry_name, self.inventory.get_configlets(container_name=entry_name)))
