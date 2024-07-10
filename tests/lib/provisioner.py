#!/usr/bin/python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: skip-file
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# pylint:disable=duplicate-code
# flake8: noqa: W503
# flake8: noqa: W1202
# flake8: noqa: R0801
from __future__ import (absolute_import, division, print_function)
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from cvprac import cvp_client, cvp_client_errors
import logging
from typing import Optional, List, Dict
from .helpers import time_log
from .utils import cvp_login


"""
provisioner.py - Provides tool for provisioning CV before running Pytest
"""


class CloudvisionProvisioner():
    def __init__(self):
        self.cv = cvp_login()
        if not isinstance(self.cv, cvp_client.CvpClient):
            logging.error('Cloudvision instance not ready')
            sys.exit(1)

    def _get_valid_only(self, entries: List):
        return [entry for entry in entries if entry['is_valid_expected']]

    def configlets_provision(self, configlets: List):
        configlets = self._get_valid_only(entries=configlets)
        for configlet in configlets:
            if configlet['is_present_expected'] is False:
                try:
                    configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                    res = self.cv.api.delete_configlet(name=configlet['name'], key=configlet_id)
                except Exception as error_message:
                    logging.error(error_message)
            elif configlet['is_present_expected']:
                try:
                    res = self.cv.api.add_configlet(name=configlet['name'], config=configlet['config'])
                    configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                    self.cv.api.add_note_to_configlet(key=configlet_id, note='Provisioned by Pytest {}'.format(time_log()))
                except Exception as error_message:
                    logging.warning('{} - moving to update process'.format(error_message))
                    try:
                        logging.info('Fallback to update process for configlet {}'.format(configlet['name']))
                        configlet_id = self.cv.api.get_configlet_by_name(name=configlet['name'])['key']
                        res = self.cv.api.update_configlet(name=configlet['name'], key=configlet_id, config=configlet['config_expected'])
                        self.cv.api.add_note_to_configlet(key=configlet_id, note='Provisioned by Pytest {}'.format(time_log()))
                    except Exception as error_message:
                        logging.error(error_message)

    def configlets_push(self, configlets: List):
        logging.debug(' Received set of configlets to publish: {}'.format(configlets))
        for configlet_title, configlet_data in configlets.items():
            try:
                res = self.cv.api.add_configlet(
                    name=configlet_title,
                    config=configlet_data
                )
                configlet_id = self.cv.api.get_configlet_by_name(
                    name=configlet_title
                )['key']
                self.cv.api.add_note_to_configlet(
                    key=configlet_id,
                    note='Provisioned by Pytest {}'.format(time_log())
                )
            except Exception as error_message:
                logging.critical(error_message)


# Cleaner class to reset information in CVP
class CloudvisionCleaner():
    def __init__(self):
        self.topology_ordered = []
        self.clnt = cvp_login()

    # Execute all the cleanup actions
    def full_cleanup(self):
        self.task_cleanup()
        self.tempaction_cleanup()
        self.remove_devices()
        self.remove_all_containers()

    # Cancel all pending tasks
    def task_cleanup(self):
        pending_task_list = self.clnt.api.get_tasks_by_status('Pending')
        logging.info("List of tasks in pending state: {}".format(pending_task_list))
        for task in pending_task_list:
            logging.info("Cancelling task: {}".format(task['workOrderId']))
            result = self.clnt.api.cancel_task(task['workOrderId'])
            logging.info("Result: {}".format(result))

    # TODO: To confirm that this is working as expected - Delete all temp actions
    def tempaction_cleanup(self):
        result_delete_temp_action_list = self.clnt.post('/provisioning/deleteAllTempAction.do')
        logging.info("Result tempaction cleanup: {}".format(result_delete_temp_action_list))

    # Remove all the devices from provisioning (so they are re-added to the undefinied_container)
    def remove_devices(self):
        inventory = self.clnt.api.get_inventory()
        for device in inventory:
            logging.info("Removing from provisoning: {}".format(device['fqdn']))
            self.clnt.api.delete_device(device['systemMacAddress'])

    # Recursive function to get topology in the correct order
    def __build_container_topology(self, container):
        logging.info("Adding container [{}]".format(container['name']))
        new_entry = {"key": container['key'], "name": container['name'], "parentContainerId": container['parentContainerId']}
        self.topology_ordered.append(new_entry)
        for child_container in container['childContainerList']:
            self.__build_container_topology(child_container)

    # Remove all the containers
    def remove_all_containers(self):
        topology = self.clnt.api.filter_topology()
        self.__build_container_topology(topology['topology'])
        # Reversing the container list so we delete the container without child containers first
        self.topology_ordered.reverse()
        logging.info("Topology ordered is: {}".format([x['name'] for x in self.topology_ordered]))

        for container in self.topology_ordered:
            # Deleting the container if not root container or undefined container
            if container['key'] not in ['root', 'undefined_container']:
                parentName = [x['name'] for x in self.topology_ordered if x['key'] == container['parentContainerId']][0]
                logging.info("Deleting the container: {} - parent is {}".format(container['name'], parentName))
                result = self.clnt.api.delete_container(container['name'], container['key'], parentName, container['parentContainerId'])
                logging.info("Result: [{}]".format(container['name'], parentName, result))
