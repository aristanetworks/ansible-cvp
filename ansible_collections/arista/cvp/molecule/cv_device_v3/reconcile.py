#!/usr/bin/env python
# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from cvprac.cvp_client import CvpClient
import ssl
import yaml
ssl._create_default_https_context = ssl._create_unverified_context
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
clnt = CvpClient()
clnt.set_log_level(log_level='WARNING')

# load the ATD password from the code-server config file
# to test this in another environment this var will need to be updated
with open("/home/coder/.config/code-server/config.yaml", encoding="utf-8") as f:
    password = yaml.safe_load(f)["password"]

# Connect to CVP
clnt.connect(['192.168.0.5'],'arista', password)

# Store device information
device = clnt.api.get_device_by_serial('s1-leaf1')
dev_mac = device['systemMacAddress']

# Reconcile device configuration
rc = clnt.api.get_device_configuration(dev_mac)
name = 'RECONCILE_' + device['serialNumber']
update = clnt.api.update_reconcile_configlet(dev_mac, rc, "", name, True)
addcfg = clnt.api.apply_configlets_to_device("auto-reconciling",device,[update['data']])
