#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
#


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class CvElement(object):
    """
    CvElement Structure for simple element representation
    """

    def __init__(self, cv_data: dict):
        self.__cv_data = cv_data

    @property
    def name(self):
        """
        name Getter to expose NAME field

        Returns
        -------
        str
            Value of KEY field
        """
        if 'name' in self.__cv_data:
            return self.__cv_data['name']
        return None

    @property
    def key(self):
        """
        key Getter to expose KEY field

        Returns
        -------
        str
            Value of the KEY field
        """
        if 'key' in self.__cv_data:
            return self.__cv_data['key']

    @property
    def reconciled(self):
        """
        key Getter to expose RECONCILED field

        Returns
        -------
        str
            Value of the KEY field
        """
        if 'reconciled' in self.__cv_data:
            return self.__cv_data['reconciled']

    @property
    def data(self):
        """
        data Getter to expose structure in a dict way

        Returns
        -------
        dict
            A dict with KEY and NAME data
        """
        return self.__cv_data
