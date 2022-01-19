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


# --------------------------------------------------------------------------------------------------------
# Information:
#
# Provides classes to classify CONSTANT in the collection. 3 types of classes are available:
#   - ModuleOptionValues: expose constants for ansible module option values
#   - <module>ResponseFields: strings to use in Ansible response for all modules.
#   - Api<ressource-type>: strings to use to get data from Cloudvision response content.
#
# Usage:
#
# If a KEY is required for more than 1 type of resource, definition MUST be in ApiGeneric class
# If a KEY is specific to a resource, its definition SHOULD go to its dedicated class Api<resource-type>
# If a KEY is required for more than 1 type of resource and one resource has a different syntax, then
#       Global definition MUST go to ApiGeneric
#       Specific definition SHALL go to resource class
# --------------------------------------------------------------------------------------------------------


class ModuleOptionValues():
    """Values for modules options"""
    APPLY_MODE_LOOSE: str = 'loose'
    APPLY_MODE_STRICT: str = 'stict'
    STATE_MODE_ABSENT: str = 'factory_reset'
    STATE_MODE_PRESENT: str = 'present'


# @dataclass
class Facts():
    """Facts Represent All fields specific to cv_facts_v3 module"""
    CACHE_CONTAINERS: str = 'containers'
    CACHE_MAPPERS: str = 'configlets_mappers'
    CONFIGLET: str = 'cvp_configlets'
    CONTAINER: str = 'cvp_containers'
    DEVICE: str = 'cvp_devices'


# @dataclass
class ContainerResponseFields():
    """Fields to build output of cv_container_v3 module"""
    CONFIGLETS_ATTACHED: str = 'configlets_attached'
    CONFIGLETS_DETACHED: str = 'configlets_detached'
    CONTAINER_ADDED: str = 'container_added'
    CONTAINER_DELETED: str = 'container_deleted'


# @dataclass
class DeviceResponseFields():
    """Fields to build output of cv_device_v3 module"""
    CONFIGLET_ATTACHED: str = 'configlets_attached'
    CONFIGLET_DETACHED: str = 'configlets_detached'
    DEVICE_DEPLOYED: str = 'devices_deployed'
    DEVICE_MOVED: str = 'devices_moved'
    DEVICE_RESET: str = 'devices_reset'


# @dataclass
class ApiGeneric():
    """Generic Keys used in all type of resources"""
    CONFIG: str = 'config'
    CONFIGLETS: str = 'configlets'
    KEY: str = 'key'
    NAME: str = 'name'
    PARENT_CONTAINER_ID: str = 'parentContainerId'
    PARENT_CONTAINER_NAME: str = 'parentContainerName'


# @dataclass
class ApiContainer():
    """Keys specific to Container resources"""
    CHILDREN_LIST: str = 'childContainerList'
    CONFIGLETS_LIST: str = 'configletList'
    COUNT_CONTAINER: str = 'childContainerCount'
    COUNT_DEVICE: str = 'childNetElementCount'
    ID: str = 'containerId'
    KEY: str = 'Key'
    TOPOLOGY: str = 'topology'
    UNDEFINED_CONTAINER_ID: str = 'undefined_container'
    UNDEFINED_CONTAINER_NAME: str = 'Undefined'


# @dataclass
class ApiDevice():
    """Keys specific to Device resources"""
    CONTAINER_NAME: str = 'containerName'
    FQDN: str = 'fqdn'
    HOSTNAME: str = 'hostname'
    ID: str = 'key'
    IMAGE_BUNDLE: str = 'image_bundle'
    SERIAL: str = 'serialNumber'
    SYSMAC: str = 'systemMacAddress'


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
    configlet: ApiConfiglet = ApiConfiglet
    container: ApiContainer = ApiContainer
    device: ApiDevice = ApiDevice
    generic: ApiGeneric = ApiGeneric
    mappers: ApiMappers = ApiMappers
    task: ApiTask = ApiTask
