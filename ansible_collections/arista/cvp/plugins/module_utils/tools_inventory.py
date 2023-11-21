#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import logging
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import

MODULE_LOGGER = logging.getLogger('arista.cvp.tools_inventory')


def find_hostname_by_mac(inventory, mac_address):
    """
    Function to get device hostname based on System Mac Address.

    Parameters
    ----------
    inventory : list
        Inventory list extracted from CVP.
    mac_address : string
        Mac address to search

    Returns
    -------
    string
        Device hostname. Default None if not found
    """
    for device in inventory:
        if 'systemMacAddress' in device:
            if device['systemMacAddress'] == mac_address:
                MODULE_LOGGER.debug('device data: %s', str(device))
                if 'name' in device:
                    return device['name']
                elif 'hostname' in device:
                    return device['hostname']
    return None


def find_containerName_by_containerId(containers_list, container_id):
    """
    Function to get containername based on container ID.

    Parameters
    ----------
    containers_list : list
        Containers list extracted from CVP.
    container_id : string
        ID of the container to search

    Returns
    -------
    string
        Container name. Default None if not found
    """
    for container in containers_list:
        if 'Key' in container:
            if container['Key'] == container_id:
                return container['Name']
    return None
