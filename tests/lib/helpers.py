#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable = duplicate-code
# flake8: noqa: R0801
#
# GNU General Public License v3.0+
#
# Copyright 2019 Arista Networks AS-EMEA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import os
import logging
from datetime import datetime
from dataclasses import dataclass
import pprint


"""
    helpers.py - Declares the utility functions and classes
"""


def time_log():
    """Find the current date & time and converts it into specified format.

    Returns:
        String: Current date & time in specified format
    """
    now = datetime.now()
    return now.strftime("%m/%d/%Y, %H:%M:%S.%f")


def setup_custom_logger(name):
    """
    setup_custom_logger Format logging to add timestamp for log generated in Pytest

    Format logging to add timestamp for log generated in Pytest.
    All logging outside of pytest is not updated.

    Parameters
    ----------
    name : str
        Name of the logging APP

    Returns
    -------
    logging
        Logging instance
    """
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)-8s File: %(filename)s  - Function: %(funcName)s - Line: %(lineno)d - %(message)s',
        )
    # Handler for logfile
    handler = logging.FileHandler('pytest.log', mode='w')
    handler.setFormatter(formatter)
    # Handler for screen
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    # Log level
    log_level = logging.getLevelName(os.environ.get('PYTEST_LOG_LEVEL', 'DEBUG'))

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger


def to_nice_json(data, ident: int = 4):
    """
    to_nice_json Helper to render JSON in logs

    Leverage pprint to help to render JSON as a nice output

    Parameters
    ----------
    data : any
        Data to nicely render with PPRINT
    ident : int, optional
        Number of space to use for indentation, by default 4

    Returns
    -------
    str
        String to print
    """
    return pprint.pformat(data, indent=ident)

@dataclass
class AnsibleModuleMock():
    """
    AnsibleModuleMock Dataclass to mock AnsibleModule element

    Emulate AnsibleModule in Pytest execution
    """
    check_mode: bool = False
    description: str = 'Fake Ansible Module'

    def fail_json(self, msg: str):
        logging.error("AnsibleModule.fail_json: {}".format(msg))

def strtobool(input):
    """
    strtobool Convert string to boolean

    Parameters
    ----------
    input : str
        String to convert into boolean

    Returns
    -------
    bool
        Result of the conversion
    """
    return input.lower() in ('true', '1', 't')
