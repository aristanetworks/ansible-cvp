#!/usr/bin/python
# coding: utf-8 -*-
"""
    config.py - Declares the credential of the specified server
"""
import os

username = os.getenv('ARISTA_AVD_CV_USER', '')
password = os.getenv('ARISTA_AVD_CV_TOKEN', '')
server = os.getenv('ARISTA_AVD_CV_SERVER', '')
