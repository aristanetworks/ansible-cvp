#!/usr/bin/env python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable = duplicate-code
# flake8: noqa: R0801
#


import sys
import os
import logging
from datetime import datetime
from dataclasses import dataclass
import pprint

# TODO - use f-strings
# pylint: disable=consider-using-f-string

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
