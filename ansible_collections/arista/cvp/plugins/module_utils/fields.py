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

# TODO: Will be activated in python 3.8
# from dataclasses import dataclass


class ModuleOptionValues():
    APPLY_MODE_STRICT: str = 'stict'
    APPLY_MODE_LOOSE: str = 'loose'
    STATE_MODE_PRESENT: str = 'present'
    STATE_MODE_ABSENT: str = 'factory_reset'


# @dataclass
class Facts():
    """Facts Represent All fields specific to cv_facts_v3 module"""
    # Facts headers
    DEVICE: str = 'cvp_devices'
    CONTAINER: str = 'cvp_containers'
    CONFIGLET: str = 'cvp_configlets'
    # Cache Headers
    CACHE_CONTAINERS: str = 'containers'
    CACHE_MAPPERS: str = 'configlets_mappers'


# @dataclass
class ContainerResponseFields():
    """Fields to build output of cv_container_v3 module"""
    CONTAINER_ADDED: str = 'container_added'
    CONTAINER_DELETED: str = 'container_deleted'
    CONFIGLETS_ATTACHED: str = 'configlets_attached'
    CONFIGLETS_DETACHED: str = 'configlets_detached'


# @dataclass
class DeviceResponseFields():
    """Fields to build output of cv_device_v3 module"""
    DEVICE_DEPLOYED: str = 'devices_deployed'
    DEVICE_MOVED: str = 'devices_moved'
    CONFIGLET_ATTACHED: str = 'configlets_attached'
    CONFIGLET_DETACHED: str = 'configlets_detached'
    DEVICE_RESET: str = 'devices_reset'


# @dataclass
class ApiGeneric():
    """Generic Keys used in all type of resources"""
    PARENT_CONTAINER_ID: str = 'parentContainerId'
    PARENT_CONTAINER_NAME: str = 'parentContainerName'
    NAME: str = 'name'
    KEY: str = 'key'
    CONFIGLETS: str = 'configlets'
    CONFIG: str = 'config'


# @dataclass
class ApiContainer():
    """Keys specific to Container resources"""
    ID: str = 'containerId'
    COUNT_DEVICE: str = 'childNetElementCount'
    COUNT_CONTAINER: str = 'childContainerCount'
    CHILDREN_LIST: str = 'childContainerList'
    CONFIGLETS_LIST: str = 'configletList'
    PARENT_CONTAINER_NAME: str = 'parentContainerName'
    PARENT_KEY: str = 'parentContainerKey'
    TOPOLOGY: str = 'topology'
    UNDEFINED_CONTAINER_ID: str = 'undefined_container'
    UNDEFINED_CONTAINER_NAME: str = 'Undefined'
    KEY: str = 'Key'


# @dataclass
class ApiDevice():
    """Keys specific to Device resources"""
    FQDN: str = 'fqdn'
    HOSTNAME: str = 'hostname'
    SYSMAC: str = 'systemMacAddress'
    SERIAL: str = 'serialNumber'
    ID: str = 'key'
    CONTAINER_NAME: str = 'containerName'
    IMAGE_BUNDLE: str = 'image_bundle'


# @dataclass
class ApiConfiglet():
    """Keys specific to Configlet resources"""
    ID: str = 'configletId'


# @dataclass
class ApiMappers():
    """Keys specific to Configlets_Mappers resources"""
    OBJECT_ID: str = 'objectId'


# @dataclass
class ApiTask():
    """Keys specific to Task resources"""
    TASK_IDS: str = 'taskIds'


# @dataclass
class ApiFields():
    """Central point to use all CV data resource fields"""
    generic: ApiGeneric = ApiGeneric
    device: ApiDevice = ApiDevice
    container: ApiContainer = ApiContainer
    configlet: ApiConfiglet = ApiConfiglet
    mappers: ApiMappers = ApiMappers
    task: ApiTask = ApiTask
