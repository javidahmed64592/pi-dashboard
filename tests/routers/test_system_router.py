"""Unit tests for the pi_dashboard.routers.system_router module."""

from fastapi.routing import APIRoute

from pi_dashboard.routers import SystemRouter


class TestRoutes:
    """Unit tests for route setup in SystemRouter."""

    def test_setup_routes(self, mock_system_router: SystemRouter) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_system_router.router.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/system/info",
            "/system/metrics",
            "/system/metrics/history",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes
