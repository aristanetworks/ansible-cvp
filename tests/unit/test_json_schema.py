#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import logging
import pytest
from ansible_collections.arista.cvp.plugins.module_utils.tools_schema import validate_json_schema
from ansible_collections.arista.cvp.plugins.module_utils.resources.schemas.v3 import SCHEMA_CV_CONTAINER, SCHEMA_CV_DEVICE, SCHEMA_CV_CONFIGLET
from tests.lib.parametrize import generate_inventory_data


# --------------------------------------------------------
# Container format validation
# --------------------------------------------------------
@pytest.mark.generic
class TestJsonSchemaContainer():
    @pytest.mark.parametrize("CV_CONTAINER", generate_inventory_data(type="container"))
    def test_container_schema_valid(self, CV_CONTAINER):
        logging.debug("Schema is: {}".format(SCHEMA_CV_CONTAINER))
        result = validate_json_schema(
            user_json=CV_CONTAINER, schema=SCHEMA_CV_CONTAINER)
        assert result
        logging.info(
            "Topology {} is valid against SCHEMA_CV_CONTAINER".format(CV_CONTAINER))

    @pytest.mark.parametrize("CV_CONTAINER_INVALID", generate_inventory_data(type="container", mode="invalid"))
    def test_container_schema_invalid(self, CV_CONTAINER_INVALID):
        result = validate_json_schema(
            user_json=CV_CONTAINER_INVALID, schema=SCHEMA_CV_CONTAINER)
        assert result is False
        logging.info(
            "Topology {} is INVALID against SCHEMA_CV_CONTAINER".format(CV_CONTAINER_INVALID))

# --------------------------------------------------------
# Configlet format validation
# --------------------------------------------------------


@pytest.mark.generic
class TestJsonSchemaConfiglet():
    @pytest.mark.parametrize("CV_CONFIGLET", generate_inventory_data(type="configlet"))
    def test_container_schema_valid(self, CV_CONFIGLET):
        logging.debug("Schema is: {}".format(SCHEMA_CV_CONFIGLET))
        result = validate_json_schema(
            user_json=CV_CONFIGLET, schema=SCHEMA_CV_CONFIGLET)
        assert result
        logging.info(
            "Topology {} is valid against SCHEMA_CV_CONFIGLET".format(CV_CONFIGLET))

    @pytest.mark.parametrize("CV_CONFIGLET_INVALID", generate_inventory_data(type="configlet", mode="invalid"))
    def test_container_schema_invalid(self, CV_CONFIGLET_INVALID):
        result = validate_json_schema(
            user_json=CV_CONFIGLET_INVALID, schema=SCHEMA_CV_CONFIGLET)
        assert result is False
        logging.info(
            "Topology {} is INVALID against SCHEMA_CV_CONFIGLET".format(CV_CONFIGLET_INVALID))

# --------------------------------------------------------
# Device format validation
# --------------------------------------------------------


@pytest.mark.generic
class TestJsonSchemaDevice():
    @pytest.mark.parametrize("CV_DEVICE", generate_inventory_data(type="device"))
    def test_container_schema_valid(self, CV_DEVICE):
        logging.debug("Schema is: {}".format(SCHEMA_CV_DEVICE))
        result = validate_json_schema(
            user_json=CV_DEVICE, schema=SCHEMA_CV_DEVICE)
        assert result
        logging.info(
            "Topology {} is valid against SCHEMA_CV_DEVICE".format(CV_DEVICE))

    @pytest.mark.parametrize("CV_DEVICE_INVALID", generate_inventory_data(type="device", mode="invalid"))
    def test_container_schema_invalid(self, CV_DEVICE_INVALID):
        result = validate_json_schema(
            user_json=CV_DEVICE_INVALID, schema=SCHEMA_CV_DEVICE)
        assert result is False
        logging.info(
            "Topology {} is INVALID against SCHEMA_CV_DEVICE".format(CV_DEVICE_INVALID))
