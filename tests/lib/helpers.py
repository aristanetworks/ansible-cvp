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
"""
    helpers.py - Declares the utility functions
"""

from datetime import datetime

# Generic helpers


def time_log():
    """Find the current date & time and converts it into specified format.

    Returns:
        String: Current date & time in specified format
    """
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")
