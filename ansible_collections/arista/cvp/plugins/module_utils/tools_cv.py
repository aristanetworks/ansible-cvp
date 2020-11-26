#!/usr/bin/env python
# coding: utf-8 -*-
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


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import logging
import traceback
from ansible.module_utils.connection import Connection
try:
    from cvprac.cvp_client import CvpClient
    from cvprac.cvp_client_errors import CvpLoginError
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


LOGGER = logging.getLogger('arista.cvp.cv_tools')


def cv_connect(module):
    """
    cv_connect CV Connection method.

    Generic Cloudvision connection method to connect to either on-prem or cvaas instances.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module information

    Returns
    -------
    CvpClient
        Instanciated CvpClient with connection information.
    """
    client = CvpClient()
    LOGGER.info('Connecting to CVP')
    connection = Connection(module._socket_path)
    host = connection.get_option("host")
    port = connection.get_option("port")
    cert_validation = connection.get_option("validate_certs")
    is_cvaas = True if connection.get_option("remote_user") == 'cvaas' else False
    cvaas_token = connection.get_option("password") if connection.get_option("remote_user") == 'cvaas' else None
    user = connection.get_option("remote_user") if connection.get_option("remote_user") != 'cvaas' else ''
    user_authentication = connection.get_option("password") if connection.get_option("remote_user") != 'cvass' else ''
    ansible_command_timeout = connection.get_option(
        "persistent_command_timeout")
    ansible_connect_timeout = connection.get_option(
        "persistent_connect_timeout")

    if cert_validation:
        LOGGER.debug("  Module will check CV certificate")
    if user == 'cvaas':
        LOGGER.debug('  Connecting to a cvaas instance')
    LOGGER.debug('  Connecting to a CV instance: %s with timers %s %s',
                 str(host),
                 str(ansible_connect_timeout),
                 str(ansible_command_timeout))
    try:
        client.connect(nodes=[host],
                       username=user,
                       cvaas_token=cvaas_token,
                       password=user_authentication,
                       protocol="https",
                       is_cvaas=is_cvaas,
                       port=port,
                       cert=cert_validation,
                       request_timeout=ansible_command_timeout,
                       connect_timeout=ansible_connect_timeout
                       )
    except CvpLoginError as e:
        module.fail_json(msg=str(e))
        LOGGER.error('Cannot connect to CVP: %s', str(e))

    LOGGER.info('Connected to CVP')

    return client


def isIterable(testing_object=None):
    """
    Test if an object is iterable or not.

    Test if an object is iterable or not. If yes return True, else return False.

    Parameters
    ----------
    testing_object : any, optional
        Object to test if it is iterable or not, by default None

    """
    try:
        some_object_iterator = iter(testing_object)  # noqa # pylint: disable=unused-variable
        return True
    except TypeError as te:  # noqa # pylint: disable=unused-variable
        return False


def match_filter(input, filter, default_always='all'):
    """
    Function to test if an object match userdefined filter.

    Function support list of string and string as filter.
    A default value is provided when calling function and if this default value for always matching is configured by user, then return True (Always matching)
    If filter is a list, then we iterate over the input and check if it matches an entry in the filter.

    Parameters
    ----------
    input : string
        Input to test of that match filter or not.
    filter : list
        List of string to compare against input.
    default_always : str, optional
        Keyword to consider as always matching, by default 'all'
    default_none : str, optional
        Keyword to consider as never matching, by default 'none'

    Returns
    -------
    bool
        True if input matchs filter, False in other situation
    """

    # W102 Workaround to avoid list as default value.
    if filter is None:
        LOGGER.critical('Filter is not set, configure default value to [\'all\']')
        filter = ["all"]

    LOGGER.debug(" * is_in_filter - filter is %s", str(filter))
    LOGGER.debug(" * is_in_filter - input string is %s", str(input))

    if "all" in filter:
        return True
    elif any(element in input for element in filter):
        return True
    LOGGER.debug(" * is_in_filter - NOT matched")
    return False


def cv_update_configlets_on_device(module, device_facts, add_configlets, del_configlets):
    response = dict()
    device_deletion = None
    device_addition = None
    # Initial Logging
    LOGGER.debug(' * cv_update_configlets_on_device - add_configlets: %s', str(add_configlets))
    LOGGER.debug(' * cv_update_configlets_on_device - del_configlets: %s', str(del_configlets))
    # Work on delete configlet scenario
    LOGGER.info(" * cv_update_configlets_on_device - start device deletion process")
    if len(del_configlets) > 0:
        try:
            device_deletion = module.client.api.remove_configlets_from_device(
                app_name="Ansible",
                dev=device_facts,
                del_configlets=del_configlets,
                create_task=True
            )
            response = device_deletion
        except Exception as error:
            errorMessage = str(error)
            LOGGER.error('OK, something wrong happens, raise an exception: %s', str(errorMessage))
        LOGGER.info(" * cv_update_configlets_on_device - device_deletion result: %s", str(device_deletion))
    # Work on Add configlet scenario
    LOGGER.debug(" * cv_update_configlets_on_device - start device addition process")
    if len(add_configlets) > 0:
        LOGGER.debug(' * cv_update_configlets_on_device - ADD configlets: %s', str(add_configlets))
        try:
            device_addition = module.client.api.apply_configlets_to_device(
                app_name="Ansible",
                dev=device_facts,
                new_configlets=add_configlets,
                create_task=True
            )
            response.update(device_addition)
        except Exception as error:
            errorMessage = str(error)
            LOGGER.error('OK, something wrong happens, raise an exception: %s', str(errorMessage))
        LOGGER.info(" * cv_update_configlets_on_device - device_addition result: %s", str(device_addition))
    LOGGER.info(" * cv_update_configlets_on_device - final result: %s", str(response))
    return response
