#!/usr/bin/python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
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
from ansible_collections.arista.cvp.plugins.module_utils.configlet_tools import ConfigletInput
from lib.parametrize import generate_flat_data
from lib.helpers import to_nice_json, setup_custom_logger
import pytest


logger = setup_custom_logger(__name__)

# TODO - use f-strings
# pylint: disable=consider-using-f-string

@pytest.mark.generic
@pytest.mark.configlet
# Parametrize to build a ConfigletInput from list of configlet in SYSTEM_CONFIGLETS_TESTS. Only those set with is_present_expected to False
class Test_ConfigletInput():

    @pytest.mark.parametrize("configlet_inventory", generate_flat_data(type='configlet', mode='valid'))
    def test_print_inventory_data(self, configlet_inventory):
        logger.debug('Inventory has {} configlets'.format(len(configlet_inventory)))
        logger.debug('Inventory is: {}'.format(to_nice_json(data=configlet_inventory)))

    @pytest.mark.parametrize("configlet_inventory", generate_flat_data(type='configlet', mode='valid'))
    def test_inventory_is_valid(self, configlet_inventory):
        configletInput = ConfigletInput(user_topology=configlet_inventory)
        logger.info('Test configlet is valid')
        assert configletInput.is_valid

    @pytest.mark.parametrize("configlet_inventory", generate_flat_data(type='configlet', mode='invalid'))
    def test_inventory_is_invalid(self, configlet_inventory):
        configletInput = ConfigletInput(user_topology=configlet_inventory)
        logger.info('Test configlet is invalid')
        assert not configletInput.is_valid
