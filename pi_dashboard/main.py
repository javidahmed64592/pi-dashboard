"""FastAPI Pi Dashboard server using uvicorn."""

from pi_dashboard.server import PiDashboardServer


def run() -> None:
    """Serve the FastAPI application using uvicorn.

    :raise SystemExit: If configuration fails to load or SSL certificate files are missing
    """
    server = PiDashboardServer()
    server.run()
