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


CV_IMAGES_PAYLOADS = [
    {   'name': '0 image, 1 bundle',
        'images': {
            "total": 0,
            "data": []
        },
        'image_bundles': {
            "data": [
                {
                    "key": "imagebundle_1643897984608204097",
                    "name": "EOS-4.26.1F",
                    "note": "",
                    "user": "tgrimonet",
                    "isCertifiedImageBundle": "true",
                    "updatedDateInLongFormat": 1643897984608,
                    "imageIds": [
                    "EOS-4.26.1F.swi"
                    ],
                    "appliedContainersCount": 0,
                    "appliedDevicesCount": 0
                }
            ],
            "total": 1,
            "imageBundleMapper": {},
            "assignedImageBundleId": ""
        }
    },
    {   'name': '0 image fake number, 1 bundle',
        'images': {
            "total": 100,
            "data": []
        },
        'image_bundles': {
            "data": [
                {
                    "key": "imagebundle_1643897984608204097",
                    "name": "EOS-4.26.1F",
                    "note": "",
                    "user": "tgrimonet",
                    "isCertifiedImageBundle": "true",
                    "updatedDateInLongFormat": 1643897984608,
                    "imageIds": [
                    "EOS-4.26.1F.swi"
                    ],
                    "appliedContainersCount": 0,
                    "appliedDevicesCount": 0
                }
            ],
            "total": 1,
            "imageBundleMapper": {},
            "assignedImageBundleId": ""
        }
    },
    {
        'name': '1 image, 1 bundle',
        'images': {
            "total": 1,
            "data": [
                {
                    "name": "EOS-4.26.1F.swi",
                    "sha512": "ce967d23eac686d74207d668bb65495500b2148017d9c880df083f296634ba732de4419649a7a273714383ed8f79519db1e6c59cb1f66a82cec4eaf33672e5bf",
                    "swiVarient": "US",
                    "imageSize": "962.2 MB",
                    "version": "4.26.1F-22602519.4261F",
                    "swiMaxHwepoch": "2",
                    "isRebootRequired": "true",
                    "user": "tgrimonet",
                    "uploadedDateinLongFormat": 1643897952009,
                    "isHotFix": "false",
                    "imageBundleKeys": [
                    "imagebundle_1643897984608204097"
                    ],
                    "key": "EOS-4.26.1F.swi",
                    "imageId": "EOS-4.26.1F.swi",
                    "imageFileName": "EOS-4.26.1F.swi",
                    "md5": "",
                    "imageFile": ""
                }
            ]
        },
        'image_bundles': {
            "data": [
                {
                    "key": "imagebundle_1643897984608204097",
                    "name": "EOS-4.26.1F",
                    "note": "",
                    "user": "tgrimonet",
                    "isCertifiedImageBundle": "true",
                    "updatedDateInLongFormat": 1643897984608,
                    "imageIds": [
                    "EOS-4.26.1F.swi"
                    ],
                    "appliedContainersCount": 0,
                    "appliedDevicesCount": 0
                }
            ],
            "total": 1,
            "imageBundleMapper": {},
            "assignedImageBundleId": ""
        }
    },
    {
        'name': 'No image, 0 bundle',
        'image_bundles': {
            "data": [],
            "total": 0,
            "imageBundleMapper": {},
            "assignedImageBundleId": ""
        }
    },
]
