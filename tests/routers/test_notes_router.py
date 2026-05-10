"""Unit tests for the pi_dashboard.routers.notes_router module."""

from fastapi.routing import APIRoute

from pi_dashboard.routers import NotesRouter


class TestRoutes:
    """Unit tests for route setup in NotesRouter."""

    def test_setup_routes(self, mock_notes_router: NotesRouter) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_notes_router.router.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/notes/",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes
