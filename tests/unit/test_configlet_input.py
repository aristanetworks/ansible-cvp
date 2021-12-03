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
from ansible_collections.arista.cvp.plugins.module_utils.schema_v3 import SCHEMA_CV_CONTAINER, SCHEMA_CV_DEVICE, SCHEMA_CV_CONFIGLET, validate_cv_inputs
from lib.parametrize import generate_CvConfigletTools_content
from lib.cvaas_configlet import SYSTEM_CONFIGLETS_TESTS
import logging
import pytest


@pytest.mark.generic
# Parametrize to build a ConfigletInput from list of configlet in SYSTEM_CONFIGLETS_TESTS. Only those set with is_present_expected to False
@pytest.mark.parametrize("configlet_inventory", generate_CvConfigletTools_content(configlet_inputs=SYSTEM_CONFIGLETS_TESTS, is_present_state=None), ids=['configlet-not-already-declared'])
class Test_ConfigletInput():

    def test_print_inventory_data(self, configlet_inventory):
        logging.debug('Inventory has {} configlets'.format(len(configlet_inventory)))
        logging.debug(configlet_inventory)

    def test_creation(self, configlet_inventory):
        pass
