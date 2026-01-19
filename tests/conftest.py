"""Pytest fixtures for the application's unit tests."""

import pytest

from pi_dashboard.models import PiDashboardConfig


# Pi Dashboard server configuration fixture
@pytest.fixture
def mock_pi_dashboard_config() -> PiDashboardConfig:
    """Provide a PiDashboardConfig instance for testing."""
    return PiDashboardConfig.model_validate({})
