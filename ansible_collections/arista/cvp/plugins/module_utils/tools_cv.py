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
    connection = Connection(module._socket_path)
    host = connection.get_option("host")
    port = connection.get_option("port")
    user = connection.get_option("remote_user")
    user_authentication = connection.get_option("password")
    LOGGER.info('Connecting to CVP')
    if user == 'cvaas':
        LOGGER.debug('Connecting to a cvaas instance')
        try:
            client.connect(nodes=[host],
                           is_cvaas=True,
                           cvaas_token=user_authentication,
                           username='',
                           password='',
                           protocol="https",
                           port=port
                           )
        except CvpLoginError as e:
            module.fail_json(msg=str(e))
            LOGGER.error('Cannot connect to CVP: %s', str(e))
    else:
        LOGGER.debug('Connecting to a on-prem instance')
        try:
            client.connect(nodes=[host],
                           username=user,
                           password=user_authentication,
                           protocol="https",
                           is_cvaas=False,
                           port=port,
                           )
        except CvpLoginError as e:
            module.fail_json(msg=str(e))
            LOGGER.error('Cannot connect to CVP: %s', str(e))

    LOGGER.debug('*** Connected to CVP')

    return client



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
            response.uate(device_addition)
        except Exception as error:
            errorMessage = str(error)
            LOGGER.error('OK, something wrong happens, raise an exception: %s', str(errorMessage))
        LOGGER.info(" * cv_update_configlets_on_device - device_addition result: %s", str(device_addition))
    LOGGER.info(" * cv_update_configlets_on_device - final result: %s", str(response))
    return response
