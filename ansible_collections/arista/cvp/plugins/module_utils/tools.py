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
import logging
try:
    import difflib
    HAS_DIFFLIB = True
except ImportError:
    HAS_DIFFLIB = False

LOGGER = logging.getLogger('arista.cvp.tools')
# replacement strings
WINDOWS_LINE_ENDING = '\r\n'
UNIX_LINE_ENDING = '\n'


def str_cleanup_line_ending(content):
    """
    str_cleanup_line_ending Cleanup line ending to use UNIX style and not Windows style

    Replace line ending from WINDOWS to UNIX

    Parameters
    ----------
    content : string
        String to cleanup

    Returns
    -------
    string
        Cleaned up string.
    """
    if isinstance(content, str):
        return content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
    return None


def compare(fromText, toText, fromName='', toName='', lines=10):
    """ Compare text string in 'fromText' with 'toText' and produce
        diffRatio - a score as a float in the range [0, 1] 2.0*M / T
          T is the total number of elements in both sequences,
          M is the number of matches.
          Score - 1.0 if the sequences are identical, and 0.0 if they have nothing in common.
        unified diff list
          Code	Meaning
          '- '	line unique to sequence 1
          '+ '	line unique to sequence 2
          '  '	line common to both sequences
          '? '	line not present in either input sequence
    """
    fromlines = str_cleanup_line_ending(content=fromText).splitlines(1)
    tolines = str_cleanup_line_ending(content=toText).splitlines(1)
    diff = list(difflib.unified_diff(
        fromlines, tolines, fromName, toName, n=lines))
    textComp = difflib.SequenceMatcher(None, fromText, toText)
    diffRatio = textComp.ratio()
    return [diffRatio, diff]

def isIterable(testing_object=None):
    """
    Test if an object is iterable or not.

    Test if an object is iterable or not. If yes return True, else return False.

    Parameters
    ----------
    testing_object : any, optional
        Object to test if it is iterable or not, by default None

    """
    try:
        some_object_iterator = iter(testing_object)  # noqa # pylint: disable=unused-variable
        return True
    except TypeError as te:  # noqa # pylint: disable=unused-variable
        return False


def match_filter(input, filter, default_always='all'):
    """
    Function to test if an object match userdefined filter.

    Function support list of string and string as filter.
    A default value is provided when calling function and if this default value for always matching is configured by user, then return True (Always matching)
    If filter is a list, then we iterate over the input and check if it matches an entry in the filter.

    Parameters
    ----------
    input : string
        Input to test of that match filter or not.
    filter : list
        List of string to compare against input.
    default_always : str, optional
        Keyword to consider as always matching, by default 'all'
    default_none : str, optional
        Keyword to consider as never matching, by default 'none'

    Returns
    -------
    bool
        True if input matchs filter, False in other situation
    """

    # W102 Workaround to avoid list as default value.
    if filter is None:
        LOGGER.critical(
            'Filter is not set, configure default value to [\'all\']')
        filter = ["all"]

    LOGGER.debug(" * is_in_filter - filter is %s", str(filter))
    LOGGER.debug(" * is_in_filter - input string is %s", str(input))

    if "all" in filter:
        return True
    elif any(element in input for element in filter):
        return True
    LOGGER.debug(" * is_in_filter - NOT matched")
    return False


def is_list_diff(list1, list2):
    """
    Check if 2 list have some differences.

    Parameters
    ----------
    list1 : list
        First list to compare.
    list2 : list
        Second list to compare.

    Returns
    -------
    boolean
        True if lists have diffs. False if not.
    """
    has_diff = False
    for entry1 in list1:
        if entry1 not in list2:
            has_diff = True
    for entry2 in list2:
        if entry2 not in list1:
            has_diff = True
    return has_diff


def is_in_filter(hostname_filter=None, hostname="eos"):
    """
    Check if device is part of the filter or not.

    Parameters
    ----------
    hostname_filter : list, optional
        Device filter, by default ['all']
    hostname : str
        Device hostname to compare against filter.

    Returns
    -------
    boolean
        True if device hostname is part of filter. False if not.
    """
    LOGGER.debug(" * is_in_filter - filter is %s", str(hostname_filter))
    LOGGER.debug(" * is_in_filter - hostname is %s", str(hostname))

    # W102 Workaround to avoid list as default value.
    if hostname_filter is None:
        hostname_filter = ["all"]

    if "all" in hostname_filter:
        return True
    elif any(element in hostname for element in hostname_filter):
        return True
    LOGGER.debug(" * is_in_filter - NOT matched")
    return False
