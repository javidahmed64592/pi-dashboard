"""Unit tests for the container handler module."""

from unittest.mock import MagicMock

import pytest
from docker.errors import APIError

from pi_dashboard.container_handler import ContainerHandler


class TestExtractPrimaryPort:
    """Tests for extracting primary port."""

    @pytest.mark.parametrize(
        ("ports", "expected"),
        [
            (
                {
                    "443/tcp": [{"HostPort": "443", "HostIp": "0.0.0.0"}],  # noqa: S104
                    "80/tcp": [{"HostPort": "8080", "HostIp": "0.0.0.0"}],  # noqa: S104
                },
                "443",
            ),
            ({}, None),
            ({"443/tcp": None}, None),
        ],
    )
    def test_extract_primary_port_standard(
        self, mock_container_handler: ContainerHandler, ports: dict, expected: str | None
    ) -> None:
        """Test extracting port from standard port mappings."""
        assert mock_container_handler._extract_primary_port(ports) == expected


class TestCheckDockerAvailable:
    """Tests for checking Docker daemon availability."""

    def test_docker_available(self, mock_container_handler: ContainerHandler) -> None:
        """Test when Docker daemon is available."""
        mock_container_handler._check_docker_available()

    def test_docker_unavailable(self, mock_container_handler: ContainerHandler) -> None:
        """Test when Docker daemon is available."""
        mock_container_handler.client = None

        with pytest.raises(APIError, match="Docker daemon not available"):
            mock_container_handler._check_docker_available()


class TestListContainers:
    """Tests for listing Docker containers."""

    def test_list_containers(self, mock_container_handler: ContainerHandler, mock_container: MagicMock) -> None:
        """Test successfully listing containers."""
        containers = mock_container_handler.list_containers()

        assert len(containers) == 1

        container = containers[0]
        assert container.container_id == "container_short_id"
        assert container.name == "test-container"
        assert container.image == "test/image:latest"
        assert container.status == "running"
        assert container.port == "443"


class TestStartContainer:
    """Tests for starting Docker containers."""

    def test_start_container(self, mock_container_handler: ContainerHandler, mock_container: MagicMock) -> None:
        """Test successfully starting a container."""
        container_name = mock_container_handler.start_container("abc123")
        assert container_name == "test-container"
        mock_container.start.assert_called_once()


class TestStopContainer:
    """Tests for stopping Docker containers."""

    def test_stop_container(self, mock_container_handler: ContainerHandler, mock_container: MagicMock) -> None:
        """Test successfully stopping a container."""
        container_name = mock_container_handler.stop_container(container_id="abc123", timeout=10)
        assert container_name == "test-container"
        mock_container.stop.assert_called_once_with(timeout=10)


class TestRestartContainer:
    """Tests for restarting Docker containers."""

    def test_restart_container(self, mock_container_handler: ContainerHandler, mock_container: MagicMock) -> None:
        """Test successfully restarting a container."""
        container_name = mock_container_handler.restart_container(container_id="abc123", timeout=10)
        assert container_name == "test-container"
        mock_container.restart.assert_called_once_with(timeout=10)


class TestUpdateContainer:
    """Tests for updating Docker containers."""

    def test_update_container_success(
        self, mock_container_handler: ContainerHandler, mock_container: MagicMock
    ) -> None:
        """Test successfully updating a container."""
        container_name, new_container_id = mock_container_handler.update_container(container_id="abc123", timeout=10)

        assert container_name == "test-container"
        assert new_container_id == "new_container_short_id"

        # Verify the update process
        mock_container_handler.client.images.pull.assert_called_once_with("test/image:latest")
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once()
        mock_container_handler.client.containers.run.assert_called_once()
