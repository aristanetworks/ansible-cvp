#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
import logging
from ansible_collections.arista.cvp.plugins.module_utils.schema_v3 import validate_cv_inputs
from ansible_collections.arista.cvp.plugins.module_utils.schema_v3 import SCHEMA_CV_CONTAINER, SCHEMA_CV_DEVICE
import pytest

# pytest - -html = report.html - -self-contained-html - -cov = . --cov-report = html - -color yes containerInputs.py - v

CV_CONTAINERS_OK = [
    {"PYTEST": {"parentContainerName": "Tenant"}, "Leafs": {"parentContainerName": "PYTEST"}, "Spines": {
        "parentContainerName": "PYTEST", "configlets": ["01TRAINING-01"]}, "POD01": {"parentContainerName": "Leafs"}},
    {"DC-2": {"parentContainerName": "Tenant"}, "DC_Leafs": {
        "parentContainerName": "DC-2"}},
    {"DC1_BL1": {"parentContainerName": "DC1_L3LEAFS"}, "DC1_FABRIC": {"parentContainerName": "Tenant"}, "DC1_L2LEAF1": {"parentContainerName": "DC1_L2LEAFS"}, "DC1_L2LEAF2": {"parentContainerName": "DC1_L2LEAFS"}, "DC1_L2LEAFS": {"parentContainerName": "DC1_FABRIC"}, "DC1_L3LEAFS": {
        "parentContainerName": "DC1_FABRIC"}, "DC1_LEAF1": {"parentContainerName": "DC1_L3LEAFS"}, "DC1_LEAF2": {"parentContainerName": "DC1_L3LEAFS"}, "DC1_LEAF3": {"parentContainerName": "DC1_L3LEAFS"}, "DC1_LEAF4": {"parentContainerName": "DC1_L3LEAFS"}, "DC1_SPINES": {"parentContainerName": "DC1_FABRIC"}}
]

CV_CONTAINERS_KO = [
    {"PYTEST": {"parent_container": "Tenant"}, "Leafs": {"parentContainerName": "PYTEST"}, "Spines": {
        "parentContainerName": "PYTEST", "configlets": ["01TRAINING-01"]}, "POD01": {"parentContainerName": "Leafs"}}
]

CV_DEVICE_OK = [
    [{"fqdn":"CV-ANSIBLE-EOS01","systemMacAddress":"50:8d:00:e3:78:aa","parentContainerName":"ANSIBLE","configlets":["01TRAINING-01","CV-EOS-ANSIBLE01"],"imageBundle":[]}],
    [{"serialNumber":"79AEA53101E7340AEC9AA4819D5E1F5B","systemMacAddress":"50:8d:00:e3:78:aa","parentContainerName":"ANSIBLE","configlets":["01TRAINING-01","CV-EOS-ANSIBLE01"],"imageBundle":[]}],
    [{"fqdn":"DEMO","serialNumber":"79AEA53101E7340AEC9AA4819D5E1F5B","systemMacAddress":"50:8d:00:e3:78:aa","parentContainerName":"ANSIBLE","configlets":["01TRAINING-01","CV-EOS-ANSIBLE01"],"imageBundle":[]}]
]

CV_DEVICE_KO = [
    [{"systemMacAddress":"50:8d:00:e3:78:aa","parentContainerName":"ANSIBLE","configlets":["01TRAINING-01","CV-EOS-ANSIBLE01"],"imageBundle":[]}],
    [{"serialNumber":"79AEA53101E7340AEC9AA4819D5E1F5B","systemMacAddress":"50:8d:00:e3:78:aa","configlets":["01TRAINING-01","CV-EOS-ANSIBLE01"],"imageBundle":[]}],
    [{"fqdn":"DEMO","serialNumber":"79AEA53101E7340AEC9AA4819D5E1F5B","systemMacAddress":"50:8d:00:e3:78:aa","configlets":["01TRAINING-01","CV-EOS-ANSIBLE01"],"imageBundle":[]}]
]

# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

def get_container_definition_valid():
    return CV_CONTAINERS_OK


def get_container_definition_invalid():
    return CV_CONTAINERS_KO

def get_device_definition_valid():
    return CV_DEVICE_OK


def get_device_definition_invalid():
    return CV_DEVICE_KO

# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #

@pytest.mark.parametrize('CV_CONTAINER', get_container_definition_valid())
@pytest.mark.generic
class TestJsonSchemaContainer():

    def test_container_schema_valid(self, CV_CONTAINER):
        result = validate_cv_inputs(
            user_json=CV_CONTAINER, schema=SCHEMA_CV_CONTAINER)
        assert result
        logging.info('Topology {} is valid against SCHEMA_CV_CONTAINER'.format(CV_CONTAINER))

    @pytest.mark.parametrize('CV_CONTAINER_INVALID', get_container_definition_invalid())
    def test_container_schema_invlaid(self, CV_CONTAINER, CV_CONTAINER_INVALID):
        result = validate_cv_inputs(
            user_json=CV_CONTAINER_INVALID, schema=SCHEMA_CV_CONTAINER)
        assert result is False
        logging.info(
            'Topology {} is INVALID against SCHEMA_CV_CONTAINER'.format(CV_CONTAINER_INVALID))

@pytest.mark.parametrize('CV_DEVICE', get_device_definition_valid())
@pytest.mark.generic
class TestJsonSchemaDevice():

    def test_device_schema_valid(self, CV_DEVICE):
        result = validate_cv_inputs(
            user_json=CV_DEVICE, schema=SCHEMA_CV_DEVICE)
        assert result
        logging.info('Topology {} is valid against SCHEMA_CV_DEVICE'.format(CV_DEVICE))

    @pytest.mark.parametrize('CV_DEVICE_INVALID', get_device_definition_invalid())
    def test_device_schema_invlaid(self, CV_DEVICE, CV_DEVICE_INVALID):
        result = validate_cv_inputs(
            user_json=CV_DEVICE_INVALID, schema=SCHEMA_CV_DEVICE)
        assert result is False
        logging.info(
            'Topology {} is INVALID against SCHEMA_CV_DEVICE'.format(CV_DEVICE_INVALID))
