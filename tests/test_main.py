"""Unit tests for the pi_dashboard.main module."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from pi_dashboard.main import run
from pi_dashboard.models import PiDashboardConfig


@pytest.fixture
def mock_pi_dashboard_server_class(
    mock_pi_dashboard_config: PiDashboardConfig,
) -> Generator[MagicMock]:
    """Mock PiDashboardServer class."""
    with patch("pi_dashboard.main.PiDashboardServer") as mock_server:
        mock_server.load_config.return_value = mock_pi_dashboard_config
        yield mock_server


class TestRun:
    """Unit tests for the run function."""

    def test_run(self, mock_pi_dashboard_server_class: MagicMock) -> None:
        """Test successful server run."""
        run()

        mock_pi_dashboard_server_class.return_value.run.assert_called_once()
