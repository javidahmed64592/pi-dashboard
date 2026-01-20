"""Pi Dashboard server module."""

from python_template_server.template_server import TemplateServer

from pi_dashboard.models import PiDashboardConfig


class PiDashboardServer(TemplateServer):
    """Pi Dashboard FastAPI server."""

    def __init__(self, config: PiDashboardConfig | None = None) -> None:
        """Initialize the PiDashboardServer.

        :param PiDashboardConfig | None config: Optional pre-loaded configuration
        """
        self.config: PiDashboardConfig
        super().__init__(
            package_name="pi_dashboard",
            config=config,
        )

    def validate_config(self, config_data: dict) -> PiDashboardConfig:
        """Validate configuration data against the PiDashboardConfig model.

        :param dict config_data: The configuration data to validate
        :return PiDashboardConfig: The validated configuration model
        :raise ValidationError: If the configuration data is invalid
        """
        return PiDashboardConfig.model_validate(config_data)  # type: ignore[no-any-return]

    def setup_routes(self) -> None:
        """Set up API routes."""
        super().setup_routes()
