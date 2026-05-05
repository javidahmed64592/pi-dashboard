"""Unit tests for the pi_dashboard.models module."""

from pi_dashboard.models import (
    MetricsConfig,
    PiDashboardConfig,
)


# Pi Dashboard server configuration
class TestPiDashboardConfig:
    """Unit tests for the PiDashboardConfig class."""

    def test_model_dump(
        self,
        mock_pi_dashboard_config: PiDashboardConfig,
        mock_metrics_config: MetricsConfig,
    ) -> None:
        """Test the model_dump method."""
        assert mock_metrics_config.model_dump() == mock_pi_dashboard_config.model_dump()["metrics"]
