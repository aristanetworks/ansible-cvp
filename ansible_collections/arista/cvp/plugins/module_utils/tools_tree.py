#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=bare-except
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
import logging
import traceback
import json
from ansible.module_utils.six import string_types
try:
    from treelib import Tree
    HAS_TREELIB = True
except ImportError:
    HAS_TREELIB = False
    TREELIB_IMP_ERR = traceback.format_exc()


LOGGER = logging.getLogger('arista.cvp.tree')


# List of Ansible default containers
BUILTIN_CONTAINERS = ['Undefined', 'root']


def get_root_container(containers_fact, debug=True):
    """
    Extract name of the root container provided by cv_facts.

    Parameters
    ----------
    containers_fact : list
        List of containers to read from cv_facts

    Returns
    -------
    string
        Name of the root container, if not found, return Tenant as default value
    """
    for container in containers_fact:
        LOGGER.debug('working on container %s', str(container))
        if container['Key'] == 'root':
            # if debug:
            LOGGER.info(
                '! ROOT container has name %s', container['Name'])
            return container['Name']
    return 'Tenant'


def tree_to_list(json_data, myList):
    """
    Transform a tree structure into a list of object to create CVP.

    Because some object have to be created in a specific order on CVP side,
    this function parse a tree to provide an ordered list of elements to create

    Example:
    --------
        >>> containers = {"Tenant": {"children": [{"Fabric": {"children": [{"Leaves": {"children": ["MLAG01", "MLAG02"]}}, "Spines"]}}]}}
        >>> print tree_to_list(containers=containers, myList=list())
        [u'Tenant', u'Fabric', u'Leaves', u'MLAG01', u'MLAG02', u'Spines']

    Parameters
    ----------
    json_data : [type]
        [description]
    myList : list
        Ordered list of element to create on CVP / recursive function

    Returns
    -------
    list
        Ordered list of element to create on CVP
    """
    # Cast input to be encoded as JSON structure.
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    # If it is a dictionary object,
    # it means we have to go through it to extract content
    if isinstance(json_data, dict):
        # Get key as it is a container name we want to save.
        for k1, v1 in json_data.items():
            # Ensure we are getting children element.
            if isinstance(v1, dict):
                for k2, v2 in v1.items():
                    if 'children' == k2:
                        # Save entry as we are dealing with an object to create
                        myList.append(k1)
                        for e in v2:
                            # Move to next element with a recursion
                            tree_to_list(
                                json_data=json.dumps(e), myList=myList)
    # We are facing a end of a branch with a list of leaves.
    elif isinstance(json_data, list):
        for entry in json_data:
            myList.append(entry)
    # We are facing a end of a branch with a single leaf.
    elif isinstance(json_data, string_types):
        myList.append(json_data)
    return myList


def tree_build_from_dict(containers=None, root='Tenant'):
    """
    Build a tree based on a unsorted dictConfig(config).

    Build a tree of containers based on an unsorted dict of containers.

    Example:
    --------
        >>> containers = {'Fabric': {'parent_container': 'Tenant'},
            'Leaves': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Fabric'},
            'MLAG01': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Leaves'},
            'MLAG02': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Leaves'},
            'Spines': {'configlets': ['container_configlet'],
                        'devices': ['veos01'],
                        'images': ['4.22.0F'],
                        'parent_container': 'Fabric'}}
        >>> print(tree_build_from_dict(containers=containers))
            {"Tenant": {"children": [{"Fabric": {"children": [{"Leaves": {"children": ["MLAG01", "MLAG02"]}}, "Spines"]}}]}}
    Parameters
    ----------
    containers : dict, optional
        Container topology to create on CVP, by default None
    root: string, optional
        Name of container to consider as root for topology, by default Tenant

    Returns
    -------
    json
        tree topology
    """
    # Create tree object
    tree = Tree()  # Create the base node
    previously_created = list()
    # Create root node to mimic CVP behavior
    LOGGER.debug('containers list is %s', str(containers))
    LOGGER.debug('root container is set to: %s', str(root))
    tree.create_node(root, root)
    # Iterate for first level of containers directly attached under root.
    for container_name, container_info in containers.items():
        if container_info['parent_container'] in [root]:
            previously_created.append(container_name)
            tree.create_node(container_name, container_name,
                             parent=container_info['parent_container'])
            LOGGER.debug(
                'create root tree entry with: %s', str(container_name))
    # Loop since expected tree is not equal to number of entries in container topology
    while (len(tree.all_nodes()) < len(containers)):
        LOGGER.debug(
            ' Tree has size: %s - Containers has size: %s', str(len(tree.all_nodes())), str(len(containers)))
        for container_name, container_info in containers.items():
            if tree.contains(container_info['parent_container']) and container_info['parent_container'] not in [root]:
                try:
                    LOGGER.debug(
                        'create new node with: %s', str(container_name))
                    tree.create_node(container_name, container_name,
                                     parent=container_info['parent_container'])
                except:  # noqa E722
                    continue
    return tree.to_json()


