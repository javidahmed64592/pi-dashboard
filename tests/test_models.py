"""Unit tests for the pi_dashboard.models module."""

from pi_dashboard.models import (
    DashboardDatabaseConfig,
    MetricsConfig,
    PiDashboardConfig,
)


# Pi Dashboard server configuration
class TestPiDashboardConfig:
    """Unit tests for the PiDashboardConfig class."""

    def test_model_dump(
        self,
        mock_pi_dashboard_config: PiDashboardConfig,
        mock_database_config: DashboardDatabaseConfig,
        mock_metrics_config: MetricsConfig,
    ) -> None:
        """Test the model_dump method."""
        config_dict = mock_pi_dashboard_config.model_dump()
        assert config_dict["db"] == mock_database_config.model_dump()
        assert config_dict["metrics"] == mock_metrics_config.model_dump()
