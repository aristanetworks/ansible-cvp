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

__metaclass__ = type












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
    dict:
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
    dict:
        Facts of all image bundles
    """
    if "cvp_facts" in module.params:
        if "imageBundles" in module.params["cvp_facts"]:
            return module.params["cvp_facts"]["imageBundles"]
    return []



def is_image_present(imageName, module):
    """
    Extract Facts of all devices from cv_facts.

    Parameters
    ----------
    module : AnsibleModule
        Ansible module.

    Returns
    -------
    dict:
        Facts of all devices
    """
    if "cvp_facts" in module.params:
        if "images" in module.params["cvp_facts"]:
            for entry in module.params["cvp_facts"]["images"]:
                if entry["imageFileName"] == imageName:
                    return True
            
    return False




def main():
    """
    main entry point for module execution.
    """
    argument_spec = dict(
        configlets=dict(type='dict', required=True),
        configlets_notes=dict(type='str', default='Managed by Ansible', required=False),
        cvp_facts=dict(type='dict', required=True),
        configlet_filter=dict(type='list', default='none', elements='str'),
        filter_mode=dict(type='str',
                         choices=['loose', 'strict'],
                         default='loose',
                         required=False),
        state=dict(type='str',
                   choices=['present', 'absent'],
                   default='present',
                   required=False))

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

    if not schema.validate_cv_inputs(user_json=module.params['configlets'], schema=schema.SCHEMA_CV_CONFIGLET):
        MODULE_LOGGER.error("Invalid configlet input : %s", str(module.params['configlets']))
        module.fail_json(
            msg='Configlet input data are not compliant with module.')

    result = dict(changed=False, data={})
    # messages = dict(issues=False)
    # Connect to CVP instance
    if not module.check_mode:
        module.client = tools_cv.cv_connect(module)

    # Pass module params to configlet_action to act on configlet
    #result = action_manager(module)

    module.exit_json(**result)


if __name__ == '__main__':
    main()