def tree_build_from_list(containers, root='Tenant'):
    """
    Build a tree based on a unsorted list.

    Build a tree of containers based on an unsorted list of containers.

    Example:
    --------
        >>> containers = [
            {
                "childContainerKey": null,
                "configlets": [],
                "devices": [],
                "imageBundle": "",
                "key": "root",
                "name": "Tenant",
                "parentName": null
            },
            {
                "childContainerKey": null,
                "configlets": [
                    "veos3-basic-configuration"
                ],
                "devices": [
                    "veos-1"
                ],
                "imageBundle": "",
                "key": "container_43_840035860469981",
                "name": "staging",
                "parentName": "Tenant"
            }]
        >>> print(tree_build_from_list(containers=containers))
            {"Tenant": {"children": [{"Fabric": {"children": [{"Leaves": {"children": ["MLAG01", "MLAG02"]}}, "Spines"]}}]}}
    Parameters
    ----------
    containers : dict, optional
        Container topology to create on CVP, by default None
    root: string, optional
        Name of container to consider as root for topology, by default Tenant

    Returns
    -------
    json
        tree topology
    """
    # Create tree object
    tree = Tree()  # Create the base node
    previously_created = list()
    # Create root node to mimic CVP behavior
    LOGGER.debug('containers list is %s', str(containers))
    tree.create_node(root, root)
    # Iterate for first level of containers directly attached under root.
    for cvp_container in containers:
        if cvp_container['parentName'] is None:
            continue
        if cvp_container['parentName'] in [root]:
            LOGGER.debug(
                'found container attached to %s: %s', str(root), str(cvp_container))
            previously_created.append(cvp_container['name'])
            tree.create_node(
                cvp_container['name'], cvp_container['name'], parent=cvp_container['parentName'])
    # Loop since expected tree is not equal to number of entries in container topology
    while len(tree.all_nodes()) < len(containers):
        for cvp_container in containers:
            # and cvp_container['parentName'] not in ['Tenant']
            if tree.contains(cvp_container['parentName']):
                try:
                    tree.create_node(
                        cvp_container['name'], cvp_container['name'], parent=cvp_container['parentName'])
                except:  # noqa E722
                    continue
    return tree.to_json()


def tree_build(containers=None, root='Tenant'):
    """
    Triage function to build a tree.

    Call appropriate function wether we are using list() or dict() as input.

    Parameters
    ----------
    containers : dict or list, optional
        Containers' structure to use to build tree, by default None
    root: string, optional
        Name of container to consider as root for topology, by default Tenant

    """
    if isinstance(containers, dict):
        return tree_build_from_dict(containers=containers, root=root)
    elif isinstance(containers, list):
        return tree_build_from_list(containers=containers, root=root)
    return None


def locate_relative_root_container(containers_topology):
    """
    Function to locate root container of partial topology

    In case user provides a partial topology, it is required to locate root of
    this topology and not CVP root container. it is useful in case of a partial
    deletion and not complete tree.

    Parameters
    ----------
    containers_topology : dict
        User's defined intended topology

    Returns
    -------
    string
        Name of the relative root container. None if not found.
    """
    LOGGER.debug('relative intended topology is: %s',
                 str(containers_topology))
    for container_name, container in containers_topology.items():
        if container['parent_container'] not in containers_topology.keys():
            return container_name
    return None
