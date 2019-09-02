#
# Copyright (c) 2017, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
''' Class containing calls to CVP RESTful API.
'''
import os
# This import is for proper file IO handling support for both Python 2 and 3
# pylint: disable=redefined-builtin
from io import open

from cvprac.cvp_client_errors import CvpApiError

try:
    from urllib import quote_plus as qplus
except (AttributeError, ImportError):
    from urllib.parse import quote_plus as qplus


class CvpApi(object):
    ''' CvpApi class contains calls to CVP RESTful API.  The RESTful API
        parameters are passed in as parameters to the method.  The results of
        the RESTful API call are converted from json to a dict and returned.
        Where needed minimal processing is performed on the results.
        Any method that does a cvprac get or post call could raise the
        following errors:

        ConnectionError: A ConnectionError is raised if there was a network
            problem (e.g. DNS failure, refused connection, etc)
        CvpApiError: A CvpApiError is raised if there was a JSON error.
        CvpRequestError: A CvpRequestError is raised if the request is not
            properly constructed.
        CvpSessionLogOutError: A CvpSessionLogOutError is raised if
            reponse from server indicates session was logged out.
        HTTPError: A HTTPError is raised if there was an invalid HTTP response.
        ReadTimeout: A ReadTimeout is raised if there was a request
            timeout when reading from the connection.
        Timeout: A Timeout is raised if there was a request timeout.
        TooManyRedirects: A TooManyRedirects is raised if the request exceeds
            the configured number of maximum redirections
        ValueError: A ValueError is raised when there is no valid
            CVP session.  This occurs because the previous get or post request
            failed and no session could be established to a CVP node.  Destroy
            the class and re-instantiate.
    '''
    # pylint: disable=too-many-public-methods
    # pylint: disable=too-many-lines

    def __init__(self, clnt, request_timeout=30):
        ''' Initialize the class.

            Args:
                clnt (obj): A CvpClient object
        '''
        self.clnt = clnt
        self.log = clnt.log
        self.request_timeout = request_timeout

    def get_cvp_info(self):
        ''' Returns information about CVP.

            Returns:
                cvp_info (dict): CVP Information
        '''
        data = self.clnt.get('/cvpInfo/getCvpInfo.do',
                             timeout=self.request_timeout)
        if 'version' in data and self.clnt.apiversion is None:
            self.clnt.set_version(data['version'])
        return data

    def get_task_by_id(self, task_id):
        ''' Returns the current CVP Task status for the task with the specified
            TaskId.

            Args:
                task_id (int): CVP task identifier

            Returns:
                task (dict): The CVP task for the associated Id.  Returns None
                    if the task_id was invalid.
        '''
        self.log.debug('get_task_by_id: task_id: %s' % task_id)
        try:
            task = self.clnt.get('/task/getTaskById.do?taskId=%s' % task_id,
                                 timeout=self.request_timeout)
        except CvpApiError as error:
            self.log.debug('Caught error: %s attempting to get task.' % error)
            # Catch an invalid task_id error and return None
            return None
        return task

    def get_tasks_by_status(self, status, start=0, end=0):
        ''' Returns a list of tasks with the given status.

            Args:
                status (str): Task status
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                tasks (list): The list of tasks
        '''
        self.log.debug('get_tasks_by_status: status: %s' % status)
        data = self.clnt.get(
            '/task/getTasks.do?queryparam=%s&startIndex=%d&endIndex=%d' %
            (status, start, end), timeout=self.request_timeout)
        return data['data']

    def get_tasks(self, start=0, end=0):
        ''' Returns a list of all the tasks.

            Args:
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                tasks (dict): The 'total' key contains the number of tasks,
                    the 'data' key contains a list of the tasks.
        '''
        self.log.debug('get_tasks:')
        return self.clnt.get('/task/getTasks.do?queryparam=&startIndex=%d&'
                             'endIndex=%d' % (start, end),
                             timeout=self.request_timeout)

    def get_logs_by_id(self, task_id, start=0, end=0):
        ''' Returns the log entries for the task with the specified TaskId.

            Args:
                task_id (int): CVP task identifier
                start (int): The first log entry to return.  Default is 0.
                end (int): The last log entry to return.  Default is 0 which
                    means to return all log entries.  Can be a large number to
                    indicate the last log entry.

            Returns:
                task (dict): The CVP log for the associated Id.  Returns None
                    if the task_id was invalid.
        '''
        self.log.debug('get_log_by_id: task_id: %s' % task_id)
        return self.clnt.get('/task/getLogsById.do?id=%s&queryparam='
                             '&startIndex=%d&endIndex=%d' %
                             (task_id, start, end),
                             timeout=self.request_timeout)

    def add_note_to_task(self, task_id, note):
        ''' Add notes to the task.

            Args:
                task_id (str): Task ID
                note (str): Note to add to the task
        '''
        self.log.debug('add_note_to_task: task_id: %s note: %s' %
                       (task_id, note))
        data = {'workOrderId': task_id, 'note': note}
        self.clnt.post('/task/addNoteToTask.do', data=data,
                       timeout=self.request_timeout)

    def execute_task(self, task_id):
        ''' Execute the task.  Note that if the task has failed then inspect
            the task logs to determine why the task failed.  If you see:

              Failure response received from the netElement: Unauthorized User

            then it means that the netelement does not have the same user ID
            and/or password as the CVP user executing the task.

            Args:
                task_id (str): Task ID
        '''
        self.log.debug('execute_task: task_id: %s' % task_id)
        data = {'data': [task_id]}
        return self.clnt.post('/task/executeTask.do', data=data,
                              timeout=self.request_timeout)

    def cancel_task(self, task_id):
        ''' Cancel the task

            Args:
                task_id (str): Task ID
        '''
        self.log.debug('cancel_task: task_id: %s' % task_id)
        data = {'data': [task_id]}
        return self.clnt.post('/task/cancelTask.do', data=data,
                       timeout=self.request_timeout)

    def get_configlets(self, start=0, end=0):
        ''' Returns a list of all defined configlets.

            Args:
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
        '''
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        configlets = self.clnt.get('/configlet/getConfiglets.do?'
                                   'startIndex=%d&endIndex=%d' % (start, end),
                                   timeout=self.request_timeout)
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            return configlets
        else:
            self.log.debug('v2 Inventory API Call')
            # New API getConfiglets does not return the actual configlet config
            # Get the actual configlet config using getConfigletByName
            if 'data' in configlets:
                for configlet in configlets['data']:
                    full_cfglt_data = self.get_configlet_by_name(
                        configlet['name'])
                    configlet['config'] = full_cfglt_data['config']
            return configlets

    def get_configlet_builder(self, c_id):
        ''' Returns the configlet builder data for the given configlet ID.

            Args:
                c_id (str): The ID (key) for the configlet to be queried.
        '''
        return self.clnt.get('/configlet/getConfigletBuilder.do?id=%s'
                             % c_id, timeout=self.request_timeout)

    def get_configlet_by_name(self, name):
        ''' Returns the configlet with the specified name

            Args:
                name (str): Name of the configlet.  Can contain spaces.

            Returns:
                configlet (dict): The configlet dict.
        '''
        self.log.debug('get_configlets_by_name: name: %s' % name)
        return self.clnt.get('/configlet/getConfigletByName.do?name=%s'
                             % qplus(name), timeout=self.request_timeout)

    def get_configlets_by_container_id(self, c_id, start=0, end=0):
        ''' Returns a list of configlets applied to the given container.

            Args:
                c_id (str): The container ID (key) to query.
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
        '''
        return self.clnt.get('/provisioning/getConfigletsByContainerId.do?'
                             'containerId=%s&startIndex=%d&endIndex=%d'
                             % (c_id, start, end),
                             timeout=self.request_timeout)

    def get_configlets_by_netelement_id(self, d_id, start=0, end=0):
        ''' Returns a list of configlets applied to the given device.

            Args:
                d_id (str): The device ID (key) to query.
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
        '''
        return self.clnt.get('/provisioning/getConfigletsByNetElementId.do?'
                             'netElementId=%s&startIndex=%d&endIndex=%d'
                             % (d_id, start, end),
                             timeout=self.request_timeout)

    def get_configlet_history(self, key, start=0, end=0):
        ''' Returns the configlet history.

            Args:
                key (str): Key for the configlet.
                start (int): The first configlet entry to return.  Default is 0
                end (int): The last configlet entry to return.  Default is 0
                    which means to return all configlet entries.  Can be a
                    large number to indicate the last configlet entry.

            Returns:
                history (dict): The configlet dict with the changes from
                    most recent to oldest.
        '''
        self.log.debug('get_configlets_history: key: %s' % key)
        return self.clnt.get('/configlet/getConfigletHistory.do?configletId='
                             '%s&queryparam=&startIndex=%d&endIndex=%d' %
                             (key, start, end), timeout=self.request_timeout)

    def get_inventory(self, start=0, end=0, query=''):
        ''' Returns the a dict of the net elements known to CVP.

            Args:
                start (int): The first inventory entry to return.  Default is 0
                end (int): The last inventory entry to return.  Default is 0
                    which means to return all inventory entries.  Can be a
                    large number to indicate the last inventory entry.
                query (string): A value that can be used as a match to filter
                    returned inventory list. For example get all switches that
                    are running a specific version of EOS.
        '''
        self.log.debug('get_inventory: called')
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            data = self.clnt.get('/inventory/getInventory.do?'
                                 'queryparam=%s&startIndex=%d&endIndex=%d' %
                                 (qplus(query), start, end),
                                 timeout=self.request_timeout)
            return data['netElementList']
        else:
            self.log.debug('v2 Inventory API Call')
            data = self.clnt.get('/inventory/devices?provisioned=true',
                                 timeout=self.request_timeout)
            for dev in data:
                dev['key'] = dev['systemMacAddress']
                dev['deviceInfo'] = dev['deviceStatus'] = dev['status']
                dev['isMLAGEnabled'] = dev['mlagEnabled']
                dev['isDANZEnabled'] = dev['danzEnabled']
                dev['parentContainerId'] = dev['parentContainerKey']
                dev['bootupTimeStamp'] = dev['bootupTimestamp']
                dev['internalBuildId'] = dev['internalBuild']
                if 'taskIdList' not in dev:
                    dev['taskIdList'] = []
                if 'tempAction' not in dev:
                    dev['tempAction'] = None
                dev['memTotal'] = 0
                dev['memFree'] = 0
                dev['sslConfigAvailable'] = False
                dev['sslEnabledByCVP'] = False
                dev['lastSyncUp'] = 0
                dev['type'] = 'netelement'
                dev['dcaKey'] = None
                parent_container = self.get_container_by_id(
                    dev['parentContainerKey'])
                if parent_container is not None:
                    dev['containerName'] = parent_container['name']
                else:
                    dev['containerName'] = ''
            return data

    def add_device_to_inventory(self, device_ip, parent_name, parent_key):
        ''' Add the device to the specified parent container.

            Args:
                device_ip (str): ip address of device we are adding
                parent_name (str): Parent container name
                parent_key (str): Parent container key
        '''
        self.log.debug('add_device_to_inventory: called')
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            data = {'data': [
                {
                    'containerName': parent_name,
                    'containerId': parent_key,
                    'containerType': 'Existing',
                    'ipAddress': device_ip,
                    'containerList': []
                }]}
            self.clnt.post('/inventory/add/addToInventory.do?'
                           'startIndex=0&endIndex=0', data=data,
                           timeout=self.request_timeout)
        else:
            self.log.debug('v2 Inventory API Call')
            data = {'hosts': [device_ip]}
            self.clnt.post('/inventory/devices', data=data,
                           timeout=self.request_timeout)
            dev = None
            devices = self.get_inventory()
            for device in devices:
                if 'ipAddress' in device and device['ipAddress'] == device_ip:
                    dev = device
                    break
            if dev is not None:
                container = {'key': parent_key, 'name': parent_name}
                self.move_device_to_container('add_device_to_inventory API v2',
                                              dev, container, False)

    def retry_add_to_inventory(self, device_mac, device_ip, username,
                               password):
        '''Retry addition of device to Cvp inventory

            Args:
                device_mac (str): MAC address of device
                device_ip (str): ip address assigned to device
                username (str): username for device login
                password (str): password for user
        '''
        self.log.debug('retry_add_to_inventory: called')
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            data = {"key": device_mac,
                    "ipAddress": device_ip,
                    "userName": username,
                    "password": password}
            self.clnt.post('/inventory/add/retryAddDeviceToInventory.do?'
                           'startIndex=0&endIndex=0',
                           data=data,
                           timeout=self.request_timeout)
        else:
            self.log.debug('v2 Inventory API Call')
            self.log.warning(
                'retry_add_to_inventory: not implemented for v2 APIs')

    def delete_device(self, device_mac):
        '''Delete the device and its pending tasks from Cvp inventory

            Args:
                device_mac (str): mac address of device we are deleting
            Returns:
                data (dict): Contains success or failure message
        '''
        self.log.debug('delete_device: called')
        return self.delete_devices([device_mac])

    def delete_devices(self, device_macs):
        '''Delete the device and its pending tasks from Cvp inventory

            Args:
                device_macs (list): list of mac address for
                                    devices we're deleting
            Returns:
                data (dict): Contains success or failure message
        '''
        self.log.debug('delete_devices: called')
        data = {'data': device_macs}
        return self.clnt.post('/inventory/deleteDevices.do?', data=data,
                              timeout=self.request_timeout)

    def get_non_connected_device_count(self):
        '''Returns number of devices not accessible/connected in the temporary
           inventory.

            Returns:
                data (int): Number of temporary inventory devices not
                            accessible/connected
        '''
        self.log.debug('get_non_connected_device_count: called')
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            data = self.clnt.get(
                '/inventory/add/getNonConnectedDeviceCount.do',
                timeout=self.request_timeout)
            return data['data']
        else:
            self.log.debug('v2 Inventory API Call')
            data = self.clnt.get('/inventory/devices?provisioned=false',
                                 timeout=self.request_timeout)
            unprovisioned_devs = 0
            for dev in data:
                if 'status' in dev and dev['status'] == '':
                    unprovisioned_devs += 1
            return unprovisioned_devs

    def save_inventory(self):
        '''Saves Cvp inventory state
        '''
        self.log.debug('save_inventory: called')
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            return self.clnt.post('/inventory/add/saveInventory.do',
                                  timeout=self.request_timeout)
        else:
            self.log.debug('v2 Inventory API Call')
            message = 'Save Inventory not implemented/necessary for' +\
                      ' CVP 2018.2 and beyond'
            data = {'data': 0, 'message': message}
            return data

    def get_devices_in_container(self, name):
        ''' Returns a dict of the devices under the named container.

            Args:
                name (str): The name of the container to get devices from
        '''
        self.log.debug('get_devices_in_container: called')
        devices = []
        container = self.get_container_by_name(name)
        if container:
            all_devices = self.get_inventory(0, 0, name)
            for device in all_devices:
                if device['parentContainerId'] == container['key']:
                    devices.append(device)
        return devices

    def get_device_by_name(self, fqdn):
        ''' Returns the net element device dict for the devices fqdn name.

            Args:
                fqdn (str): Fully qualified domain name of the device.

            Returns:
                device (dict): The net element device dict for the device if
                    otherwise returns an empty hash.
        '''
        self.log.debug('get_device_by_name: fqdn: %s' % fqdn)
        data = self.get_inventory(start=0, end=0, query=fqdn)
        if len(data) > 0:
            for netelement in data:
                if netelement['fqdn'] == fqdn:
                    device = netelement
                    break
            else:
                device = {}
        else:
            device = {}
        return device

    def get_device_configuration(self, device_mac):
        ''' Returns the running configuration for the device provided.

            Args:
                device_mac (str): Mac address of the device to get the running
                    configuration for.

            Returns:
                device (dict): The net element device dict for the device if
                    otherwise returns an empty hash.
        '''
        self.log.debug('get_device_configuration: device_mac: %s' % device_mac)
        data = self.clnt.get('/inventory/getInventoryConfiguration.do?'
                             'netElementId=%s' % device_mac,
                             timeout=self.request_timeout)
        running_config = ''
        if 'output' in data:
            running_config = data['output']
        return running_config

    def get_containers(self, start=0, end=0):
        ''' Returns a list of all the containers.

            Args:
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                containers (dict): The 'total' key contains the number of
                containers, the 'data' key contains a list of the containers
                with associated info.
        '''
        self.log.debug('Get list of containers')
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            return self.clnt.get('/inventory/add/searchContainers.do?'
                                 'startIndex=%d&endIndex=%d' % (start, end))
        else:
            self.log.debug('v2 Inventory API Call')
            containers = self.clnt.get('/inventory/containers')
            for container in containers:
                container['name'] = container['Name']
                container['key'] = container['Key']
                full_cont_info = self.get_container_by_id(
                    container['Key'])
                if (full_cont_info is not None and
                        #container['Name'] != 'Tenant'):
                        container['Key'] != 'root'):
                    container['parentName'] = full_cont_info['parentName']
                    full_parent_info = self.get_container_by_name(
                        full_cont_info['parentName'])
                    if full_parent_info is not None:
                        container['parentId'] = full_parent_info['key']
                    else:
                        container['parentId'] = None
                else:
                    container['parentName'] = None
                    container['parentId'] = None
                container['type'] = None
                container['id'] = 21
                container['factoryId'] = 1
                container['userId'] = None
                container['childContainerId'] = None
            return {'data': containers, 'total': len(containers)}

    def get_container_by_name(self, name):
        ''' Returns a container that exactly matches the name.

            Args:
                name (str): String to search for in container names.

            Returns:
                container (dict): Container info in dictionary format or None
        '''
        self.log.debug('Get info for container %s' % name)
        conts = self.clnt.get('/provisioning/searchTopology.do?queryParam=%s'
                              '&startIndex=0&endIndex=0' % qplus(name))
        if conts['total'] > 0 and conts['containerList']:
            for cont in conts['containerList']:
                if cont['name'] == name:
                    return cont
        return None

    def get_container_by_id(self, key):
        ''' Returns a container for the given id.

            Args:
                key (str): String ID for container to find.

            Returns:
                container (dict): Container info in dictionary format or None
        '''
        self.log.debug('Get info for container %s' % key)
        return self.clnt.get('/provisioning/getContainerInfoById.do?'
                             'containerId=%s' % qplus(key))

    def get_configlets_by_device_id(self, mac, start=0, end=0):
        ''' Returns the list of configlets applied to a device.

            Args:
                mac (str): Device mac address (i.e. device id)
                start (int): The first configlet entry to return.  Default is 0
                end (int): The last configlet entry to return.  Default is 0
                    which means to return all configlet entries.  Can be a
                    large number to indicate the last configlet entry.

            Returns:
                configlets (list): The list of configlets applied to the device
        '''
        self.log.debug('get_configlets_by_device: mac: %s' % mac)
        data = self.clnt.get('/provisioning/getConfigletsByNetElementId.do?'
                             'netElementId=%s&queryParam=&startIndex=%d&'
                             'endIndex=%d' % (mac, start, end),
                             timeout=self.request_timeout)
        return data['configletList']

    def add_configlet(self, name, config):
        ''' Add a configlet and return the key for the configlet.

            Args:
                name (str): Configlet name
                config (str): Switch config statements

            Returns:
                key (str): The key for the configlet
        '''
        self.log.debug('add_configlet: name: %s config: %s' % (name, config))
        body = {'name': name, 'config': config}
        # Create the configlet
        self.clnt.post('/configlet/addConfiglet.do', data=body,
                       timeout=self.request_timeout)

        # Get the key for the configlet
        data = self.clnt.get('/configlet/getConfigletByName.do?name=%s'
                             % qplus(name), timeout=self.request_timeout)
        return data['key']

    def delete_configlet(self, name, key):
        ''' Delete the configlet.

            Args:
                name (str): Configlet name
                key (str): Configlet key
        '''
        self.log.debug('delete_configlet: name: %s key: %s' % (name, key))
        body = [{'name': name, 'key': key}]
        # Delete the configlet
        self.clnt.post('/configlet/deleteConfiglet.do', data=body,
                       timeout=self.request_timeout)

    def update_configlet(self, config, key, name, wait_task_ids=False):
        ''' Update a configlet.

            Args:
                config (str): Switch config statements
                key (str): Configlet key
                name (str): Configlet name
                wait_task_ids (boolean): Wait for task IDs to generate

            Returns:
                data (dict): Contains success or failure message
        '''
        self.log.debug('update_configlet: config: %s key: %s name: %s' %
                       (config, key, name))

        # Update the configlet
        body = {'config': config, 'key': key, 'name': name,
                'waitForTaskIds': wait_task_ids}
        return self.clnt.post('/configlet/updateConfiglet.do', data=body,
                              timeout=self.request_timeout)

    def add_note_to_configlet(self, key, note):
        ''' Add a note to a configlet.

            Args:
                key (str): Configlet key
                note (str): Note to be added to configlet.
        '''
        data = {
            'key': key,
            'note': note,
        }
        return self.clnt.post('/configlet/addNoteToConfiglet.do',
                              data=data, timeout=self.request_timeout)

    def validate_config(self, device_mac, config):
        ''' Validate a config against a device

            Args:
                device_mac (str): Device MAC address
                config (str): Switch config statements

            Returns:
                response (dict): A dict that contains the result of the
                    validation operation
        '''
        self.log.debug('validate_config: name: %s config: %s'
                       % (device_mac, config))
        body = {'netElementId': device_mac, 'config': config}
        # Invoke the validate API call
        result = self.clnt.post('/configlet/validateConfig.do', data=body,
                                timeout=self.request_timeout)
        validated = True
        if 'warningCount' in result and result['warnings']:
            for warning in result['warnings']:
                self.log.warning('Validation of config produced warning - %s'
                                 % warning)
        if 'errorCount' in result:
            self.log.error('Validation of config produced %s errors'
                           % result['errorCount'])
            if 'errors' in result:
                for error in result['errors']:
                    self.log.error('Validation of config produced error - %s'
                                   % error)
            validated = False
        if 'result' in result:
            for item in result['result']:
                if 'messages' in item:
                    for message in item['messages']:
                        self.log.info('Validation of config returned'
                                      ' message - %s' % message)
        return validated

    def get_all_temp_actions(self, start=0, end=0):
        ''' Returns a list of existing temp actions.

            Args:
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.

            Returns:
                response (dict): A dict that contains a list of the current
                    temp actions.
        '''
        url = ('/provisioning/getAllTempActions.do?startIndex=%d&endIndex=%d'
               % (start, end))
        data = self.clnt.get(url, timeout=self.request_timeout)

        return data

    def _add_temp_action(self, data):
        ''' Adds temp action that requires a saveTopology call to take effect.

            Args:
                data (dict): a data dict with a specific format for the
                    desired action.

                    Base Ex: data = {'data': [{specific key/value pairs}]}
        '''
        url = ('/provisioning/addTempAction.do?'
               'format=topology&queryParam=&nodeId=root')
        self.clnt.post(url, data=data, timeout=self.request_timeout)

    def _save_topology_v2(self, data):
        ''' Confirms a previously created temp action.

            Args:
                data (list): a list that contains a dict with a specific
                    format for the desired action. Our primary use case is for
                    confirming existing temp actions so we most often send an
                    empty list to confirm an existing temp action.

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': []}}
        '''
        url = '/provisioning/v2/saveTopology.do'
        return self.clnt.post(url, data=data, timeout=self.request_timeout)

    def apply_configlets_to_device(self, app_name, dev, new_configlets=None, create_task=True):
        ''' Apply the configlets to the device.

            Args:
                app_name (str): The application name to use in info field.
                dev (dict): The switch device dict
                new_configlets (list): List of configlet name and key pairs
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        self.log.debug('apply_configlets_to_device: dev: %s names: %s' %
                       (dev, new_configlets))
        # Get all the configlets assigned to the device.
        configlets = self.get_configlets_by_device_id(dev['systemMacAddress'])

        # Get a list of the names and keys of the configlets
        cnames = []
        ckeys = []
        for configlet in configlets:
            cnames.append(configlet['name'])
            ckeys.append(configlet['key'])

        # Add the new configlets to the end of the arrays
        # Issue #10 - move device to container without new configlet.
        if new_configlets is not None:
            for entry in new_configlets:
                cnames.append(entry['name'])
                ckeys.append(entry['key'])

        info = '%s: Configlet Assign: to Device %s' % (app_name, dev['fqdn'])
        info_preview = '<b>Configlet Assign:</b> to Device' + dev['fqdn']
        data = {'data': [{'info': info,
                          'infoPreview': info_preview,
                          'note': '',
                          'action': 'associate',
                          'nodeType': 'configlet',
                          'nodeId': '',
                          'configletList': ckeys,
                          'configletNamesList': cnames,
                          'ignoreConfigletNamesList': [],
                          'ignoreConfigletList': [],
                          'configletBuilderList': [],
                          'configletBuilderNamesList': [],
                          'ignoreConfigletBuilderList': [],
                          'ignoreConfigletBuilderNamesList': [],
                          'toId': dev['systemMacAddress'],
                          'toIdType': 'netelement',
                          'fromId': '',
                          'nodeName': '',
                          'fromName': '',
                          'toName': dev['fqdn'],
                          'nodeIpAddress': dev['ipAddress'],
                          'nodeTargetIpAddress': dev['ipAddress'],
                          'childTasks': [],
                          'parentTask': ''}]}
        self.log.debug('apply_configlets_to_device: saveTopology data:\n%s' %
                       data['data'])
        self._add_temp_action(data)
        if create_task:
            return self._save_topology_v2([])
        else:
            return data

    def apply_configlets_to_container(self, app_name, container, new_configlets, create_task=True):
        ''' Apply the configlets to the container.

            Args:
                app_name (str): The application name to use in info field.
                container (dict): The container dict
                new_configlets (list): List of configlet name and key pairs
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        self.log.debug('apply_configlets_to_container: container: %s names: %s' %
                       (container, new_configlets))
        # Get all the configlets assigned to the device.
        configlets = self.get_configlets_by_container_id(container['key'])

        # Get a list of the names and keys of the configlets
        # Static Configlets
        cnames = []
        ckeys = []
        # ConfigletBuilder Configlets
        bnames = []
        bkeys = []
        if len(configlets['configletList']) > 0:
            for configlet in configlets['configletList']:
                if configlet['type'] == 'Static':
                    cnames.append(configlet['name'])
                    ckeys.append(configlet['key'])
                elif configlet['type'] == 'Builder':
                    bnames.append(configlet['name'])
                    bkeys.append(configlet['key'])

        # Add the new configlets to the end of the arrays
        for entry in new_configlets:
            cnames.append(entry['name'])
            ckeys.append(entry['key'])

        info = '%s: Configlet Assign: to Container %s' % (app_name, container['name'])
        info_preview = '<b>Configlet Assign:</b> to Container' + container['name']
        data = {'data': [{'info': info,
                          'infoPreview': info_preview,
                          'note': '',
                          'action': 'associate',
                          'nodeType': 'configlet',
                          'nodeId': '',
                          'configletList': ckeys,
                          'configletNamesList': cnames,
                          'ignoreConfigletNamesList': [],
                          'ignoreConfigletList': [],
                          'configletBuilderList': bkeys,
                          'configletBuilderNamesList': bnames,
                          'ignoreConfigletBuilderList': [],
                          'ignoreConfigletBuilderNamesList': [],
                          'toId': container['key'],
                          'toIdType': 'container',
                          'fromId': '',
                          'nodeName': '',
                          'fromName': '',
                          'toName': container['name'],
                          'nodeIpAddress': '',
                          'nodeTargetIpAddress': '',
                          'childTasks': [],
                          'parentTask': ''}]}
        self.log.debug('apply_configlets_to_container: saveTopology data:\n%s' %
                       data['data'])
        self._add_temp_action(data)
        if create_task:
            return self._save_topology_v2([])
        else:
            return data

    # pylint: disable=too-many-locals
    def remove_configlets_from_device(self, app_name, dev, del_configlets, create_task=True):
        ''' Remove the configlets from the device.

            Args:
                app_name (str): The application name to use in info field.
                dev (dict): The switch device dict
                del_configlets (list): List of configlet name and key pairs
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'35']}}
        '''
        self.log.debug('remove_configlets_from_device: dev: %s names: %s' %
                       (dev, del_configlets))

        # Get all the configlets assigned to the device.
        configlets = self.get_configlets_by_device_id(dev['systemMacAddress'])

        # Get a list of the names and keys of the configlets.  Do not add
        # configlets that are on the delete list.
        keep_names = []
        keep_keys = []
        for configlet in configlets:
            key = configlet['key']
            if next((ent for ent in del_configlets if ent['key'] == key),
                    None) is None:
                keep_names.append(configlet['name'])
                keep_keys.append(key)

        # Remove the names and keys of the configlets to keep and build a
        # list of the configlets to remove.
        del_names = []
        del_keys = []
        for entry in del_configlets:
            del_names.append(entry['name'])
            del_keys.append(entry['key'])

        info = '%s Configlet Remove: from Device %s' % (app_name, dev['fqdn'])
        info_preview = '<b>Configlet Remove:</b> from Device' + dev['fqdn']
        data = {'data': [{'info': info,
                          'infoPreview': info_preview,
                          'note': '',
                          'action': 'associate',
                          'nodeType': 'configlet',
                          'nodeId': '',
                          'configletList': keep_keys,
                          'configletNamesList': keep_names,
                          'ignoreConfigletNamesList': del_names,
                          'ignoreConfigletList': del_keys,
                          'configletBuilderList': [],
                          'configletBuilderNamesList': [],
                          'ignoreConfigletBuilderList': [],
                          'ignoreConfigletBuilderNamesList': [],
                          'toId': dev['systemMacAddress'],
                          'toIdType': 'netelement',
                          'fromId': '',
                          'nodeName': '',
                          'fromName': '',
                          'toName': dev['fqdn'],
                          'nodeIpAddress': dev['ipAddress'],
                          'nodeTargetIpAddress': dev['ipAddress'],
                          'childTasks': [],
                          'parentTask': ''}]}
        self.log.debug('remove_configlets_from_device: saveTopology data:\n%s'
                       % data['data'])
        self._add_temp_action(data)
        if create_task:
            return self._save_topology_v2([])
        else:
            return data

    # pylint: disable=too-many-locals
    def remove_configlets_from_container(self, app_name, container, del_configlets, create_task=True):
        ''' Remove the configlets from the container.

            Args:
                app_name (str): The application name to use in info field.
                container (dict): The container dict
                del_configlets (list): List of configlet name and key pairs
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'35']}}
        '''
        self.log.debug('remove_configlets_from_container: container: %s names: %s' %
                       (container, del_configlets))

        # Get all the configlets assigned to the device.
        configlets = self.get_configlets_by_container_id(container['key'])

        # Get a list of the names and keys of the configlets.  Do not add
        # configlets that are on the delete list.
        keep_names = []
        keep_keys = []
        for configlet in configlets['configletList']:
            key = configlet['key']
            if next((ent for ent in del_configlets if ent['key'] == key),
                    None) is None:
                keep_names.append(configlet['name'])
                keep_keys.append(key)

        # Remove the names and keys of the configlets to keep and build a
        # list of the configlets to remove.
        del_names = []
        del_keys = []
        for entry in del_configlets:
            del_names.append(entry['name'])
            del_keys.append(entry['key'])

        info = '%s Configlet Remove: from Container %s' % (app_name, container['name'])
        info_preview = '<b>Configlet Remove:</b> from Container' + container['name']
        data = {'data': [{'info': info,
                          'infoPreview': info_preview,
                          'note': '',
                          'action': 'associate',
                          'nodeType': 'configlet',
                          'nodeId': '',
                          'configletList': keep_keys,
                          'configletNamesList': keep_names,
                          'ignoreConfigletNamesList': del_names,
                          'ignoreConfigletList': del_keys,
                          'configletBuilderList': [],
                          'configletBuilderNamesList': [],
                          'ignoreConfigletBuilderList': [],
                          'ignoreConfigletBuilderNamesList': [],
                          'toId': container['key'],
                          'toIdType': 'container',
                          'fromId': '',
                          'nodeName': '',
                          'fromName': '',
                          'toName': container['name'],
                          'nodeIpAddress': '',
                          'nodeTargetIpAddress': '',
                          'childTasks': [],
                          'parentTask': ''}]}
        self.log.debug('remove_configlets_from_container: saveTopology data:\n%s'
                       % data['data'])
        self._add_temp_action(data)
        if create_task:
            return self._save_topology_v2([])
        else:
            return data

    def get_applied_devices(self, configlet_name, start=0, end=0):
        ''' Returns a list of devices to which the named configlet is applied.

            Args:
                configlet_name (str): The name of the configlet to be queried.
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
        '''
        return self.clnt.get('/configlet/getAppliedDevices.do?'
                             'configletName=%s&startIndex=%d&endIndex=%d'
                             % (configlet_name, start, end),
                             timeout=self.request_timeout)

    def get_applied_containers(self, configlet_name, start=0, end=0):
        ''' Returns a list of containers to which the named
            configlet is applied.

            Args:
                configlet_name (str): The name of the configlet to be queried.
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
        '''
        return self.clnt.get('/configlet/getAppliedContainers.do?'
                             'configletName=%s&startIndex=%d&endIndex=%d'
                             % (configlet_name, start, end),
                             timeout=self.request_timeout)

    # pylint: disable=too-many-arguments
    def _container_op(self, container_name, container_key, parent_name,
                      parent_key, operation):
        ''' Perform the operation on the container.

            Args:
                container_name (str): Container name
                container_key (str): Container key, can be empty for add.
                parent_name (str): Parent container name
                parent_key (str): Parent container key
                operation (str): Container operation 'add' or 'delete'.

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': []}}
        '''
        msg = ('%s container %s under container %s' %
               (operation, container_name, parent_name))
        data = {'data': [{'info': msg,
                          'infoPreview': msg,
                          'action': operation,
                          'nodeType': 'container',
                          'nodeId': container_key,
                          'toId': '',
                          'fromId': '',
                          'nodeName': container_name,
                          'fromName': '',
                          'toName': '',
                          'childTasks': [],
                          'parentTask': '',
                          'toIdType': 'container'}]}
        if operation is 'add':
            data['data'][0]['toId'] = parent_key
            data['data'][0]['toName'] = parent_name
        elif operation is 'delete':
            data['data'][0]['fromId'] = parent_key
            data['data'][0]['fromName'] = parent_name

        # Perform the container operation
        self._add_temp_action(data)
        return self._save_topology_v2([])

    def add_container(self, container_name, parent_name, parent_key):
        ''' Add the container to the specified parent.

            Args:
                container_name (str): Container name
                parent_name (str): Parent container name
                parent_key (str): Parent container key

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': []}}
        '''
        self.log.debug('add_container: container: %s parent: %s parent_key: %s'
                       % (container_name, parent_name, parent_key))
        return self._container_op(container_name, 'new_container', parent_name,
                                  parent_key, 'add')

    def delete_container(self, container_name, container_key, parent_name,
                         parent_key):
        ''' Add the container to the specified parent.

            Args:
                container_name (str): Container name
                container_key (str): Container key
                parent_name (str): Parent container name
                parent_key (str): Parent container key

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': []}}
        '''
        self.log.debug('delete_container: container: %s container_key: %s '
                       'parent: %s parent_key: %s' %
                       (container_name, container_key, parent_name,
                        parent_key))
        return self._container_op(container_name, container_key, parent_name,
                                  parent_key, 'delete')

    def get_parent_container_for_device(self, device_mac):
        ''' Add the container to the specified parent.

            Args:
                device_mac (str): Device mac address

            Returns:
                response (dict): A dict that contains the parent container info
        '''
        self.log.debug('get_parent_container_for_device: called for %s'
                       % device_mac)
        data = self.clnt.get('/provisioning/searchTopology.do?'
                             'queryParam=%s&startIndex=0&endIndex=0'
                             % device_mac, timeout=self.request_timeout)
        if data['total'] > 0:
            cont_name = data['netElementContainerList'][0]['containerName']
            return self.get_container_by_name(cont_name)
        return None

    def move_device_to_container(self, app_name, device, container,
                                 create_task=True):
        ''' Add the container to the specified parent.

            Args:
                app_name (str): String to specify info/signifier of calling app
                device (dict): Device info
                container (dict): Container info
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': []}}
        '''
        info = '%s moving device %s to container %s' % (app_name,
                                                        device['fqdn'],
                                                        container['name'])
        self.log.debug('Attempting to move device %s to container %s'
                       % (device['fqdn'], container['name']))
        if 'parentContainerId' in device:
            from_id = device['parentContainerId']
        else:
            parent_cont = self.get_parent_container_for_device(device['key'])
            from_id = parent_cont['key']
        data = {'data': [{'info': info,
                          'infoPreview': info,
                          'action': 'update',
                          'nodeType': 'netelement',
                          'nodeId': device['key'],
                          'toId': container['key'],
                          'fromId': from_id,
                          'nodeName': device['fqdn'],
                          'toName': container['name'],
                          'toIdType': 'container',
                          'childTasks': [],
                          'parentTask': ''}]}
        try:
            self._add_temp_action(data)
        # pylint: disable=invalid-name
        except CvpApiError as e:
            if 'Data already exists' in str(e):
                self.log.debug('Device %s already in container %s'
                               % (device['fqdn'], container))
        if create_task:
            resp = self._save_topology_v2([])
            return resp

    def search_topology(self, query, start=0, end=0):
        ''' Search the topology for items matching the query parameter.

            Args:
                query (str): Query parameter which is the name of the container
                    or device.
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                response (dict): A dict that contains the container and
                    netelement lists.
        '''
        self.log.debug('search_topology: query: %s start: %d end: %d' %
                       (query, start, end))
        data = self.clnt.get('/provisioning/searchTopology.do?queryParam=%s&'
                             'startIndex=%d&endIndex=%d'
                             % (qplus(query), start, end),
                             timeout=self.request_timeout)
        return data

    def filter_topology(self, node_id='root', fmt='topology',
                        start=0, end=0):
        ''' Filter the CVP topology for container and device information.

            Args:
                node_id (str): The container key to base the filter in.
                    Default is 'root', for the Tenant container.
                fmt (str): The type of filter to return. Must be either
                    'topology' or 'list'. Default is 'topology'.
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
        '''
        url = ('/provisioning/filterTopology.do?nodeId=%s&'
               'format=%s&startIndex=%d&endIndex=%d'
               % (node_id, fmt, start, end))
        return self.clnt.get(url, timeout=self.request_timeout)

    def check_compliance(self, node_key, node_type):
        ''' Check that a device is in compliance, that is the configlets
            applied to the device match the devices running configuration.

            Args:
                node_key (str): The device key.
                node_type (str): The device type.

            Returns:
                response (dict): A dict that contains the results of the
                    compliance check.
        '''
        self.log.debug('check_compliance: node_key: %s node_type: %s' %
                       (node_key, node_type))
        data = {'nodeId': node_key, 'nodeType': node_type}
        resp = self.clnt.post('/provisioning/checkCompliance.do', data=data,
                              timeout=self.request_timeout)
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v2':
            if resp['complianceIndication'] == u'':
                resp['complianceIndication'] = 'NONE'
        return resp

    def get_event_by_id(self, e_id):
        ''' Return information on the requested event ID.

            Args:
                e_id (str): The event id to be queried.
        '''
        return self.clnt.get('/event/getEventById.do?eventId=%s' % e_id,
                             timeout=self.request_timeout)

    def get_default_snapshot_template(self):
        ''' Return the default snapshot template.

        '''
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            url = ('/snapshot/getDefaultSnapshotTemplate.do?'
                   'startIndex=0&endIndex=0')
            return self.clnt.get(url, timeout=self.request_timeout)
        else:
            self.log.debug('v2 Inventory API Call')
            self.log.debug('API getDefaultSnapshotTemplate.do'
                           ' deprecated for CVP 2018.2 and beyond')
            return None

    # pylint: disable=invalid-name
    def capture_container_level_snapshot(self, template_key, container_key):
        ''' Initialize a container level snapshot event.

            Args:
                template_key (str): The snapshot template key to be used for
                    the snapshots.
                container_key (str): The container key to start the
                    snapshots on.
        '''
        if self.clnt.apiversion is None:
            self.get_cvp_info()
        if self.clnt.apiversion == 'v1':
            self.log.debug('v1 Inventory API Call')
            data = {
                'templateId': template_key,
                'containerId': container_key,
            }
            return self.clnt.post('/snapshot/captureContainerLevelSnapshot.do',
                                  data=data, timeout=self.request_timeout)
        else:
            self.log.debug('v2 Inventory API Call')
            self.log.debug('API captureContainerLevelSnapshot.do'
                           ' deprecated for CVP 2018.2 and beyond')
            return None

    def add_image(self, filepath):
        ''' Add an image to a CVP cluster.

            Args:
                filepath (str): Local path to the image to upload.

            Returns:
                data (dict): Dictionary of image add data.
        '''
        # Get the absolute file path to be uploaded
        image_path = os.path.abspath(filepath)
        image_data = open(image_path, 'rb')
        response = self.clnt.post('/image/addImage.do',
                                  files={'file': image_data})
        return response

    def cancel_image(self, image_name):
        ''' Discard/cancel the uploaded image/image bundle before save.

            Args:
                image_name (string): Name of image to cancel/discard.

            Returns:
                data (dict): Success or error message.
        '''
        image_data = {'data': image_name}
        return self.clnt.post('/image/cancelImages.do', data=image_data,
                              timeout=self.request_timeout)

    def get_images(self, start=0, end=0):
        ''' Return a list of all images.

            Args:
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                images (dict): The 'total' key contains the number of images,
                    the 'data' key contains a list of images and their info.
        '''
        self.log.debug('Get info about images')
        return self.clnt.get('/image/getImages.do?queryparam=&startIndex=%d&'
                             'endIndex=%d' % (start, end),
                             timeout=self.request_timeout)

    def get_image_bundles(self, start=0, end=0):
        ''' Return a list of all image bundles.

            Args:
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                image bundles (dict): The 'total' key contains the number of
                    image bundles, the 'data' key contains a list of image
                    bundles and their info.
        '''
        self.log.debug('Get image bundles that can be applied to devices or'
                       ' containers')
        return self.clnt.get('/image/getImageBundles.do?queryparam=&'
                             'startIndex=%d&endIndex=%d' % (start, end),
                             timeout=self.request_timeout)

    def get_image_bundle_by_name(self, name):
        ''' Return a dict of info about an image bundle.

            Args:
                name (str): Name of image bundle to return info about.

            Returns:
                image bundle (dict): Dict of info specific to the image bundle
                    requested or None if the name requested doesn't exist.
        '''
        self.log.debug('Attempt to get image bundle %s' % name)
        try:
            image = self.clnt.get('/image/getImageBundleByName.do?name=%s'
                                  % qplus(name), timeout=self.request_timeout)
        except CvpApiError as error:
            # Catch an invalid task_id error and return None
            if 'Entity does not exist' in str(error):
                self.log.debug('Bundle with name %s does not exist' % name)
                return None
            raise error
        return image

    def delete_image_bundle(self, image_key, image_name):
        ''' Delete image bundle

            Args:
                image_key (str): The key of the image bundle to be deleted.
                image_name (str): The name of the image bundle to be deleted.
        '''
        bundle_data = {
            'data': [{'key': image_key,
                      'name': image_name}]
        }
        return self.clnt.post('/image/deleteImageBundles.do', data=bundle_data,
                              timeout=self.request_timeout)

    def save_image_bundle(self, name, images, certified=True):
        ''' Save an image bundle to a cluster.

            Args:
                name (str): The name of the image bundle to be saved.
                images (list): A list of image names to include in the bundle.
                certified (bool): Whether the image bundle is certified or
                    not. Default is True.
        '''
        certified_image = 'true' if certified else 'false'
        data = {
            'name': name,
            'isCertifiedImage': certified_image,
            'images': images,
        }
        return self.clnt.post('/image/saveImageBundle.do', data=data,
                              timeout=self.request_timeout)

    def update_image_bundle(self, bundle_id, name, images, certified=True):
        ''' Update an existing image bundle
        '''
        certified_image = 'true' if certified else 'false'
        data = {
            'id': bundle_id,
            'name': name,
            'isCertifiedImage': certified_image,
            'images': images,
        }
        return self.clnt.post('/image/updateImageBundle.do', data=data,
                              timeout=self.request_timeout)

    def apply_image_to_device(self, image, device, create_task=True):
        ''' Apply an image bundle to a device

            Args:
                image (dict): The image info.
                device (dict): Info about device to apply image to.
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any). Image updates will not run until
                    task or tasks are executed.

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        return self.apply_image_to_element(image, device, device['fqdn'],
                                           'netelement', create_task)

    def apply_image_to_container(self, image, container, create_task=True):
        ''' Apply an image bundle to a container

            Args:
                image (dict): The image info.
                container (dict): Info about container to apply image to.
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any). Image updates will not run until
                    task or tasks are executed.

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        return self.apply_image_to_element(image, container, container['name'],
                                           'container', create_task)

    def apply_image_to_element(self, image, element, name, id_type,
                               create_task=True):
        ''' Apply an image bundle to a device or container.

            Args:
                image (dict): The image info.
                element (dict): Info about element to apply image to. Dict
                    can contain device info or container info.
                name (str): Name of element image is being applied to.
                id_type (str): Id type of element image is being applied to.
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any). Image updates will not run until
                    task or tasks are executed.

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        self.log.debug('Attempt to apply %s to %s %s' % (image['name'],
                                                         id_type, name))
        info = 'Apply image: %s to %s %s' % (image['name'], id_type, name)
        data = {'data': [{'info': info,
                          'infoPreview': info,
                          'note': '',
                          'action': 'associate',
                          'nodeType': 'imagebundle',
                          'nodeId': image['id'],
                          'toId': element['key'],
                          'toIdType': id_type,
                          'fromId': '',
                          'nodeName': image['name'],
                          'fromName': '',
                          'toName': name,
                          'childTasks': [],
                          'parentTask': ''}]}
        self._add_temp_action(data)
        if create_task:
            return self._save_topology_v2([])

    def remove_image_from_device(self, image, device):
        ''' Remove the image bundle from the specified device.

            Args:
                image (dict): The image info.
                device (dict): The device info.

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        return self.remove_image_from_element(image, device, device['fqdn'],
                                              'netelement')

    def remove_image_from_container(self, image, container):
        ''' Remove the image bundle from the specified container.

            Args:
                image (dict): The image info.
                container (dict): The container info.

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        return self.remove_image_from_element(image, container,
                                              container['name'], 'container')

    def remove_image_from_element(self, image, element, name, id_type):
        ''' Remove the image bundle from the specified container.

            Args:
                image (dict): The image info.
                element (dict): The container info.
                name (): name.
                id_type (): type.

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        self.log.debug('Attempt to remove %s from %s' % (image['name'], name))
        info = 'Remove image: %s from %s' % (image['name'], name)
        data = {'data': [{'info': info,
                          'infoPreview': info,
                          'note': '',
                          'action': 'associate',
                          'nodeType': 'imagebundle',
                          'nodeId': '',
                          'toId': element['key'],
                          'toIdType': id_type,
                          'fromId': '',
                          'nodeName': '',
                          'fromName': '',
                          'toName': name,
                          'ignoreNodeId': image['id'],
                          'ignoreNodeName': image['name'],
                          'childTasks': [],
                          'parentTask': ''}]}
        self._add_temp_action(data)
        return self._save_topology_v2([])

    def get_change_controls(self, query='', start=0, end=0):
        ''' Returns a list of change controls.

            Args:
                query (str): Query to look for in change control names
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                change controls (list): The list of change controls
        '''
        self.log.debug('get_change_controls: query: %s' % query)
        data = self.clnt.get(
            '/changeControl/getChangeControls.do?searchText=%s&startIndex=%d'
            '&endIndex=%d' % (qplus(query), start, end),
            timeout=self.request_timeout)
        if 'data' not in data:
            return None
        return data['data']

    def change_control_available_tasks(self, query='', start=0, end=0):
        ''' Returns a list of tasks that are available for a change control.

            Args:
                query (str): Query to look for in task
                start (int): Start index for the pagination.  Default is 0.
                end (int): End index for the pagination.  If end index is 0
                    then all the records will be returned.  Default is 0.

            Returns:
                tasks (list): The list of available tasks
        '''
        self.log.debug('change_control_available_tasks: query: %s' % query)
        data = self.clnt.get(
            '/changeControl/getTasksByStatus.do?searchText=%s&startIndex=%d'
            '&endIndex=%d' % (qplus(query), start, end),
            timeout=self.request_timeout)
        if 'data' not in data:
            return None
        return data['data']

    def create_change_control(self, name, change_control_tasks, timezone,
                              country_id, date_time, snapshot_template_key='',
                              change_control_type='Custom',
                              stop_on_error='false'):
        ''' Create change control with provided information and return
            change control ID.

            Args:
                name (string): The name for the new change control.
                change_control_tasks (list): A list of key value pairs where
                    the key is the Task ID and the value is the task order
                    as an integer.
                    Ex: [{'taskId': '100', 'taskOrder': 1},
                         {'taskId': '101', 'taskOrder': 1},
                         {'taskId': '102', 'taskOrder': 2}]
                timezone (string): The timezone as a string.
                    Ex: "America/New_York"
                country_id (string): The country ID.
                    Ex: "United States"
                date_time (string): The date and time for execution.
                    Time is military time format.
                    Ex: "2018-08-22 11:30"
                snapshot_template_key (string): ???
                change_control_type (string): The type of change control being
                    created. Options are "Custom" or "Rollback".
                stop_on_error (string): String representation of a boolean
                    to set whether this change control will stop if an error is
                    encountered in one of its tasks.

            Returns:
                response (dict): A dict that contains...

                Ex: {"data": "success", "ccId": "4"}
        '''
        self.log.debug('create_change_control')
        # {
        #  "timeZone": "America/New_York",
        #  "countryId": "United States",
        #  "dateTime": "2018-08-22 11:30",
        #  "ccName": "test2",
        #  "snapshotTemplateKey": "",
        #  "type": "Custom",
        #  "stopOnError": "false",
        #  "deletedTaskIds": [],
        #  "changeControlTasks": [
        #    {
        #      "taskId": "126",
        #      "taskOrder": 1,
        #      "snapshotTemplateKey": "",
        #      "clonedCcId": ""
        #    }
        #  ]
        # }
        task_data_list = []
        for taskinfo in change_control_tasks:
            task_list_entry = {'taskId': taskinfo['taskId'],
                               'taskOrder': taskinfo['taskOrder'],
                               'snapshotTemplateKey': '',
                               'clonedCcId': ''}
            task_data_list.append(task_list_entry)
        data = {'timeZone': timezone,
                'countryId': country_id,
                'dateTime': date_time,
                'ccName': name,
                'snapshotTemplateKey': snapshot_template_key,
                'type': change_control_type,
                'stopOnError': stop_on_error,
                'deletedTaskIds': [],
                'changeControlTasks': task_data_list}
        return self.clnt.post('/changeControl/addOrUpdateChangeControl.do',
                              data=data, timeout=self.request_timeout)

    def add_notes_to_change_control(self, cc_id, notes):
        ''' Add provided notes to the specified change control.

            Args:
                cc_id (string): The id for the change control to add notes to.
                notes (string): The notes to add to the change control.

            Returns:
                response (dict): A dict that contains...

                Ex: {"data": "success"}
        '''
        self.log.debug('add_notes_to_change_control: cc_id %s, notes %s'
                       % (cc_id, notes))
        data = {'ccId': cc_id,
                'notes': notes}
        return self.clnt.post('/changeControl/addNotesToChangeControl.do',
                              data=data, timeout=self.request_timeout)

    def execute_change_controls(self, cc_ids):
        ''' Execute the change control indicated by its ccId.

            Args:
                cc_ids (list): A list of change control IDs to be executed.
        '''
        cc_id_list = [{'ccId': x} for x in cc_ids]
        data = {'ccIds': cc_id_list}
        self.clnt.post('/changeControl/executeCC.do', data=data,
                       timeout=self.request_timeout)

    def get_change_control_info(self, cc_id):
        ''' Get the detailed information for a single change control.

            Args:
                cc_id (string): The id for the change control to be retrieved.

            Returns:
                response (dict): A dict that contains...

                Ex: {'ccId': '4',
                     'ccName': 'test_api_1541106830',
                     'changeControlTasks': {'data': [<task data>],
                                             'total': 1},
                     'classId': 68,
                     'containerName': '',
                     'countryId': '',
                     'createdBy': 'cvpadmin',
                     'createdTimestamp': 1541106831629,
                     'dateTime': '',
                     'deviceCount': 1,
                     'executedBy': 'cvpadmin',
                     'executedTimestamp': 1541106831927,
                     'factoryId': 1,
                     'id': 68,
                     'key': '4',
                     'notes': '',
                     'postSnapshotEndTime': 0,
                     'postSnapshotStartTime': 0,
                     'preSnapshotEndTime': 0,
                     'preSnapshotStartTime': 0,
                     'progressStatus': {<status>},
                     'scheduledBy': '',
                     'scheduledByPassword': '',
                     'scheduledTimestamp': 0,
                     'snapshotTemplateKey': '',
                     'snapshotTemplateName': None,
                     'status': 'Inprogress',
                     'stopOnError': False,
                     'taskCount': 1,
                     'taskEndTime': 0,
                     'taskStartTime': 0,
                     'timeZone': '',
                     'type': 'Custom'}
        '''
        return self.clnt.get('/changeControl/getChangeControlInformation.do?'
                             'startIndex=0&endIndex=0&ccId=%s' % cc_id,
                             timeout=self.request_timeout)

    def deploy_device(self, device, container, configlets=None, image=None,
                      create_task=True):
        ''' Move a device from the undefined container to a target container.
            Optionally apply device-specific configlets and an image.

            Args:
                device (dict): unique key for the device
                container (str): name of container to move device to
                configlets (list): list of dicts with configlet key/name pairs
                image (str): name of image to apply to device
                create_task (boolean): Create task for this deploy device
                    sequence.

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': [u'32']}}
        '''
        info = 'Deploy device %s to container %s' % (device['fqdn'], container)
        self.log.debug(info)
        container_info = self.get_container_by_name(container)
        # Add action for moving device to specified container
        self.move_device_to_container('Deploy device', device, container_info,
                                      create_task=False)
        # Get proposed configlets device will inherit from container it is
        # being moved to.
        prop_conf = self.clnt.get('/provisioning/getTempConfigsByNetElementId.do?netElementId=%s' % device['key'])  # noqa E501
        new_configlets = prop_conf['proposedConfiglets']
        if configlets:
            new_configlets.extend(configlets)
        self.apply_configlets_to_device(app_name='deploy_device', dev=device,
                                        new_configlets=new_configlets, create_task=False)
        # Apply image to the device
        if image:
            image_info = self.get_image_bundle_by_name(image)
            self.apply_image_to_device(image_info, device, create_task=False)
        if create_task:
            return self._save_topology_v2([])

