"""Shared pytest fixtures for INTERCEPTA test suite.

Per L4.2 §2.1: synthetic-data-only test policy.
Per L4.2 §2.2: this conftest provides shared fixtures, parametrized substrate
fixtures, and CI environment detection.
"""

import os
import pytest


def pytest_collection_modifyitems(config, items):
    """Skip GPU tests on CI by default (per L4.2 §2.4)."""
    if os.getenv("CI") == "true":
        skip_gpu = pytest.mark.skip(reason="GPU tests not run on CI; nightly on Explorer")
        for item in items:
            if "gpu" in item.keywords:
                item.add_marker(skip_gpu)


@pytest.fixture(scope="session")
def random_seed():
    """Canonical seed for reproducibility (matches Charter v1.2 + L4.1)."""
    return 42
