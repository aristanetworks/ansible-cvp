#!/usr/bin/python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
"""
    config.py - Declares the credential of the specified server
"""
import os

# TODO - use f-strings
# pylint: disable=consider-using-f-string


def strtobool(val):
    """
    Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    Port of distutils.util.strtobool as per PEP 0632 recommendation
    https://peps.python.org/pep-0632/#migration-advice
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


user_token = os.getenv("ARISTA_AVD_CV_TOKEN", "unset_token")
server = os.getenv("ARISTA_AVD_CV_SERVER", "")
provision_cv = strtobool(os.getenv("ARISTA_AVD_CV_PROVISION", "true"))
cvaas = strtobool(os.getenv("ARISTA_AVD_CVAAS", "true"))
