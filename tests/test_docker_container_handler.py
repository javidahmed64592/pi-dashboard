"""Unit tests for the pi_dashboard.docker_container_handler module."""

from unittest.mock import MagicMock, PropertyMock

import pytest
from docker.errors import APIError, ImageNotFound

from pi_dashboard.docker_container_handler import DockerContainerHandler


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
        self, mock_docker_container_handler: DockerContainerHandler, ports: dict, expected: str | None
    ) -> None:
        """Test extracting port from standard port mappings."""
        assert mock_docker_container_handler._extract_primary_port(ports) == expected


class TestCheckDockerAvailable:
    """Tests for checking Docker daemon availability."""

    def test_docker_available(self, mock_docker_container_handler: DockerContainerHandler) -> None:
        """Test when Docker daemon is available."""
        mock_docker_container_handler._check_docker_available()

    def test_docker_unavailable(self, mock_docker_container_handler: DockerContainerHandler) -> None:
        """Test when Docker daemon is unavailable."""
        mock_docker_container_handler.client = None

        with pytest.raises(APIError, match="Docker daemon not available"):
            mock_docker_container_handler._check_docker_available()


class TestListContainers:
    """Tests for listing Docker containers."""

    def test_list_containers(
        self, mock_docker_container_handler: DockerContainerHandler, mock_container: MagicMock
    ) -> None:
        """Test successfully listing containers."""
        containers = mock_docker_container_handler.list_containers()

        assert len(containers) == 1

        container = containers[0]
        assert container.container_id == "container_short_id"
        assert container.name == "test-container"
        assert container.image == "test/image:latest"
        assert container.status == "running"
        assert container.port == "443"

    def test_list_containers_with_deleted_image(
        self, mock_docker_container_handler: DockerContainerHandler, mock_docker_client: MagicMock
    ) -> None:
        """Test listing containers when the image has been deleted."""
        # Create a mock container with an image that raises ImageNotFound
        container = MagicMock()
        container.short_id = "container_short_id"
        container.name = "test-container-deleted-image"
        container.status = "running"
        container.ports = {"80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}]}  # noqa: S104
        container.attrs = {"Image": "sha256:36dc4d37740d30a06fd53e1f1a858417369d45cec30aaa60908cf108a954c9db"}

        # Mock the image property to raise ImageNotFound
        type(container).image = PropertyMock(side_effect=ImageNotFound("No such image"))

        # Set up the mock client to return this container
        mock_docker_client.containers.list.return_value = [container]

        # List containers should handle the exception gracefully
        containers = mock_docker_container_handler.list_containers()

        assert len(containers) == 1
        container_result = containers[0]
        assert container_result.container_id == "container_short_id"
        assert container_result.name == "test-container-deleted-image"
        assert container_result.image == "sha256:36dc4"  # First 12 chars of the image ID
        assert container_result.status == "running"
        assert container_result.port == "8080"


class TestStartContainer:
    """Tests for starting Docker containers."""

    def test_start_container(
        self, mock_docker_container_handler: DockerContainerHandler, mock_container: MagicMock
    ) -> None:
        """Test successfully starting a container."""
        container_name = mock_docker_container_handler.start_container("abc123")
        assert container_name == "test-container"
        mock_container.start.assert_called_once()


class TestStopContainer:
    """Tests for stopping Docker containers."""

    def test_stop_container(
        self, mock_docker_container_handler: DockerContainerHandler, mock_container: MagicMock
    ) -> None:
        """Test successfully stopping a container."""
        container_name = mock_docker_container_handler.stop_container(container_id="abc123", timeout=10)
        assert container_name == "test-container"
        mock_container.stop.assert_called_once_with(timeout=10)


class TestRestartContainer:
    """Tests for restarting Docker containers."""

    def test_restart_container(
        self, mock_docker_container_handler: DockerContainerHandler, mock_container: MagicMock
    ) -> None:
        """Test successfully restarting a container."""
        container_name = mock_docker_container_handler.restart_container(container_id="abc123", timeout=10)
        assert container_name == "test-container"
        mock_container.restart.assert_called_once_with(timeout=10)


class TestUpdateContainer:
    """Tests for updating Docker containers."""

    def test_update_container_success(
        self, mock_docker_container_handler: DockerContainerHandler, mock_container: MagicMock
    ) -> None:
        """Test successfully updating a container."""
        container_name, new_container_id = mock_docker_container_handler.update_container(
            container_id="abc123", timeout=10
        )

        assert container_name == "test-container"
        assert new_container_id == "new_container_short_id"

        # Verify the update process
        mock_docker_container_handler.client.images.pull.assert_called_once_with("test/image:latest")  # ty:ignore[unresolved-attribute]
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once()
        mock_docker_container_handler.client.containers.run.assert_called_once()  # ty:ignore[unresolved-attribute]


class TestGetContainerLogs:
    """Tests for getting Docker container logs."""

    def test_get_container_logs(
        self, mock_docker_container_handler: DockerContainerHandler, mock_container: MagicMock
    ) -> None:
        """Test successfully getting container logs."""
        logs = mock_docker_container_handler.get_container_logs("abc123", 100)

        assert logs == ["log line 1", "log line 2", "log line 3"]
        mock_container.logs.assert_called_once_with(tail=100, timestamps=False, stream=False)
