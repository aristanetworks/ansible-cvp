#!/usr/bin/python
# coding: utf-8 -*-
"""
    config.py - Declares the credential of the specified server
"""
import os
from distutils.util import strtobool

user_token = os.getenv('ARISTA_AVD_CV_TOKEN')
server = os.getenv('ARISTA_AVD_CV_SERVER')
username = os.getenv('ARISTA_AVD_CV_USERNAME')
password = os.getenv('ARISTA_AVD_CV_PASSWORD')
provision_cv = strtobool(os.getenv('ARISTA_AVD_CV_PROVISION', 'true'))
cvaas = strtobool(os.getenv('ARISTA_AVD_CVAAS', 'true'))
