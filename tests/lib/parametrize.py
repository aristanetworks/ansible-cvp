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
from lib.json_data import mook_data, container_topology, schemas, modes, CONTAINER_IDS


# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

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
