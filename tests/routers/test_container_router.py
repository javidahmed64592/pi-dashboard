"""Unit tests for the pi_dashboard.routers.container_router module."""

from fastapi.routing import APIRoute

from pi_dashboard.routers import ContainerRouter


class TestRoutes:
    """Unit tests for route setup in ContainerRouter."""

    def test_setup_routes(self, mock_container_router: ContainerRouter) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_container_router.router.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/containers/",
            "/containers/refresh",
            "/containers/{container_id}/start",
            "/containers/{container_id}/stop",
            "/containers/{container_id}/restart",
            "/containers/{container_id}/update",
            "/containers/{container_id}/logs",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes
