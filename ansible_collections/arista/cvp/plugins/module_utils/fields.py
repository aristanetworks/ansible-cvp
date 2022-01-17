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

# from dataclasses import dataclass

# Section to build FACTS dictionary
FIELD_FACTS_DEVICE = 'cvp_devices'
FIELD_FACTS_CONTAINER = 'cvp_containers'
FIELD_FACTS_CONFIGLET = 'cvp_configlets'


# @dataclass
class Facts():
    """
    Facts Represent All fields specific to cv_facts_v3 module.
    """
    # Facts headers
    DEVICE: str = 'cvp_devices'
    CONTAINER: str = 'cvp_containers'
    CONFIGLET: str = 'cvp_configlets'
    # Cache Headers
    CACHE_CONTAINERS: str = 'containers'
    CACHE_MAPPERS: str = 'configlets_mappers'


# @dataclass
class ApiGeneric():
    PARENT_ID: str = 'parentContainerId'
    PARENT_NAME: str = 'parentContainerName'
    NAME: str = 'name'
    KEY: str = 'key'
    CONFIGLETS: str = 'configlets'


# @dataclass
class ApiContainer():
    ID: str = 'containerId'
    COUNT_DEVICE: str = 'childNetElementCount'
    COUNT_CONTAINER: str = 'childContainerCount'
    PARENT_CONTAINER_NAME: str = 'parentContainerName'
    PARENT_KEY: str = 'parentContainerKey'
    TOPOLOGY: str = 'topology'
    UNDEFINED_CONTAINER_ID: str = 'undefined_container'
    PARENT_NAME: str = 'parentName'
    KEY: str = 'Key'


# @dataclass
class ApiDevice():
    FQDN: str = 'fqdn'
    HOSTNAME: str = 'hostname'
    SYSMAC: str = 'systemMacAddress'
    SERIAL: str = 'serialNumber'
    ID: str = 'key'
    CONTAINER_NAME: str = 'containerName'
    IMAGE_BUNDLE: str = 'image_bundle'


# @dataclass
class ApiConfiglet():
    ID: str = 'configletId'


# @dataclass
class ApiMappers():
    OBJECT_ID: str = 'objectId'


# @dataclass
class ApiFields():
    generic: ApiGeneric = ApiGeneric
    device: ApiDevice = ApiDevice
    container: ApiContainer = ApiContainer
    configlet: ApiConfiglet = ApiConfiglet
    mappers: ApiMappers = ApiMappers
