#!/usr/bin/python
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

from __future__ import absolute_import, division, print_function
import os
__metaclass__ = type



EXAMPLES = r"""
---
---
- name: CVP Image Tests
  hosts: cv_server
  gather_facts: no
  vars:

  tasks:
    - name: "Gather CVP facts {{inventory_hostname}}"
      arista.cvp.cv_facts:
        facts:
          images
      register: cv_facts


    - name: "Print out facts from {{inventory_hostname}}"
      debug:
        msg: "{{cv_facts}}"



    - name: "Get CVP images {{inventory_hostname}}"
      arista.cvp.cv_image:
        mode: images
        cvp_facts: '{{cv_facts.ansible_facts}}'

      register: image_facts

    - name: "Print out images from {{inventory_hostname}}"
      debug:
        msg: "{{image_facts}}"



"""








# Required by Ansible and CVP
import re
import logging
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
import ansible_collections.arista.cvp.plugins.module_utils.tools_cv as tools_cv
import ansible_collections.arista.cvp.plugins.module_utils.tools as tools
import ansible_collections.arista.cvp.plugins.module_utils.schema_v1 as schema

MODULE_LOGGER = logging.getLogger('arista.cvp.cv_image')
MODULE_LOGGER.info('Start cv_image module execution')


def facts_images(module):
    """
    Extract Facts of all images from cv_facts.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    list:
        Facts of all images
    """
    if "cvp_facts" in module.params:
        if "images" in module.params["cvp_facts"]:
            return module.params["cvp_facts"]["images"]
    return []

def facts_bundles(module):
    """
    Extract Facts of all image bundles from cv_facts.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    list:
        Facts of all image bundles
    """
    if "cvp_facts" in module.params:
        if "imageBundles" in module.params["cvp_facts"]:
            return module.params["cvp_facts"]["imageBundles"]
    return []



def is_image_present(module):
    """
    Checks if a named image is present.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    Bool:
        True if present, False if not
    """
    if "cvp_facts" in module.params:
        if "images" in module.params["cvp_facts"]:
            for entry in module.params["cvp_facts"]["images"]:
                if entry["imageFileName"] == os.path.basename(module.params['image']):
                    return True
            
    return False


def does_bundle_exist(module):
    """
    Checks if a named bundle already exists

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    Bool:
        True if present, False if not
    """
    if "cvp_facts" in module.params:
        if "bundles" in module.params["cvp_facts"]:
            for entry in module.params["cvp_facts"]["bundles"]:
                if entry["name"] == module.params['bundle_name']:
                    return True
            
    return False


def get_bundle_key(module):
    """
    Gets the key for a given bundle

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    String:
        The string value equivelent to the bundle key,
        or None if not found
    """
    for entry in module.params["cvp_facts"]["bundles"]:
        if entry["name"] == module.params['bundle_name']:
           return entry["key"]

    return None


def build_image_list(module):
    """
    Builds a list of the image data structures, for a given list of image names.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    List:
        Returns a list of images, with complete data or None in the event of failure
    """
    image_list = list()
    image_data = None
    success = True
    
    for entry in module.params['image_list']:
        for image in module.params["cvp_facts"]["images"]:
            if image["imageFileName"] == entry:
                image_data = image
                
        if image_data is not None:
            image_list.append(image_data)
            image_data = None
        else:
            module.fail_json(msg="Specified image ({}) does not exist".format(entry) )
            success = False
    
    if success:
        return image_list
    else:
        return None
    
    
        
    


def module_action(module):
    """
    Method to call the other modules.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    dict:
       result with tasks and information.
    """
    changed = False
    data = dict()
    warnings = list()

    
    
    if module.params['mode'] == 'images':
        if module.params['action'] == "get":
            data = facts_images(module)
            return changed, data, warnings

        
        elif module.params['action'] == "add":
            if module.params['image'] and os.path.exists(module.params['image']):
                if is_image_present(module) is False:
                    MODULE_LOGGER.debug("Image not present. Trying to add.")
                    try:
                        module.params["cvp_facts"]["images"].append(module.client.api.add_image(module.params['image']))
                        MODULE_LOGGER.debug(data)
                        changed = True
                    except Exception as e:
                        module.fail_json( msg="%s" % str(e))
                else:
                    module.fail_json(msg="Same image name already exists on the system")
            else:
                module.fail_json(msg="Specified file ({}) does not exist".format(module.params['image']) )
        else:
            module.fail_json(msg="Deletion of images through API is not currently supported")


    # So we are dealing with bundles rather than images
    else:
        if module.params['action'] == "get":
            data = facts_bundles(module)
            return changed, data, warnings
        
        elif module.params['action'] == "add":
            # There are basically 2 actions - either we are adding a new bundle (save)
            # or changing an existing bundle (update)
            if does_bundle_exist(module):
                warnings.append('Note that when updating a bundle, all the images to be used in the bundle must be listed')
                key = get_bundle_key(module)
                images = build_image_list(module)
                if images is not None:
                    try:
                       response = module.client.api.update_image_bundle( key, module.params['bundle_name'], images )
                       changed = True
                       data = response['data']
                    except Exception as e:
                        module.fail_json( msg="%s" % str(e) )
                
                else:
                    module.fail_json(msg="Unable to update bundle - images not present on server")
                        
                return changed, data, warnings
                    

            else:
                images = build_image_list(module)
                if images is not None:
                    try:
                        response = module.client.api.save_image_bundle( module.params['bundle_name'], images )
                        changed = True
                        data = response['data']
                    except Exception as e:
                        module.fail_json( msg="%s" % str(e) )

                else:
                    module.fail_json(msg="Unable to create bundle - images not present on server")                    
                # create bundle
                
                return changed, data, warnings
            
        else:
            warnings.append('Note that deleting the image bundle does not delete the images')
            if does_bundle_exist(module):
                key = get_bundle_key(module)
                try:
                    response = module.client.api.delete_image_bundle(key,module.params['bundle_name'] )
                    changed = True
                    data = response['data']
                except Exception as e:
                        module.fail_json( msg="%s" % str(e) )
            else:
                module.fail_json(msg="Unable to delete bundle - not found")
            
    return changed, data, warnings


def main():
    """
    main entry point for module execution.
    """
    argument_spec = dict(
        cvp_facts=dict(type='dict', required=True),
        image=dict(type='str'),
        image_list=dict(type="list", elements='str'),
        bundle_name=dict(type='str'),
        mode=dict(default='images', type='str', choices=['images','bundles']),
        action=dict(default='get', type='str', choices=['get','add','remove']),
        filter=dict(type='str') )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    MODULE_LOGGER.info('starting module cv_image')
    if module.check_mode:
        MODULE_LOGGER.warning('! check_mode is enable')
        # module.exit_json(changed=True)

    if not tools.HAS_DIFFLIB:
        module.fail_json(msg='difflib required for this module')

    if not tools.HAS_HASHLIB:
        module.fail_json(msg='hashlib required for this module')

    if not tools_cv.HAS_CVPRAC:
        module.fail_json(
            msg='cvprac required for this module. Please install using pip install cvprac')

    if not schema.HAS_JSONSCHEMA:
        module.fail_json(
            msg="jsonschema is required. Please install using pip install jsonschema")



    result = dict( changed=False )
    # messages = dict(issues=False)
    # Connect to CVP instance
    if not module.check_mode:
        module.client = tools_cv.cv_connect(module)
        result['changed'], result['data'], warnings = module_action(module)

    # Pass module params to configlet_action to act on configlet
    #result = action_manager(module)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
