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
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import DeviceElement, FIELD_CONFIGLETS, FIELD_CONTAINER_NAME, FIELD_PARENT_NAME
from ansible_collections.arista.cvp.plugins.module_utils.device_tools import FIELD_FQDN, FIELD_SERIAL, FIELD_SYSMAC
from lib.json_data import mook_data, container_topology, schemas, container_ids

CONTAINER_IDS = ['Tenant', 'container-1111-2222-3333-4444', 'container_222_ccc_rrr']


# ---------------------------------------------------------------------------- #
#   PARAMETRIZE Management
# ---------------------------------------------------------------------------- #

def generate_flat_data(type: str, mode: str = 'valid'):
    flat_data = list()
    if mode in ['valid', 'invalid']:
        for inv in mook_data[mode][type]:
            if type == 'device':
                for unit in inv:
                    flat_data.append(unit)
            else:
                flat_data.append(inv)
    return flat_data


def generate_inventory_data(type: str, mode: str = 'valid'):
    return mook_data[mode][type]


# -----------------------------
#   cvDeviceElement specific
# -----------------------------

def generate_container_ids():
    return container_ids

# -----------------------------
#   cvResponse specific
# -----------------------------

def generate_cv_response_api_action_name():
    return ["", "a", "action", "action_test", "action test"]


def generate_cv_response_result_manager_name():
    return ["", "r", "result", "result_manager", "result manager"]


def generate_cv_response_ansible_name():
    return ["", "a", "ansible", "ansible_response", "ansible content"]

# -----------------------------
#   ContainerInputs specific
# -----------------------------

def generate_cv_container_topology():
    return container_topology
