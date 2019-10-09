#
# Copyright (c) 2019, Arista Networks, Inc.
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
''' Class containing calls to CVP 2018.x.x RESTful API.
'''
import os
# This import is for proper file IO handling support for both Python 2 and 3
# pylint: disable=redefined-builtin
from io import open

from cvp_client_errors import CvpApiError

try:
    from urllib import quote_plus as qplus
except (AttributeError, ImportError):
    from urllib.parse import quote_plus as qplus


class CvpApi(object):
    ''' CvpApi class contains calls to CVP 2018.x.x RESTful API.  The RESTful API
        parameters are passed in as parameters to the method.  The results of
        the RESTful API call are converted from json to a dict and returned.
        Where needed minimal processing is performed on the results.
        Any method that does a cv_client get or post call could raise the
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
        return data

    # ~Device Related API Calls
    
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

    # ~Configlet Related API Calls

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

    def get_configlets(self, start=0, end=0):
        ''' Returns a list of all defined configlets.

            Args:
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
        '''
        self.log.debug('v2 Inventory API Call')
        # New API getConfiglets does not return the actual configlet config
        # Get the actual configlet config using getConfigletByName
        configlets = self.clnt.get('/configlet/getConfiglets.do?'
                           'startIndex=%d&endIndex=%d' % (start, end),
                           timeout=self.request_timeout)
        if 'data' in configlets:
            for configlet in configlets['data']:
                full_cfglt_data = self.get_configlet_by_name(
                    configlet['name'])
                configlet['config'] = full_cfglt_data['config']
        return configlets

    def get_devices_by_configlet(self, configlet_name, start=0, end=0):
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

    def get_containers_by_configlet(self, configlet_name, start=0, end=0):
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

    # ~Container Related API Calls

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
        self.log.debug('v2 Inventory API Call')
        containers = self.clnt.get('/inventory/containers')
        for container in containers:
            container['name'] = container['Name']
            container['key'] = container['Key']
            full_cont_info = self.get_container_by_id(
                container['Key'])
            if (full_cont_info is not None and
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
        containers = self.clnt.get('/provisioning/searchTopology.do?queryParam=%s'
                              '&startIndex=0&endIndex=0' % qplus(name))
        if containers['total'] > 0 and containers['containerList']:
            for container in containers['containerList']:
                if container['name'] == name:
                    return container

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

    def get_devices_by_container_id(self, key):
        ''' Returns a dict of the devices under the named container.

            Args:
                key (str): The containerId of the container to get devices from
        '''
        self.log.debug('get_devices_in_container: by Id')
        devices = []
        all_elements = self.clnt.get('/provisioning/getNetElementList.do?'
                                    'nodeId=%s&startIndex=0&endIndex=0&ignoreAdd=false'
                                     %key,timeout=self.request_timeout)
        for device in all_elements["netElementList"]:
            devices.append(device)
        return devices

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

    def get_image_bundle_by_container_id(self, c_id, start=0, end=0, scope='false'):
        ''' Returns a list of ImageBundles applied to the given container.

            Args:
                c_id (str): The container ID (key) to query.
                start (int): Start index for the pagination. Default is 0.
                end (int): End index for the pagination. If end index is 0
                    then all the records will be returned. Default is 0.
                scope (string) the session scope
        '''
        return self.clnt.get('/provisioning/getImageBundleByContainerId.do?'
                             'containerId=%s&startIndex=%d&endIndex=%d&sessionScope=%s'
                             % (c_id, start, end, scope),
                             timeout=self.request_timeout)
    
    # ~Image Related API Calls

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
    
    # ~Task Related API Calls

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
