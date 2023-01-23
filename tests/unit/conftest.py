<<<<<<< HEAD
from unittest.mock import create_autospec
import pytest
from tests.lib import mockMagic
from cvprac.cvp_client import CvpClient, CvpApi

=======
import pytest
from unittest.mock import create_autospec
from cvprac.cvp_client import CvpClient, CvpApi
from tests.lib import mockMagic
>>>>>>> 384f2ed (Restructured pytest)

@pytest.fixture
def apply_mock(mocker):
    """
    apply_mock - factory function to return a method to apply mocker.patch() on paths
<<<<<<< HEAD

=======
>>>>>>> 384f2ed (Restructured pytest)
    """
    def _apply_mock_factory(paths: list):
        return [mocker.patch(path) for path in paths]

    return _apply_mock_factory

@pytest.fixture
<<<<<<< HEAD
def mock_cvpClient():
    """
    mock_cvprac - mocks cvprac classes/objects
    """
    # mocked cvpClient object
    mock_cvpClient = create_autospec(CvpClient)
    mock_cvpClient.api = mockMagic.MockCvpApi(spec=CvpApi)
    return mock_cvpClient
=======
def mock_cvprac():
    """
    mock_cvprac - mocks cvprac classes/objects
    """
    # mock class containing dummy cvprac functions
    dummy_cvprac = mockMagic.MockCvpApi()

    # mocked cvpClient object
    mock_cvpClient = create_autospec(CvpClient)
    mock_cvpClient.api = create_autospec(CvpApi)
    return dummy_cvprac, mock_cvpClient
>>>>>>> 384f2ed (Restructured pytest)
