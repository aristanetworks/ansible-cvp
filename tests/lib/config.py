#!/usr/bin/python
# coding: utf-8 -*-
"""
    config.py - Declares the credential of the specified server
"""
import os

user_token = os.getenv('ARISTA_AVD_CV_TOKEN', 'unset_token')
server = os.getenv('ARISTA_AVD_CV_SERVER', '')
