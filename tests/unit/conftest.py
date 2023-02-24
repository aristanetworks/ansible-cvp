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
    mock_cvpClient.api = mockMagic.MockCvpApi(spec=CvpApi)
    return mock_cvpClient
