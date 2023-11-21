#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import logging
import uuid
import os
from logging.handlers import RotatingFileHandler  # noqa # pylint: disable=unused-import

# Get Logging level from Environment variable / Default INFO

# Define standard logging verbosity
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

# Set loglevel for arista.cvp modules
LOGGING_LEVEL = os.getenv('ANSIBLE_CVP_LOG_LEVEL', 'error')
LOGLEVEL = LEVELS.get(LOGGING_LEVEL, logging.NOTSET)

# Set loglevel for urllib3
LOGGING_LEVEL_URLLIB3 = os.getenv('ANSIBLE_CVP_LOG_APICALL', 'error')
LOGLEVEL_URLLIB3 = LEVELS.get(LOGGING_LEVEL_URLLIB3, logging.ERROR)

# Get filename to write logs / default /temp/arista.cvp.debug-<uuid>.log
DEFAULT_LOG_FILE = '/tmp/arista.cvp.debug.' + str(uuid.uuid4()) + '.log'
LOGGING_FILENAME = os.getenv(
    'ANSIBLE_CVP_LOG_FILE', DEFAULT_LOG_FILE)

# set a format which is simpler for console use
formatter = logging.Formatter(
    '%(asctime)s - %(name)-12s: %(levelname)-s - func: %(funcName)-12s (L:%(lineno)-3d) - %(message)s')

# set up ROOT handler to use logging with file rotation.
handler = logging.handlers.RotatingFileHandler(
    LOGGING_FILENAME, maxBytes=1000000, backupCount=5)
handler.setFormatter(formatter)
handler.setLevel(LOGLEVEL)
# Unset default logging level for root handler
logging.getLogger('').setLevel(logging.NOTSET)
logging.getLogger('').addHandler(handler)

# Configure URLLIB3 logging (default Warning to avoid too much verbosity)
logging.getLogger("urllib3").setLevel(LOGLEVEL_URLLIB3)
