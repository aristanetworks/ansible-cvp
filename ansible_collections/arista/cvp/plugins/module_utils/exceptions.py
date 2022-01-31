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

from enum import Enum, auto
from typing import Callable


class CVPRessource(Enum):
    """Enumeration that defines possible ressource in CVP"""
    DEVICE = auto()
    CONTAINER = auto()
    CONFIGLET = auto()
    TASK = auto()

    def __str__(self):
        return str(self.name).lower()


class AnsibleCVPError(Exception):
    """Base class for exceptions in ansible-cvp collection"""
    pass


class AnsibleCVPApiError(Exception):
    """Exception raised when an API-related error occurs"""
    def __init__(self, cvprac_method: Callable, message: str) -> None:
        """
        Constructor for the AnsibleCVPApiError class

        Parameters
        ----------
        cvprac_method : Callable
            The cvprac module method called
        message : str
            Description of the context in which the error occured
        """
        self.cvprac_method = cvprac_method
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.cvprac_method.__name__} -> {self.message}'


class AnsibleCVPNotFoundError(Exception):
    """Raised when the ressource is not found in CloudVision instance."""
    def __init__(self, name: str, type: CVPRessource, message: str = None) -> None:
        """
        Constructor for the AnsibleCVPNotFoundError class

        Parameters
        ----------
        name : str
            The ressource name
        type : CVPRessource
            The ressource type
        message : str, optional
            Description of the context in which the error occured
        """
        self.name = name
        self.type = type
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if self.message:
            return f'{self.type} {self.name} -> {self.message}'
        else:
            return f'{self.type} {self.name}'
