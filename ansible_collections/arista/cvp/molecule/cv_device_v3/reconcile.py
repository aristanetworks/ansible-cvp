#!/usr/bin/env python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from cvprac.cvp_client import CvpClient
import yaml
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# Setting variables
RECONCILE = 'RECONCILE_'  # Prefix for the configlet name
fixture_file = 'molecule/fixtures/cv_device_v3.yaml'

with open(fixture_file, encoding="utf-8") as f:
    dut = yaml.safe_load(f)

# load password from fixtures otherwise assume it's and ATD environemnt and read the password from
# the config file
if len(dut[0]["password"]) > 0:
    password = dut[0]["password"]
else:
    config_file = "/home/coder/.config/code-server/config.yaml"
    with open(config_file, encoding="utf-8") as f:
        password = yaml.safe_load(f)["password"]

# Connect to CloudVision
clnt = CvpClient()
clnt.set_log_level(log_level='WARNING')
clnt.connect([dut[0]["node"]], dut[0]["username"], password)

# Store device information
device = clnt.api.get_device_by_serial(dut[0]["device"])
dev_mac = device["systemMacAddress"]

# Reconcile device configuration
rc = clnt.api.get_device_configuration(dev_mac)
name = RECONCILE + device['serialNumber']
update = clnt.api.update_reconcile_configlet(dev_mac, rc, "", name, True)
addcfg = clnt.api.apply_configlets_to_device("auto-reconciling", device, [update['data']])
