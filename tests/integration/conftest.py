import os
from typing import Final

import pytest

ALLOW_DESTRUCTIVE_TEST_CLEANUP: Final[str] = "ALLOW_DESTRUCTIVE_TEST_CLEANUP"
ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE: Final[str] = "1"


@pytest.fixture(scope="session")
def allow_destructive() -> None:
    """Use on fixtures that require potentially dangerous cleanup."""
    if os.getenv(ALLOW_DESTRUCTIVE_TEST_CLEANUP) != ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE:
        raise pytest.UsageError(
            "Destructive cleanup is disabled: "
            f"{ALLOW_DESTRUCTIVE_TEST_CLEANUP} must be set to {ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE}. "
            "This guard prevents accidental cleanup of non-test data."
        )