# New modules to add to cvp_api

    def reset_device(self, app_name, device, create_task=True):
        ''' Reset device by moving it to the Undefined Container.

            Args:
                app_name (str): String to specify info/signifier of calling app
                device (dict): Device info
                container (dict): Container info
                create_task (bool): Determines whether or not to execute a save
                    and create the tasks (if any)

            Returns:
                response (dict): A dict that contains a status and a list of
                    task ids created (if any).

                    Ex: {u'data': {u'status': u'success', u'taskIds': []}}
        '''
        info = '%s Reseting device %s moving it to Undefined' % (app_name,
                                                        device['fqdn'])
        self.log.debug('Attempting to Reset device %s moving it to Undefined'
                       % (device['fqdn']))
        if 'parentContainerId' in device:
            from_id = device['parentContainerId']
        else:
            parent_cont = self.get_parent_container_for_device(device['key'])
            from_id = parent_cont['key']
        data = {'data': [{'info': info,
                          'infoPreview': info,
                          'action': 'reset',
                          'nodeType': 'netelement',
                          'nodeId': device['key'],
                          'toId': 'undefined_container',
                          'fromId': from_id,
                          'nodeName': device['fqdn'],
                          'toName': 'Undefined',
                          'toIdType': 'container',
                          'childTasks': [],
                          'parentTask': ''}]}
        try:
            self._add_temp_action(data)
        # pylint: disable=invalid-name
        except CvpApiError as e:
            if 'Data already exists' in str(e):
                self.log.debug('Device %s already in container Undefined'
                               %device['fqdn'])
        if create_task:
            resp = self._save_topology_v2([])
            return resp

    def get_device_reconcile_config(self, device_mac):
        ''' Returns the Reconcile configuration for the device provided.

            Args:
                device_mac (str): Mac address of the device to get the Reconciled
                    configuration for.

            Returns:
                reconciledConfig config (string): The string of configuration
                elements different from the running config.
        '''
        self.log.debug('get_device_reconcile_config: device_mac: %s' % device_mac)
        configlet_list = self.get_configlets_by_device_id(device_mac)
        configletKey_list = []
        for configlet in configlet_list:
            configletKey_list.append(configlet['key'])
        body = {'configIdList':configletKey_list, 'netElementId':device_mac, 'pageType':'viewConfig'}
        validate_compare = self.clnt.post('/provisioning/validateAndCompareConfiglets.do',
                             data=body,
                             timeout=self.request_timeout)
        reconcile_config = ''
        if 'reconciledConfig' in validate_compare:
            reconcile_config = validate_compare['reconciledConfig']
        return reconcile_config

    def get_net_element_info_by_device_id(self, d_id):
        ''' Return a dict of info about a device in CVP.

            Args:
                d_id (str): Device Id Key / System MAC.

            Returns:
                net element data (dict): Dict of info specific to the device
                    requested or None if the name requested doesn't exist.
        '''
        self.log.debug('Attempt to get net element data for %s' % d_id)
        try:
            element_info = self.clnt.get('/provisioning/getNetElementInfoById.do?netElementId=%s'
                                  % qplus(d_id), timeout=self.request_timeout)
        except CvpApiError as error:
            # Catch an invalid task_id error and return None
            if 'errorMessage' in str(error):
                self.log.debug('Device with id %s could not be found' % d_id)
                return None
            raise error
        return element_info
