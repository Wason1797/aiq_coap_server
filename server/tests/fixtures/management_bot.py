from app.telegram.bot import ManagementBot
import pytest

from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def mock_management_bot() -> MagicMock:
    return MagicMock(ManagementBot)
