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
from typing import Any
__metaclass__ = type
import logging
import traceback
from typing import Any
import json
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
try:
    from cvprac.cvp_client import CvpClient
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_objects')
MODULE_LOGGER.info('Start cv_object module execution')

FIELD_TOPO_CONTAINER_LIST = 'childContainerList'
FIELD_TOPO_DEVICE_LIST = 'childNetElementList'
FIELD_TOPO_COUNT_DEVICES = 'childNetElementCount'
FIELD_TOPO_COUNT_CONTAINERS = 'childContainerCount'
FIELD_TOPO_NAME = 'name'
FIELD_TOPO_KEY = 'key'
FIELD_TOPO_PARENT_ID = 'parentContainerId'
FIELD_INV_NAME = 'Name'
FIELD_INV_KEY = 'Key'


class CvContainerTopology(object):

    def __init__(self, cv_connection: CvpClient = None, topology_filename: str = None, container_inventory_filename: str = None):
        if cv_connection is not None:
            self._cv_connection = cv_connection
            self.refresh_data()
        # Implemented for offline debugging
        elif cv_connection is None:
            self._topology = self._load_json(filename=topology_filename)
            self._inventory = self._load_json(
                filename=container_inventory_filename)

    # PRIVATE FUNCTIONS

    def _load_json(self, filename: str):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data

    def _lookup_container(self, container_name: str, topology: dict = None, result: Any = None):
        if topology is None:
            if 'name' in topology:
                if topology[FIELD_TOPO_NAME] == container_name:
                    return topology
            topology = self._topology['topology'][FIELD_TOPO_CONTAINER_LIST]
        for container in topology:
            if 'name' in container:
                if container[FIELD_TOPO_NAME] == container_name:
                    result = container
                elif FIELD_TOPO_CONTAINER_LIST in container:
                    result = self._lookup_container(
                        topology=container[FIELD_TOPO_CONTAINER_LIST],
                        container_name=container_name, result=result)
        return result

    def _remove_keys(self, full_dict: dict, filtered_keys: list = [FIELD_TOPO_CONTAINER_LIST, FIELD_TOPO_DEVICE_LIST]):
        for filtered_key in filtered_keys:
            if filtered_key in full_dict:
                full_dict.pop(filtered_key, None)
        return full_dict

    # GENERIC FUNCTIONS

    def refresh_data(self):
        self._topology = self._cv_connection.api.filter_topology(
            node_id='root')
        self._inventory = self._cv_connection.api.get_containers()['data']

    def get_container_topology(self, container_name: str, brief: bool = False, verbose: bool = False):
        container = self._lookup_container(container_name=container_name)
        if container is None:
            return None
        elif brief is True:
            return {
                FIELD_TOPO_KEY: container[FIELD_TOPO_KEY],
                FIELD_TOPO_NAME: container[FIELD_TOPO_NAME],
                FIELD_TOPO_PARENT_ID: container[FIELD_TOPO_PARENT_ID]
                }
        elif verbose is True:
            return container
        return self._remove_keys(full_dict=container)

    def get_container_inventory(self, container_name: str = None, container_id: str = None):
        if container_name is not None:
            for container in self._inventory:
                if container[FIELD_TOPO_NAME] == container_name:
                    return container
            return None
        if container_id is not None:
            for container in self._inventory:
                if container[FIELD_TOPO_KEY] == container_id:
                    return container
            return None

    # BOOLEAN & TEST FUNCTIONS

    def has_device(self, container_name: str):
        container = self._lookup_container(container_name=container_name)
        if FIELD_TOPO_COUNT_DEVICES in container:
            if int(container[FIELD_TOPO_COUNT_DEVICES]) > 0:
                return True
        return False

    def has_children(self, container_name: str):
        container = self._lookup_container(container_name=container_name)
        if FIELD_TOPO_COUNT_CONTAINERS in container:
            if int(container[FIELD_TOPO_COUNT_CONTAINERS]) > 0:
                return True
        return False

    def is_container_exist(self, container_name: str):
        if self.get_container_inventory(container_name=container_name) is not None:
            return True
        return False

    def is_container_empty(self, container_name: str):
        if (self.has_children(container_name=container_name)
                and self.has_device(container_name=container_name)):
            return False
        return True

    # GETTERS

    @property
    def root_container(self):
        return {FIELD_TOPO_KEY: self._topology['topology'][FIELD_TOPO_KEY],
                FIELD_TOPO_NAME: self._topology['topology'][FIELD_TOPO_NAME]}

    @property
    def containers_list(self):
        return self._inventory

    def get_container_id(self, container_name: str):
        return self.get_container_inventory(container_name=container_name)[FIELD_INV_KEY]

    def get_parent_container(self, child_container: str):
        parent_id = self.get_container_topology(
            container_name=child_container, brief=True)[FIELD_TOPO_PARENT_ID]
        parent_container = self.get_container_inventory(container_id=parent_id)
        return {FIELD_INV_KEY: parent_container[FIELD_INV_KEY],
                FIELD_INV_NAME: parent_container[FIELD_INV_NAME]}


# class CvContainerAction(object):
#     def __init__(self, cv_connection: CvpClient):
#         self._cv_connection = cv_connection
#         self._container_data = CvContainerTopology(cv_connection=self._cv_connection)

#     def create(container: str, parent: str):
