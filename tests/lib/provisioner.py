#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801

"""
parametrize.py - Retrieves the mock data from the json_data file
"""

from __future__ import (absolute_import, division, print_function)
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from cvprac import cvp_client, cvp_client_errors
import logging
from typing import Optional, List, Dict





class CloudvisionProvisioner():
    def __init__(self, server: str, token: str, port: int = 443):
        self.server = server
        self.port = port
        self.token = token
        self.cv = cvp_client.CvpClient()
        try:
            self.cv.connect(
                nodes=[self.server],
                username="",
                password="",
                is_cvaas=True,
                api_token=self.token
            )
        except cvp_client_errors.CvpLoginError:
            logging.error('Can\'t connect to CV instance')

    def provision_configlets(self, configlets: List):
        for configlet in configlets:
            if configlet['is_present_expected'] is False:
                try:
                    configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                    res = self.cv.api.delete_configlet(name=configlet['name'], key=configlet_id)
                except Exception as error_message:
                    logging.critical(error_message)
            elif configlet['is_present_expected']:
                try:
                    res = self.cv.api.add_configlet(name=configlet['name'], config=configlet['config'])
                except Exception as error_message:
                    logging.critical(error_message)
                    try:
                        logging.info('Fallback to update process for configlet {}'.format(configlet['name']))
                        configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                        res = self.cv.api.update_configlet(name=configlet['name'], key=configlet_id, config=configlet['config_expected'])
                    except Exception as error_message:
                        logging.critical(error_message)
