#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#
# Copyright 2022 Arista Networks
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
    VALIDATE_MODE_IGNORE: str = 'ignore'
    VALIDATE_MODE_STOP_ON_WARNING: str = 'stop_on_warning'
    VALIDATE_MODE_STOP_ON_ERROR: str = 'stop_on_error'
    INVENTORY_MODE_LOOSE: str = 'loose'
    INVENTORY_MODE_STRICT: str = 'strict'
    STATE_MODE_ABSENT: str = 'factory_reset'
    STATE_MODE_PRESENT: str = 'present'
    STATE_MODE_DECOMM: str = 'absent'
    STATE_MODE_REMOVE: str = 'provisioning_reset'


# @dataclass
class FactsResponseFields():
    """Facts Represent All fields specific to cv_facts_v3 module"""
    CACHE_CONTAINERS: str = 'containers'
    CACHE_MAPPERS: str = 'configlets_mappers'
    CONFIGLET: str = 'cvp_configlets'
    CONTAINER: str = 'cvp_containers'
    DEVICE: str = 'cvp_devices'
    IMAGE_BUNDLE: str = 'cvp_image_bundle'
    IMAGE: str = 'cvp_images'
    TASK: str = 'cvp_tasks'


# @dataclass
class ContainerResponseFields():
    """Fields to build output of cv_container_v3 module"""
    CONFIGLETS_ATTACHED: str = 'configlets_attached'
    CONFIGLETS_DETACHED: str = 'configlets_detached'
    CONTAINER_ADDED: str = 'container_added'
    CONTAINER_DELETED: str = 'container_deleted'
    BUNDLE_ATTACHED: str = 'bundle_attached'
    BUNDLE_DETACHED: str = 'bundle_detached'


# @dataclass
class DeviceResponseFields():
    """Fields to build output of cv_device_v3 module"""
    CONFIGLET_ATTACHED: str = 'configlets_attached'
    CONFIGLET_DETACHED: str = 'configlets_detached'
    CONFIGLET_VALIDATED: str = 'configlets_validated'
    DEVICE_DEPLOYED: str = 'devices_deployed'
    DEVICE_MOVED: str = 'devices_moved'
    DEVICE_RESET: str = 'devices_reset'
    BUNDLE_ATTACHED: str = 'bundle_attached'
    BUNDLE_DETACHED: str = 'bundle_detached'
    DEVICE_DECOMMISSIONED: str = 'devices_decommissioned'
    DEVICE_REMOVED: str = 'devices_removed'
