"""
utility.py - Declaration of utility functions.
"""
from __future__ import (absolute_import, division, print_function)
import logging
import sys
import requests.packages.urllib3
from cvprac.cvp_client import CvpClient, CvpLoginError, CvpRequestError
from ansible_collections.arista.cvp.plugins.module_utils.resources.api.fields import Api
from tests.lib import config
from tests.lib.helpers import time_log
from tests.lib.json_data import CONTAINER_IDS
from tests.data.container_tools_unit import CVP_DEVICES
from tests.system.constants_data import USER_CONTAINERS, CV_CONTAINERS_NAME_ID_LIST, CVP_DEVICES, CVP_DEVICES_1, CVP_DEVICES_UNKNOWN, CVP_DEVICES_SCHEMA_TEST, CONTAINER_DESTINATION

MODULE_LOGGER = logging.getLogger(__name__)

def cvp_login():
    """Login cvp devices

    Returns:
        Object: cvp client
    """
    requests.packages.urllib3.disable_warnings()
    cvp_client = CvpClient(log_level=logging.getLevelName(MODULE_LOGGER.getEffectiveLevel()))
    MODULE_LOGGER.info("Start CV login process at {}".format(time_log()))
    try:
        cvp_client.connect(
            nodes=[config.server],
            username="",
            password="",
            is_cvaas=config.cvaas,
            api_token=config.user_token
        )
    except (CvpLoginError, CvpRequestError):
        MODULE_LOGGER.error('Can\'t connect to CV instance')
        sys.exit(1)
    else:
        MODULE_LOGGER.info("End of CV login process at {}".format(time_log()))
        MODULE_LOGGER.info("Connected to CVP")
        return cvp_client


def generate_test_ids_dict(val):
    """
    generate_test_ids Helper to generate test ID for parametrize

    Only related to SYSTEM_CONFIGLETS_TESTS structure

    Parameters
    ----------
    val : dict
        A configlet test structure

    Returns
    -------
    str
        Name of the configlet
    """
    if 'name' in val.keys():
        # note this wouldn't show any hours/minutes/seconds
        return val['name']
    elif 'hostname' in val.keys():
        return val['hostname']


def get_devices():
    """Returns the cvp devices

    Returns:
        List: cvp devices
    """
    return CVP_DEVICES


def get_container_name_id():
    """Return cv container name id list

    Returns:
        List: container name id
    """
    return CV_CONTAINERS_NAME_ID_LIST


def get_unit_container():
    """Return unit container

    Returns:
        List: unit container config
    """
    result = []
    for key, values in USER_CONTAINERS[0].items():
        values["name"] = key
        result.append(values)
    return [result[0]]


def get_topology_user_input():
    """Return topology user input

    Returns:
        List: user container config
    """
    return USER_CONTAINERS


def get_devices_for_schema():
    """Returns the cvp devices schema

    Returns:
        List: cvp devices schema
    """
    return CVP_DEVICES_SCHEMA_TEST


def get_devices_unknown():
    """Returns the unknown cvp devices

    Returns:
      List: unknown cvp devices
    """
    return CVP_DEVICES_UNKNOWN


def get_cvp_devices_after_move():
    """Returns list of devices to move

    Returns:
      List: cvp devices to move
    """
    return CVP_DEVICES_1

def get_devices_to_move():
    """Returns list of devices to move

    Returns:
      List: cvp devices to move
    """
    to_move = []
    for entry in CVP_DEVICES_1:
        if Api.generic.PARENT_CONTAINER_NAME in entry:
            entry[Api.generic.PARENT_CONTAINER_NAME] = CONTAINER_DESTINATION
        to_move.append(entry)
    return to_move

def generate_container_ids():
    """Returns the container ids

    Returns:
        List: container ids
    """
    return CONTAINER_IDS
