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
import unittest
import logging
from ansible_collections.arista.cvp.plugins.module_utils.schema_v3 import validate_cv_inputs
from lib.json_data import schemas, schema_valid, schema_invalid

# pytest - -html = report.html - -self-contained-html - -cov = . --cov-report = html - -color yes containerInputs.py - v

class TestCvSchemas(unittest.TestCase):

    def setUp(self):
        self.data_to_validate = dict()
        self.valid_data = schema_valid
        self.invalid_data = schema_invalid
        self.schema_types = ['container', 'device', 'configlet']
        return super().setUp()

    def test_schema_valid(self):
        for schema_type, schema in schemas.items():
            logging.info('Test schema for {}'.format(schema_type))
            for cv_container in self.valid_data[schema_type]:
                result = validate_cv_inputs(
                    user_json=cv_container, schema=schema)
                self.assertTrue(result)

    def test_schema_invalid(self):
        for schema_type, schema in schemas.items():
            logging.info('Test schema for {}'.format(schema_type))
            for cv_container in self.invalid_data[schema_type]:
                result = validate_cv_inputs(
                    user_json=cv_container, schema=schema)
                self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
