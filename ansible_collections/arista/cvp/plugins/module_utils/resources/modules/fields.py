#!/usr/bin/env python
# coding: utf-8 -*-
#
# GNU General Public License v3.0+
#
# Copyright 2022 Arista Networks AS-EMEA
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


# @dataclass
class ModuleOptionValues():
    """Values for modules options"""
    APPLY_MODE_LOOSE: str = 'loose'
    APPLY_MODE_STRICT: str = 'strict'
    STATE_MODE_ABSENT: str = 'factory_reset'
    STATE_MODE_PRESENT: str = 'present'


# @dataclass
class FactsResponseFields():
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
