from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def baseline_image_dir(request):
    """
    Returns the path to the baseline image directory for the current test file.
    """
    return Path(request.module.__file__).parent / "baseline"


@pytest.fixture(scope="session")
def mpl_cleanup():
    """
    Cleans up any temporary matplotlib artifacts after the session.
    """
    return
    # Could add cleanup logic here if needed, but pytest-mpl mostly handles itself
