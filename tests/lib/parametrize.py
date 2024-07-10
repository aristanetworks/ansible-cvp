#!/usr/bin/python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
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
from tests.lib.json_data import mook_data, container_topology, modes, CONTAINER_IDS


# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

def generate_list_from_dict(data):
    """
    generate_flat_data Generate a flat list of dict

    Example
    -------
    >>> CUSTOMER_CVP_CONTAINER_TOPOLOGY = {"Tenant":{"name":"Tenant","key":"root","parentContainerId":"None"},"Undefined":{"name":"Undefined","key":"undefined_container","parentContainerId":"root"}}

    >>> result = generate_flat_data(CUSTOMER_CVP_CONTAINER_TOPOLOGY)

    >>> print(result)
    [{"name":"Tenant","key":"root","parentContainerId":"None"},{"name":"Undefined","key":"undefined_container","parentContainerId":"root"}]

    Parameters
    ----------
    data : dict
        Data to transform

    Returns
    -------
    list
        List extracted from the dict
    """
    return [dict(data[d].items()) for d in data]


def generate_flat_data(type: str, mode: str = "valid"):
    """Returns the data based on type and mode

        Args:
            type (string): type of data. It can be 'device', 'container' or 'configlet'
            mode (string): mode can be 'valid' or 'invalid'

        Returns:
            List: data based on mode and type
        """
    flat_data = list()
    if mode in modes:
        for inv in mook_data[mode][type]:
            if type == "device":
                for unit in inv:
                    flat_data.append(unit)
                # flat_data = [unit for unit in inv]
            else:
                flat_data.append(inv)
    return flat_data


def generate_inventory_data(type: str, mode: str = "valid"):
    """Returns the inventory data based on type and mode

            Args:
                type (string): type of data. It can be 'device', 'container' or 'configlet'
                mode (string): mode can be 'valid' or 'invalid'

            Returns:
                List: inventory data based on mode and type
            """
    return mook_data[mode][type]


# -----------------------------
#   CvConfigletTools specific
# -----------------------------
def generate_CvConfigletTools_content(configlet_inputs: list, is_present_state: bool = False):
    configletInventory = []
    if not is_present_state:
        temp = {
            configlet_in['name']: configlet_in['config'] for configlet_in in configlet_inputs if configlet_in['is_present_expected'] is False
        }
    else:
        temp = {
            configlet_in['name']: configlet_in['config'] for configlet_in in configlet_inputs if configlet_in['is_present_expected']
        }
    configletInventory.append(temp)
    return configletInventory


# -----------------------------
#   cvDeviceElement specific
# -----------------------------

def generate_container_ids():
    """Returns the list of container ids initialized in the json_data file

    Returns:
        List: container ids
    """
    return CONTAINER_IDS

# -----------------------------
#   cvResponse specific
# -----------------------------


def generate_cv_response_api_action_name():
    """Returns the cv response api action name

    Returns:
        List: cv response api action name
    """
    return ["", "a", "action", "action_test", "action test"]


def generate_cv_response_result_manager_name():
    """Returns the cv response result manager name

    Returns:
        List: cv response result manager name
    """
    return ["", "r", "result", "result_manager", "result manager"]


def generate_cv_response_ansible_name():
    """Returns the cv response ansible name

    Returns:
        List: cv response ansible name
    """
    return ["", "a", "ansible", "ansible_response", "ansible content"]

# -----------------------------
#   ContainerInputs specific
# -----------------------------


def generate_cv_container_topology():
    """Returns the cv container topology

    Returns:
        List: configuration
    """
    return container_topology
