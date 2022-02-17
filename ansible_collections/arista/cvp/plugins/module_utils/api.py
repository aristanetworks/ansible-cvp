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
import asyncio
import time
import functools
from typing import Callable, List
from cvprac.cvp_client import CvpClient
from concurrent.futures import ThreadPoolExecutor

LOGGER = logging.getLogger(__name__)


async def call(func: Callable[..., dict], args: List[dict]) -> List[dict]:
    """
    Query CloudVision using concurrent API calls.
    Take as argument a function that have one or multiple arbitrary arguments.
    The function must return a dictionary.
    This function can be a blocking call since it is run in a separate thread.

    The list args contains the arguments for each concurrent API call and thus defines the number of concurrent calls.

    This is a coroutine and can be used in asynchronous code to query multiple ressources concurently.

    Parameters
    ----------
    func : Callable[..., dict]
        Function to call
    args : List[dict]
        The arguments for each concurrent API call

    Returns
    -------
    List[dict]
        Aggregated results of concurrent API calls
    """
    now = time.time()
    loop = asyncio.get_running_loop()

    LOGGER.info('%s: Querying %s items', func.__name__, len(args))

    with ThreadPoolExecutor() as pool:
        responses = await asyncio.gather(*(loop.run_in_executor(pool,
                                           functools.partial(func, **kwargs))
                                           for kwargs in args))

    LOGGER.info('%s: Queried %s items in %ss', func.__name__, len(responses), time.time() - now)

    return responses


async def call_batch(func: Callable[[int, int], dict], item_per_call: int = 2) -> dict:
    """
    Query CloudVision using concurrent API calls.
    Take as argument a function that have the following signature: func(start:int, end:int).
    The function must return the following data structure:
    {
        "data": [
            {},
            {}
        ],
        "total": 2
    }

    This function can be a blocking call since it is run in a separate thread.

    The optional parameter item_per_call defines the number of item to retrieve per concurrent API call.

    This is a coroutine and can be used in asynchronous code to query multiple ressources concurently.

    Parameters
    ----------
    func : Callable[[int, int], dict]
        Function to call
    item_per_call : int, optional
        Number of item to retrieve per concurrent API call, by default 2

    Returns
    -------
    dict
        Aggregated results of concurrent API calls
    """
    now = time.time()
    data = []
    loop = asyncio.get_running_loop()
    first = func(start=0, end=1)
    total = first['total']
    data.extend(first['data'])

    if total == 1:
        LOGGER.info('%s: Collected 1 item in %ss', func.__name__, time.time() - now)
        return {'total': total, 'data': data}

    # Some cvprac calls are broken and ignore the start and end parameters
    if len(data) == total:
        LOGGER.info('%s: Collected %s items in %ss', func.__name__, len(data), time.time() - now)
        return {'total': total, 'data': data}

    LOGGER.info('%s: Collecting %s items, %s items per API call', func.__name__, total, item_per_call)

    with ThreadPoolExecutor() as pool:
        responses = await asyncio.gather(*(loop.run_in_executor(pool,
                                           functools.partial(func, start=i, end=i + item_per_call))
                                           for i in range(1, total, item_per_call)))

    for r in responses:
        data.extend(r['data'])
    LOGGER.info('%s: Collected %s items in %ss', func.__name__, len(data), time.time() - now)

    return {'total': total, 'data': data}


def get_configlets_by_name(client: CvpClient, names: List[str]) -> List[dict]:
    return asyncio.run(call(client.api.get_configlet_by_name, [{'name': i} for i in names]))


def get_configlets(client: CvpClient, **item_per_call) -> dict:
    return asyncio.run(call_batch(client.api.get_configlets, **item_per_call))


def get_images(client: CvpClient, **item_per_call) -> dict:
    return asyncio.run(call_batch(client.api.get_images, **item_per_call))


def get_containers(client: CvpClient, **item_per_call) -> dict:
    return asyncio.run(call_batch(client.api.get_containers, **item_per_call))


def update_configlets(client: CvpClient, configs: List[dict]) -> dict:
    """
    config example:
       {'name': 'my-configlet',
        'key': 'configlet_123456',
        'config': 'hostname EOS',
        'wait_task_ids': False
        }
    """
    return asyncio.run(call(client.api.update_configlet, configs))


def add_notes_to_configlets(client: CvpClient, configs: List[dict]) -> dict:
    """
    note example:
       {'key': 'configlet_123456',
        'note': 'my note'}
    """
    return asyncio.run(call(client.api.add_note_to_configlet, configs))


def get_images_and_configlets(client: CvpClient, **item_per_call) -> dict:
    async def run():
        r = await asyncio.gather(call_batch(client.api.get_configlets, **item_per_call),
                                 call_batch(client.api.get_images, **item_per_call))
        return r
    return asyncio.run(run())
