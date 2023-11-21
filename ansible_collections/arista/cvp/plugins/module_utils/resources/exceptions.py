#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
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
