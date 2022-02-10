#!/usr/bin/env python
# coding: utf-8 -*-
#
# GNU General Public License v3.0+
#
# Copyright 2021 Arista Networks AS-EMEA
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

import traceback
import logging
import os
from typing import List
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.arista.cvp.plugins.module_utils.logger   # noqa # pylint: disable=unused-import
from ansible_collections.arista.cvp.plugins.module_utils.response import CvApiResult, CvManagerResult, CvAnsibleResponse  # noqa # pylint: disable=unused-import
try:
    from cvprac.cvp_client import CvpClient  # noqa # pylint: disable=unused-import
    from cvprac.cvp_client_errors import CvpApiError, CvpRequestError  # noqa # pylint: disable=unused-import
    HAS_CVPRAC = True
except ImportError:
    HAS_CVPRAC = False
    CVPRAC_IMP_ERR = traceback.format_exc()


MODULE_LOGGER = logging.getLogger('arista.cvp.image_tools')
MODULE_LOGGER.info('Start image_tools module execution')


class CvImageTools():
    """
    CvImageTools Class to manage Cloudvision software images and byndles
    """

    def __init__(self, cv_connection, ansible_module: AnsibleModule = None, check_mode: bool = False):
        self.__cv_client = cv_connection
        self.__ansible = ansible_module
        self.__check_mode = check_mode
        self.refresh_cvp_image_data()

    def __get_images(self):  # sourcery skip: class-extract-method
        images = []

        MODULE_LOGGER.debug('  -> Collecting images')
        response = self.__cv_client.api.get_images()
        images = response['data'] if 'data' in response else []
        MODULE_LOGGER.debug(images)
        if len(images) > 0:
            self.cvp_images = images
            return True
        return False

    def __get_image_bundles(self):
        imageBundles = []
        MODULE_LOGGER.debug('  -> Collecting image bundles')
        response = self.__cv_client.api.get_image_bundles()
        imageBundles = response['data'] if 'data' in response else []
        MODULE_LOGGER.debug(imageBundles)
        if len(imageBundles) > 0:
            self.cvp_imageBundles = imageBundles
            return True
        return False

    def refresh_cvp_image_data(self):
        self.__get_images()
        self.__get_image_bundles()

        return True

    def is_image_present(self, image):
        """
        Checks if a named image is present.

        Parameters
        ----------
        image: str
            The name of the software image

        Returns
        -------
        Bool:
            True if present, False if not
        """
        return any(
            entry["imageFileName"] == os.path.basename(image)
            for entry in self.cvp_images
        )

    def does_bundle_exist(self, bundle):
        """
        Checks if a named bundle already exists

        Parameters
        ----------
        bundle : str
            Name of software image bundle.

        Returns
        -------
        Bool:
            True if present, False if not
        """
        return any(entry["name"] == bundle for entry in self.cvp_imageBundles)

    def get_bundle_key(self, bundle):
        """
        Gets the key for a given bundle

        Parameters
        ----------
        bundle : str
            Ansible module.

        Returns
        -------
        str:
            The string value equivelent to the bundle key,
            or None if not found
        """
        for entry in self.cvp_imageBundles:
            if entry["name"] == bundle:
                return entry["key"]
        return None

    def build_image_list(self, image_list):
        """
        Builds a list of the image data structures, for a given list of image names.

        Parameters
        ----------
        image_list : list
            List of software image names

        Returns
        -------
        List:
            Returns a list of images, with complete data or None in the event of failure
        """
        internal_image_list = []
        image_data = None
        success = True

        for entry in image_list:
            for image in self.cvp_images:
                if image["imageFileName"] == entry:
                    image_data = image

            if image_data is not None:
                internal_image_list.append(image_data)
                image_data = None
            else:
                success = False

        return internal_image_list if success else None

    def module_action(self, image: str, image_list: List[str], bundle_name: str, mode: str = "images", action: str = "get"):
        # sourcery no-metrics
        """
        Method to call the other modules.

        Parameters
        ----------
        image : str
            The name (and/or path) of the software image.
        image_list: list
            List of software image names (used for image bundles)
        bundle_name: str
            The name of the software image bundle
        mode: str
            Default "images". Can run in "images" or "bundles" mode
        action: str
            Default "get". Can add/update, get or remove images or image bundles

        Returns
        -------
        dict:
            result with tasks and information.
        """
        changed = False
        data = {}
        warnings = []

        self.refresh_cvp_image_data()

        if mode in {"image", "images"}:
            if action == "get":
                return changed, {'images': self.cvp_images}, warnings

            elif action == "add" and self.__check_mode is False:
                MODULE_LOGGER.debug("   -> trying to add an image")
                if image != '' and os.path.exists(image):
                    if self.is_image_present(image) is False:
                        MODULE_LOGGER.debug("Image not present. Trying to add.")
                        try:
                            data = self.__cv_client.api.add_image(image)
                            self.refresh_cvp_image_data()
                            MODULE_LOGGER.debug("   -> Returned data follows")
                            MODULE_LOGGER.debug(data)
                            changed = True
                        except Exception as e:
                            self.__ansible.fail_json(msg="{0}".format(e))
                    else:
                        self.__ansible.fail_json(msg="Unable to add image {0}. Image already present on server".format(image))
                else:
                    self.__ansible.fail_json(msg="Specified file ({0}) does not exist".format(image))
            else:
                self.__ansible.fail_json(msg="Deletion of images through API is not currently supported")

        elif mode in {"bundle", "bundles"}:
            if action == "get":
                return changed, {'bundles': self.cvp_imageBundles}, warnings

            elif action == "add" and self.__check_mode is False:
                # There are basically 2 actions - either we are adding a new bundle (save)
                # or changing an existing bundle (update)
                if self.does_bundle_exist(bundle_name):
                    MODULE_LOGGER.debug("   -> Updating existing bundle")
                    warnings.append('Note that when updating a bundle, all the images to be used in the bundle must be listed')
                    cvp_key = self.get_bundle_key(bundle_name)
                    images = self.build_image_list(image_list)
                    if images is not None:
                        try:
                            data = self.__cv_client.api.update_image_bundle(cvp_key, bundle_name, images)
                            changed = True
                            self.refresh_cvp_image_data()
                        except Exception as e:
                            self.__ansible.fail_json(msg="{0}".format(e))
                    else:
                        self.__ansible.fail_json(msg="Unable to update bundle - images not present on server")
                else:
                    images = self.build_image_list(image_list)
                    MODULE_LOGGER.debug("   -> creating a new bundle")
                    if images is not None:
                        try:
                            # MODULE_LOGGER.debug("Bundle name: {0} - Image list: \n{1}".format(bundle_name, str(images)))
                            data = self.__cv_client.api.save_image_bundle(bundle_name, images)
                            changed = True
                            self.refresh_cvp_image_data()
                        except Exception as e:
                            self.__ansible.fail_json(msg="{0}".format(e))
                    else:
                        self.__ansible.fail_json(msg="Unable to create bundle - images not present on server")
                return changed, data, warnings

            elif action == "remove" and self.__check_mode is False:
                MODULE_LOGGER.debug("   -> trying to delete a bundle")
                warnings.append('Note that deleting the image bundle does not delete the images')
                if self.does_bundle_exist(bundle_name):
                    cvp_key = self.get_bundle_key(bundle_name)
                    try:
                        data = self.__cv_client.api.delete_image_bundle(cvp_key, bundle_name)
                        changed = True
                        self.refresh_cvp_image_data()
                    except Exception as e:
                        self.__ansible.fail_json(msg="{0}".format(e))
                else:
                    self.__ansible.fail_json(msg="Unable to delete bundle - not found")

            else:
                # You have reached a logically impossible state
                warnings.append("You have reached a logically impossible state")

        else:
            self.__ansible.fail_json(msg="Unsupported mode {0}".format(mode))

        return changed, data, warnings
