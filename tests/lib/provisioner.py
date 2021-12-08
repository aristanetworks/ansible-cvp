#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801
from __future__ import (absolute_import, division, print_function)
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from cvprac import cvp_client, cvp_client_errors
import logging
from typing import Optional, List, Dict
from .helpers import time_log


"""
provisioner.py - Provides tool for provisioning CV before running Pytest
"""


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

    def _get_valid_only(self, entries: List):
        return [entry for entry in entries if entry['is_valid_expected']]

    def configlets_provision(self, configlets: List):
        configlets = self._get_valid_only(entries=configlets)
        for configlet in configlets:
            if configlet['is_present_expected'] is False:
                try:
                    configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                    res = self.cv.api.delete_configlet(name=configlet['name'], key=configlet_id)
                except Exception as error_message:
                    logging.error(error_message)
            elif configlet['is_present_expected']:
                try:
                    res = self.cv.api.add_configlet(name=configlet['name'], config=configlet['config'])
                    configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                    self.cv.api.add_note_to_configlet(key=configlet_id, note='Provisioned by Pytest {}'.format(time_log()))
                except Exception as error_message:
                    logging.warning('{} - moving to update process'.format(error_message))
                    try:
                        logging.info('Fallback to update process for configlet {}'.format(configlet['name']))
                        configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                        res = self.cv.api.update_configlet(name=configlet['name'], key=configlet_id, config=configlet['config_expected'])
                        self.cv.api.add_note_to_configlet(key=configlet_id, note='Provisioned by Pytest {}'.format(time_log()))
                    except Exception as error_message:
                        logging.error(error_message)

    def configlets_push(self, configlets: List):
        logging.debug(' Received set of configlets to publish: {}'.format(configlets))
        for configlet_title, configlet_data in configlets.items():
            try:
                res = self.cv.api.add_configlet(
                    name=configlet_title,
                    config=configlet_data
                )
                configlet_id = self.cv.api.get_configlet_by_name(
                    name=configlet_title
                )['key']
                self.cv.api.add_note_to_configlet(
                    key=configlet_id,
                    note='Provisioned by Pytest {}'.format(time_log())
                )
            except Exception as error_message:
                logging.critical(error_message)
