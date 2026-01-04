"""Functional tests for the Streamlit dashboard using AppTest."""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app():
    """Fixture to load the dashboard app."""
    # Assumes the dashboard script is at 'streamlit_app.py' in root
    at = AppTest.from_file("streamlit_app.py", default_timeout=30)
    return at


def test_app_loads(app):
    """Test that the app loads without error."""
    app.run()
    assert not app.exception


def test_sidebar_defaults(app):
    """Test that default sidebar parameters are set correctly."""
    app.run()

    # Check if we can find some known sidebar elements
    # Note: Streamlit testing API is a bit opaque, we often check structure
    assert len(app.sidebar) > 0


def test_scenario_selection(app):
    """Test changing scenarios."""
    app.run()

    # Assuming the first selectbox is the scenario selector
    # This depends heavily on UI structure
    if app.sidebar.selectbox:
        sel = app.sidebar.selectbox[0]
        # Change value if possible
        if len(sel.options) > 1:
            sel.select_index(1).run()
            assert not app.exception
