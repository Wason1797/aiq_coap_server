from typing import Type
from app.security.payload_validator import PayloadValidator
import pytest


@pytest.fixture(scope="session")
def mock_payload_validator() -> Type[PayloadValidator]:
    class MockValidator(PayloadValidator):
        pass

    MockValidator.init_validator("test_secret")

    return MockValidator
