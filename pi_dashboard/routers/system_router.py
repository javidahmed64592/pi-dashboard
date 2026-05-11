"""System router for Pi Dashboard."""

from fastapi import Request
from python_template_server.routers import BaseRouter

from pi_dashboard.db import MetricsDatabaseManager
from pi_dashboard.models import (
    GetSystemInfoResponse,
    GetSystemMetricsHistoryRequest,
    GetSystemMetricsHistoryResponse,
    GetSystemMetricsResponse,
)
from pi_dashboard.system_metrics_handler import get_system_info, get_system_metrics


class SystemRouter(BaseRouter):
    """Router for the system endpoints."""

    def configure_router(self, db: MetricsDatabaseManager) -> None:
        """Configure the router with necessary dependencies."""
        self._db = db

    def setup_routes(self) -> None:
        """Set up the API routes for the system endpoints."""
        self.add_route(
            endpoint="/info",
            handler_function=self.get_system_info,
            response_model=GetSystemInfoResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/metrics",
            handler_function=self.get_system_metrics,
            response_model=GetSystemMetricsResponse,
            methods=["GET"],
            limited=False,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/metrics/history",
            handler_function=self.get_system_metrics_history,
            response_model=GetSystemMetricsHistoryResponse,
            methods=["POST"],
            limited=False,
            authentication_required=True,
        )

    async def get_system_info(self, request: Request) -> GetSystemInfoResponse:
        """Get system information.

        :return GetSystemInfoResponse: The system information response model
        """
        info = get_system_info()
        return GetSystemInfoResponse(
            message="Retrieved system info successfully",
            info=info,
        )

    async def get_system_metrics(self, request: Request) -> GetSystemMetricsResponse:
        """Get system metrics.

        :return GetSystemMetricsResponse: The system metrics response model
        """
        metrics = get_system_metrics()
        return GetSystemMetricsResponse(
            message="Retrieved system metrics successfully",
            metrics=metrics,
        )

    async def get_system_metrics_history(
        self, request: Request, body: GetSystemMetricsHistoryRequest
    ) -> GetSystemMetricsHistoryResponse:
        """Get system metrics history.

        :return GetSystemMetricsHistoryResponse: The system metrics history response model
        """
        entries = self._db.get_system_metrics_entries_since(body.last_n_seconds, body.max_data_points)
        return GetSystemMetricsHistoryResponse(
            message="Retrieved system metrics history successfully",
            history=entries,
        )
