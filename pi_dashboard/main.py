"""FastAPI Pi Dashboard server using uvicorn."""

from pi_dashboard.server import PiDashboardServer


def run() -> None:
    """Serve the FastAPI application using uvicorn."""
    server = PiDashboardServer()
    server.run()
