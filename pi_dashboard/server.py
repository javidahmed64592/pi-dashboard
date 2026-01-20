"""Pi Dashboard server module."""

from python_template_server.models import ResponseCode
from python_template_server.template_server import TemplateServer

from pi_dashboard.models import (
    GetSystemInfoResponse,
    GetSystemMetricsResponse,
    PiDashboardConfig,
    SystemInfo,
    SystemMetrics,
)


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
        self.add_authenticated_route(
            endpoint="/system/info",
            handler_function=self.get_system_info,
            response_model=GetSystemInfoResponse,
            methods=["GET"],
            limited=False,
        )
        self.add_authenticated_route(
            endpoint="/system/metrics",
            handler_function=self.get_system_metrics,
            response_model=GetSystemMetricsResponse,
            methods=["GET"],
            limited=False,
        )
        super().setup_routes()

    async def get_system_info(self) -> GetSystemInfoResponse:
        """Get system information.

        :return GetSystemInfoResponse: The system information response model
        """
        return GetSystemInfoResponse(
            code=ResponseCode.OK,
            message="Retrieved system info successfully",
            timestamp=GetSystemInfoResponse.current_timestamp(),
            info=SystemInfo(
                hostname="",
                node="",
                system="",
                release="",
                version="",
                machine="",
            ),
        )

    async def get_system_metrics(self) -> GetSystemMetricsResponse:
        """Get system metrics.

        :return GetSystemMetricsResponse: The system metrics response model
        """
        return GetSystemMetricsResponse(
            code=ResponseCode.OK,
            message="Retrieved system metrics successfully",
            timestamp=GetSystemMetricsResponse.current_timestamp(),
            metrics=SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                memory_total=0,
                disk_usage=0.0,
                disk_total=0,
                uptime=0,
                temperature=0.0,
            ),
        )
