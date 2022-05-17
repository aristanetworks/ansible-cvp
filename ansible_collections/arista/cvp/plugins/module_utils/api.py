#!/usr/bin/python
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
import os
import asyncio
import time
import functools
from typing import Callable, List
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
    started_at = time.monotonic()
    loop = asyncio.get_running_loop()

    LOGGER.info('%s: Querying %s items', func.__name__, len(args))

    with ThreadPoolExecutor() as pool:
        responses = await asyncio.gather(*(loop.run_in_executor(pool,
                                           functools.partial(func, **kwargs))
                                           for kwargs in args))

    LOGGER.info('%s: Queried %s items in %ss', func.__name__, len(responses), time.monotonic() - started_at)

    return responses


async def call_batch(func: Callable[[int, int], dict], pagination_coeff: int = 4) -> dict:
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

    The optional parameter pagination_coeff influences the number of item retrieved per concurrent API call.
    A pagination_coeff value of 1 means the number API calls will be equal equal to the max_workers value on
    the execution machine. A value of 2 means the number of API calls will be half the max_workers value.
    In Python 3.8, max_workers value is min(32, os.cpu_count() + 4. This value defines the maximum of running
    concurrent threads of a ThreadPoolExecutor.

    This is a coroutine and can be used in asynchronous code to query multiple ressources concurently.

    Parameters
    ----------
    func : Callable[[int, int], dict]
        Function to call
    pagination_coeff : int, optional
        Influence the number of item retrieved per concurrent API call

    Returns
    -------
    dict
        Aggregated results of concurrent API calls
    """
    LOGGER.debug('%s: Collecting concurrently', func.__name__)
    started_at = time.monotonic()
    data = []
    loop = asyncio.get_running_loop()
    first = func(start=0, end=1)
    total = first['total']
    data.extend(first['data'])

    if total == 1:
        LOGGER.info('%s: Collected 1 item in %ss', func.__name__, time.monotonic() - started_at)
        return {'total': total, 'data': data}

    # Some cvprac calls ignore the start and end parameters
    if len(data) == total:
        LOGGER.info('%s: Collected %s items in %ss', func.__name__, len(data), time.monotonic() - started_at)
        return {'total': total, 'data': data}

    # min(32, os.cpu_count() + 4) is the max_workers value of ThreadPoolExecutor in Python 3.8
    item_per_call = int(total / min(32, os.cpu_count() + 4) * pagination_coeff)

    LOGGER.info('%s: Collecting %s items, %s items per API call', func.__name__, total, item_per_call)

    with ThreadPoolExecutor() as pool:
        responses = await asyncio.gather(*(loop.run_in_executor(pool,
                                           functools.partial(func, start=i, end=i + item_per_call))
                                           for i in range(1, total, item_per_call)))

    for r in responses:
        data.extend(r['data'])
    LOGGER.info('%s: Collected %s items in %ss', func.__name__, len(data), time.monotonic() - started_at)

    return {'total': total, 'data': data}


def get_configlets_by_name(client, names: List[str]) -> List[dict]:
    return asyncio.run(call(client.api.get_configlet_by_name, [{'name': i} for i in names]))


def get_configlets(client) -> dict:
    return asyncio.run(call_batch(client.api.get_configlets))


def get_images(client) -> dict:
    return asyncio.run(call_batch(client.api.get_images))


def get_containers(client) -> dict:
    return asyncio.run(call_batch(client.api.get_containers))


def update_configlets(client, configs: List[dict]) -> dict:
    """
    config example:
       {'name': 'my-configlet',
        'key': 'configlet_123456',
        'config': 'hostname EOS',
        'wait_task_ids': False
        }
    """
    return asyncio.run(call(client.api.update_configlet, configs))


def add_notes_to_configlets(client, configs: List[dict]) -> dict:
    """
    note example:
       {'key': 'configlet_123456',
        'note': 'my note'}
    """
    return asyncio.run(call(client.api.add_note_to_configlet, configs))


def get_images_and_configlets(client, **item_per_call) -> dict:
    async def run():
        r = await asyncio.gather(call_batch(client.api.get_configlets, **item_per_call),
                                 call_batch(client.api.get_images, **item_per_call))
        return r
    return asyncio.run(run())
