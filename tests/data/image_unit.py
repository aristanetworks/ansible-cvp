#!/usr/bin/env python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
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
