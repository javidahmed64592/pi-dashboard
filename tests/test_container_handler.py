"""Unit tests for the container handler module."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from docker.errors import APIError, NotFound
from python_template_server.models import ResponseCode

from pi_dashboard.container_handler import ContainerHandler


@pytest.fixture
def mock_docker_client() -> Mock:
    """Provide a mock Docker client for testing."""
    client = Mock()
    client.ping.return_value = True
    return client


@pytest.fixture
def container_handler(mock_docker_client: Mock) -> ContainerHandler:
    """Provide a ContainerHandler instance with mocked Docker client."""
    with patch("pi_dashboard.container_handler.docker.from_env", return_value=mock_docker_client):
        handler = ContainerHandler()
    return handler


@pytest.fixture
def mock_container() -> Mock:
    """Provide a mock Docker container."""
    container = Mock()
    container.short_id = "abc123def456"
    container.name = "test-container"
    container.status = "running"
    container.ports = {
        "443/tcp": [{"HostIp": "0.0.0.0", "HostPort": "443"}],
        "80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}],
    }

    # Mock image
    mock_image = Mock()
    mock_image.tags = ["test/image:latest"]
    mock_image.id = "sha256:abcdef123456"
    container.image = mock_image

    # Mock attrs
    container.attrs = {
        "Created": "2024-01-01T00:00:00.000000000Z",
        "Config": {
            "Env": ["ENV_VAR=value"],
        },
        "HostConfig": {
            "PortBindings": {"443/tcp": [{"HostPort": "443"}]},
            "Binds": ["/data:/app/data"],
            "NetworkMode": "bridge",
            "RestartPolicy": {"Name": "unless-stopped"},
        },
    }

    return container


class TestContainerHandlerInitialization:
    """Tests for ContainerHandler initialization."""

    def test_init_success(self, mock_docker_client: Mock) -> None:
        """Test successful initialization with Docker daemon connection."""
        with patch("pi_dashboard.container_handler.docker.from_env", return_value=mock_docker_client):
            handler = ContainerHandler()

        assert handler.client == mock_docker_client
        mock_docker_client.ping.assert_called_once()

    def test_init_failure(self) -> None:
        """Test initialization when Docker daemon is unavailable."""
        with patch("pi_dashboard.container_handler.docker.from_env", side_effect=Exception("Connection refused")):
            handler = ContainerHandler()

        assert handler.client is None


class TestListContainers:
    """Tests for listing Docker containers."""

    def test_list_containers_success(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test successfully listing containers."""
        container_handler.client.containers.list.return_value = [mock_container]

        response = container_handler.list_containers()

        assert response.code == ResponseCode.OK
        assert response.docker_available is True
        assert len(response.containers) == 1

        container = response.containers[0]
        assert container.container_id == "abc123def456"
        assert container.name == "test-container"
        assert container.image == "test/image:latest"
        assert container.status == "running"
        assert container.port == "443"

    def test_list_containers_no_image_tags(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test listing containers with no image tags."""
        mock_container.image.tags = []
        container_handler.client.containers.list.return_value = [mock_container]

        response = container_handler.list_containers()

        assert response.code == ResponseCode.OK
        assert len(response.containers) == 1
        assert response.containers[0].image == "sha256:abcde"  # Shortened ID (12 chars)

    def test_list_containers_no_ports(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test listing containers with no port mappings."""
        mock_container.ports = {}
        container_handler.client.containers.list.return_value = [mock_container]

        response = container_handler.list_containers()

        assert response.code == ResponseCode.OK
        assert response.containers[0].port is None

    def test_list_containers_null_port_bindings(
        self, container_handler: ContainerHandler, mock_container: Mock
    ) -> None:
        """Test listing containers with null port bindings."""
        mock_container.ports = {"443/tcp": None}
        container_handler.client.containers.list.return_value = [mock_container]

        response = container_handler.list_containers()

        assert response.code == ResponseCode.OK
        assert response.containers[0].port is None

    def test_list_containers_docker_unavailable(self) -> None:
        """Test listing containers when Docker daemon is unavailable."""
        handler = ContainerHandler()
        handler.client = None

        response = handler.list_containers()

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert response.docker_available is False
        assert len(response.containers) == 0
        assert "Docker daemon not available" in response.message

    def test_list_containers_api_error(self, container_handler: ContainerHandler) -> None:
        """Test listing containers with Docker API error."""
        container_handler.client.containers.list.side_effect = APIError("API Error")

        response = container_handler.list_containers()

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert response.docker_available is True
        assert len(response.containers) == 0
        assert "Docker API error" in response.message

    def test_list_containers_unexpected_error(self, container_handler: ContainerHandler) -> None:
        """Test listing containers with unexpected error."""
        container_handler.client.containers.list.side_effect = Exception("Unexpected error")

        response = container_handler.list_containers()

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert response.docker_available is False
        assert len(response.containers) == 0
        assert "Unexpected error" in response.message


class TestStartContainer:
    """Tests for starting Docker containers."""

    def test_start_container_success(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test successfully starting a container."""
        container_handler.client.containers.get.return_value = mock_container

        response = container_handler.start_container("abc123")

        assert response.code == ResponseCode.OK
        assert response.container_id == "abc123"
        assert response.action == "start"
        assert "started successfully" in response.message
        mock_container.start.assert_called_once()

    def test_start_container_docker_unavailable(self) -> None:
        """Test starting container when Docker daemon is unavailable."""
        handler = ContainerHandler()
        handler.client = None

        response = handler.start_container("abc123")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Docker daemon not available" in response.message

    def test_start_container_not_found(self, container_handler: ContainerHandler) -> None:
        """Test starting container that doesn't exist."""
        container_handler.client.containers.get.side_effect = NotFound("Container not found")

        response = container_handler.start_container("nonexistent")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Container not found" in response.message

    def test_start_container_api_error(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test starting container with Docker API error."""
        container_handler.client.containers.get.return_value = mock_container
        mock_container.start.side_effect = APIError("Cannot start container")

        response = container_handler.start_container("abc123")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Docker API error" in response.message


class TestStopContainer:
    """Tests for stopping Docker containers."""

    def test_stop_container_success(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test successfully stopping a container."""
        container_handler.client.containers.get.return_value = mock_container

        response = container_handler.stop_container("abc123")

        assert response.code == ResponseCode.OK
        assert response.container_id == "abc123"
        assert response.action == "stop"
        assert "stopped successfully" in response.message
        mock_container.stop.assert_called_once_with(timeout=10)

    def test_stop_container_custom_timeout(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test stopping container with custom timeout."""
        container_handler.client.containers.get.return_value = mock_container

        response = container_handler.stop_container("abc123", timeout=30)

        assert response.code == ResponseCode.OK
        mock_container.stop.assert_called_once_with(timeout=30)

    def test_stop_container_docker_unavailable(self) -> None:
        """Test stopping container when Docker daemon is unavailable."""
        handler = ContainerHandler()
        handler.client = None

        response = handler.stop_container("abc123")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Docker daemon not available" in response.message

    def test_stop_container_not_found(self, container_handler: ContainerHandler) -> None:
        """Test stopping container that doesn't exist."""
        container_handler.client.containers.get.side_effect = NotFound("Container not found")

        response = container_handler.stop_container("nonexistent")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Container not found" in response.message


class TestRestartContainer:
    """Tests for restarting Docker containers."""

    def test_restart_container_success(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test successfully restarting a container."""
        container_handler.client.containers.get.return_value = mock_container

        response = container_handler.restart_container("abc123")

        assert response.code == ResponseCode.OK
        assert response.container_id == "abc123"
        assert response.action == "restart"
        assert "restarted successfully" in response.message
        mock_container.restart.assert_called_once_with(timeout=10)

    def test_restart_container_docker_unavailable(self) -> None:
        """Test restarting container when Docker daemon is unavailable."""
        handler = ContainerHandler()
        handler.client = None

        response = handler.restart_container("abc123")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Docker daemon not available" in response.message


class TestUpdateContainer:
    """Tests for updating Docker containers."""

    def test_update_container_success(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test successfully updating a container."""
        container_handler.client.containers.get.return_value = mock_container

        # Mock the new container created after update
        new_container = Mock()
        new_container.short_id = "new123"
        new_container.name = "test-container"
        container_handler.client.containers.run.return_value = new_container

        response = container_handler.update_container("abc123")

        assert response.code == ResponseCode.OK
        assert response.container_id == "new123"
        assert response.action == "update"
        assert "updated successfully" in response.message

        # Verify the update process
        container_handler.client.images.pull.assert_called_once_with("test/image:latest")
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once()
        container_handler.client.containers.run.assert_called_once()

    def test_update_container_no_image_tags(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test updating container with no image tags."""
        mock_container.image.tags = []
        container_handler.client.containers.get.return_value = mock_container

        response = container_handler.update_container("abc123")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "image has no tags" in response.message

    def test_update_container_docker_unavailable(self) -> None:
        """Test updating container when Docker daemon is unavailable."""
        handler = ContainerHandler()
        handler.client = None

        response = handler.update_container("abc123")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Docker daemon not available" in response.message

    def test_update_container_not_found(self, container_handler: ContainerHandler) -> None:
        """Test updating container that doesn't exist."""
        container_handler.client.containers.get.side_effect = NotFound("Container not found")

        response = container_handler.update_container("nonexistent")

        assert response.code == ResponseCode.NOT_FOUND
        assert "Container not found" in response.message

    def test_update_container_pull_error(self, container_handler: ContainerHandler, mock_container: Mock) -> None:
        """Test updating container with image pull error."""
        container_handler.client.containers.get.return_value = mock_container
        container_handler.client.images.pull.side_effect = APIError("Failed to pull image")

        response = container_handler.update_container("abc123")

        assert response.code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Docker API error" in response.message


class TestExtractPrimaryPort:
    """Tests for extracting primary port."""

    def test_extract_primary_port_standard(self, container_handler: ContainerHandler) -> None:
        """Test extracting port from standard port mappings."""
        ports = {
            "443/tcp": [{"HostPort": "443", "HostIp": "0.0.0.0"}],
            "80/tcp": [{"HostPort": "8080", "HostIp": "0.0.0.0"}],
        }

        result = container_handler._extract_primary_port(ports)

        assert result == "443"

    def test_extract_primary_port_empty(self, container_handler: ContainerHandler) -> None:
        """Test extracting port from empty port mappings."""
        result = container_handler._extract_primary_port({})

        assert result is None

    def test_extract_primary_port_none_value(self, container_handler: ContainerHandler) -> None:
        """Test extracting port from mappings with None value."""
        ports = {"443/tcp": None}

        result = container_handler._extract_primary_port(ports)

        assert result is None

    def test_extract_primary_port_first_binding(self, container_handler: ContainerHandler) -> None:
        """Test that only first port is extracted when multiple exist."""
        ports = {
            "80/tcp": [
                {"HostPort": "8080", "HostIp": "0.0.0.0"},
                {"HostPort": "8081", "HostIp": "127.0.0.1"},
            ]
        }

        result = container_handler._extract_primary_port(ports)

        assert result == "8080"
