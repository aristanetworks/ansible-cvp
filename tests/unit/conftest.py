# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from unittest.mock import create_autospec
import pytest
from tests.lib import mockMagic
from cvprac.cvp_client import CvpClient, CvpApi


@pytest.fixture
def apply_mock(mocker):
    """
    apply_mock - factory function to return a method to apply mocker.patch() on paths
    """
    def _apply_mock_factory(paths: list):
        return [mocker.patch(path) for path in paths]

    return _apply_mock_factory

@pytest.fixture
def mock_cvpClient():
    """
    mock_cvprac - mocks cvprac classes/objects
    """
    # mocked cvpClient object
    mock_cvpClient = create_autospec(CvpClient)
    mock_cvpClient.api = create_autospec(spec=CvpApi)
    mock_cvpClient.api.validate_config_for_device.side_effect = mockMagic.validate_config_for_device
    mock_cvpClient.api.move_device_to_container.side_effect = mockMagic.move_device_to_container
    mock_cvpClient.api.remove_image_from_element.side_effect = mockMagic.remove_image_from_element
    mock_cvpClient.api.get_image_bundle_by_name.side_effect = mockMagic.get_image_bundle_by_name
    mock_cvpClient.api.apply_image_to_element.side_effect = mockMagic.apply_image_to_element
    mock_cvpClient.api.get_image_bundle_by_name.side_effect = mockMagic.get_image_bundle_by_name
    mock_cvpClient.api.device_decommissioning.side_effect = mockMagic.device_decommissioning
    mock_cvpClient.api.device_decommissioning_status_get_one.side_effect = mockMagic.device_decommissioning_status_get_one
    mock_cvpClient.api.reset_device.side_effect = mockMagic.reset_device
    mock_cvpClient.api.delete_device.side_effect = mockMagic.delete_device
    return mock_cvpClient
