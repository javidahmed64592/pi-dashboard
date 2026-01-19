"""Unit tests for the pi_dashboard.models module."""

from pi_dashboard.models import PiDashboardConfig


# Pi Dashboard server configuration
class TestPiDashboardConfig:
    """Unit tests for the PiDashboardConfig class."""

    def test_model_dump(
        self,
        mock_pi_dashboard_config: PiDashboardConfig,
    ) -> None:
        """Test the model_dump method."""
        assert isinstance(mock_pi_dashboard_config.model_dump(), dict)
