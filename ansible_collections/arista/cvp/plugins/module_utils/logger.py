#!/usr/bin/env python
# coding: utf-8 -*-
#
# FIXME: required to pass ansible-test
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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import logging
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
LOGGING_LEVEL = os.getenv('ANSIBLE_CVP_LOG_LEVEL', 'info')
LOGLEVEL = LEVELS.get(LOGGING_LEVEL, logging.NOTSET)

# Set loglevel for urllib3
LOGGING_LEVEL_URLLIB3 = os.getenv('ANSIBLE_CVP_LOG_APICALL', 'warning')
LOGLEVEL_URLLIB3 = LEVELS.get(LOGGING_LEVEL_URLLIB3, logging.WARNING)

# Get filename to write logs / default /temp/arista.cvp.debug.log
LOGGING_FILENAME = os.getenv(
    'ANSIBLE_CVP_LOG_FILE', '/tmp/arista.cvp.debug.log')

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
