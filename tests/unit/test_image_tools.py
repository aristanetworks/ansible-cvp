#!/usr/bin/python
# coding: utf-8 -*-

import logging
from ansible_collections.arista.cvp.plugins.module_utils.image_tools import CvImageTools
import pytest
import pprint
from ansible_collections.arista.cvp.plugins.module_utils.image_tools import CvImageTools
from ansible_collections.arista.cvp.plugins.module_utils.exceptions import AnsibleCVPApiError, AnsibleCVPNotFoundError
from tests.lib import mock
from tests.data import image_unit as data
from tests.lib.utils import generate_test_ids_dict

LOGGER = logging.getLogger(__name__)

@pytest.fixture
def cvp_database(request):
    database = mock.MockCVPDatabase()
    if hasattr(request, 'param'):
        database.devices.update(request.param.get('devices', []))
        database.containers.update(request.param.get('containers', []))
        database.configlets.update(request.param.get('configlets', []))
        database.images.update(request.param.get('images', []))
        database.image_bundles.update(request.param.get('image_bundles', []))
    else:
        database = mock.MockCVPDatabase(
            images = data.CV_IMAGES_PAYLOAD['images'] if 'images' in data.data.CV_IMAGES_PAYLOADS else {},
            image_bundles = data.CV_IMAGES_PAYLOAD['image_bundles'] if 'image_bundles' in data.data.CV_IMAGES_PAYLOADS else {}
        )
    LOGGER.info('Initial CVP state: %s', database)
    yield database
    LOGGER.info('Final CVP state: %s', database)

@pytest.fixture()
def image_unit_tool(request, cvp_database):
    cvp_client = mock.get_cvp_client(cvp_database)
    instance = CvImageTools(cv_connection=cvp_client)
    LOGGER.debug('Initial CVP state: %s', cvp_database)
    yield instance
    LOGGER.debug('Mock calls: %s', pprint.pformat(cvp_client.mock_calls))


@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools__get_images(image_unit_tool, cvp_database):
    result = image_unit_tool._CvImageTools__get_images()
    LOGGER.info('__get_images response: %s', str(result))
    if 'data' in cvp_database.images and  len(cvp_database.images['data']) > 0:
        LOGGER.info('Size of DB is: %s', str(len(cvp_database.images['data'])))
        assert result is True
    else:
        assert result is False



@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools__get_image_bundles(image_unit_tool, cvp_database):
    result = image_unit_tool._CvImageTools__get_image_bundles()
    LOGGER.info('__get_image_bundles response: %s', str(result))
    if 'data' in cvp_database.images and  len(cvp_database.image_bundles['data']) > 0:
        LOGGER.info('Size of DB is: %s', str(len(cvp_database.image_bundles['data'])))
        assert result is True
    else:
        assert result is False

@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools_is_image_present(image_unit_tool, cvp_database):
    if 'data' not in cvp_database.images or len(cvp_database.images['data']) == 0:
        pytest.skip('Not concerned by this test as no image is in DB')
    for image in cvp_database.images['data']:
        fake_path_file = '/fake/path/to/'+image['imageFileName']
        is_filename_found = image_unit_tool.is_image_present(fake_path_file)
        assert is_filename_found is True
        LOGGER.info('Filename (%s) exists on CVP', str(image['imageFileName']))

@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools_does_bundle_exist(image_unit_tool, cvp_database):
    if 'data' not in cvp_database.image_bundles or len(cvp_database.image_bundles['data']) == 0:
        pytest.skip('Not concerned by this test as no image bundle is in DB')
    for bundle in cvp_database.image_bundles['data']:
        is_bundle_found = image_unit_tool.does_bundle_exist(bundle['name'])
        assert is_bundle_found is True
        LOGGER.info('Filename (%s) exists on CVP', str(bundle['name']))

@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools_does_bundle_exist_with_invalid(image_unit_tool, cvp_database):
    if 'data' not in cvp_database.image_bundles or len(cvp_database.image_bundles['data']) == 0:
        pytest.skip('Not concerned by this test as no image bundle is in DB')
    for bundle in cvp_database.image_bundles['data']:
        is_bundle_found = image_unit_tool.does_bundle_exist('FAKE_BUNDLE')
        assert is_bundle_found is False
        LOGGER.info('Filename (FAKE_BUNDLE) does not exists on CVP')

@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools_get_bundle_key(image_unit_tool, cvp_database):
    if 'data' not in cvp_database.image_bundles or len(cvp_database.image_bundles['data']) == 0:
        pytest.skip('Not concerned by this test as no image bundle is in DB')
    for bundle in cvp_database.image_bundles['data']:
        bundle_key = image_unit_tool.get_bundle_key(bundle['name'])
        assert bundle_key == bundle['key']
        LOGGER.info('Bundle Key (%s) is for bundle %s', str(bundle['key']), str(bundle['name']))

@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools_get_bundle_key(image_unit_tool, cvp_database):
    if 'data' not in cvp_database.image_bundles or len(cvp_database.image_bundles['data']) == 0:
        pytest.skip('Not concerned by this test as no image bundle is in DB')
    for bundle in cvp_database.image_bundles['data']:
        bundle_key = image_unit_tool.get_bundle_key(bundle['name'])
        assert bundle_key == bundle['key']
        LOGGER.info('Bundle Key (%s) is for bundle %s', str(bundle['key']), str(bundle['name']))

@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools_build_image_list(image_unit_tool, cvp_database):
    if 'data' not in cvp_database.image_bundles or len(cvp_database.image_bundles['data']) == 0:
        pytest.skip('Not concerned by this test as no image bundle is in DB')
    images_to_bundle = [image['imageFileName'] for image in cvp_database.images['data']]
    built_image_list = image_unit_tool.build_image_list(images_to_bundle)
    LOGGER.info('Image to bundle %s', str(images_to_bundle))
    LOGGER.info('Bundle data %s', str(built_image_list))
    for image in cvp_database.images['data']:
        assert image == next((entry for entry in built_image_list if entry['name'] == image['name']), None)
    LOGGER.info('List of images to attach to bundle is valid')

@pytest.mark.generic
@pytest.mark.usefixtures("cvp_database")
@pytest.mark.usefixtures("image_unit_tool")
@pytest.mark.parametrize("cvp_database", data.CV_IMAGES_PAYLOADS, indirect=["cvp_database"], ids=generate_test_ids_dict)
def test_CvImageTools_build_image_list_with_some_fakes(image_unit_tool, cvp_database):
    if 'data' not in cvp_database.images or len(cvp_database.images['data']) == 0:
        pytest.skip('Not concerned by this test as no image is in DB')
    images_to_bundle = [image['imageFileName'] for image in cvp_database.images['data']]
    images_to_bundle.append('FAKE_IMAGE')
    built_image_list = image_unit_tool.build_image_list(images_to_bundle)
    LOGGER.info('Image to bundle %s', str(images_to_bundle))
    LOGGER.info('Bundle data %s', str(built_image_list))
    assert built_image_list is None
