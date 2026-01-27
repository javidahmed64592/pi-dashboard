"""Docker container management handler."""

import logging

import docker
from docker.errors import APIError, NotFound
from python_template_server.models import ResponseCode

from pi_dashboard.models import (
    ContainerActionResponse,
    ContainerListResponse,
    DockerContainer,
)

logger = logging.getLogger(__name__)


class ContainerHandler:
    """Handler for Docker container operations."""

    def __init__(self) -> None:
        """Initialize the ContainerHandler."""
        self.client: docker.DockerClient | None = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Docker client."""
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            logger.info("Successfully connected to Docker daemon")
        except Exception:
            logger.exception("Failed to connect to Docker daemon")
            self.client = None

    def _extract_primary_port(self, ports: dict) -> str | None:
        """Extract the primary (first) port from Docker container.

        :param dict ports: Docker ports dictionary
        :return str | None: The first host port as a string, or None if no ports
        """
        if not ports:
            return None

        for host_bindings in ports.values():
            if host_bindings is None:
                continue

            # Return the first host port found
            for binding in host_bindings:
                host_port = binding.get("HostPort", "")
                if host_port:
                    return str(host_port)

        return None

    def list_containers(self) -> ContainerListResponse:
        """List all Docker containers.

        :return ContainerListResponse: Response containing list of containers
        """
        if not self.client:
            return ContainerListResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker daemon not available",
                timestamp=ContainerListResponse.current_timestamp(),
                containers=[],
            )

        try:
            containers = self.client.containers.list(all=True)
            docker_containers: list[DockerContainer] = []

            for container in containers:
                # Get image name with tag
                image_name = container.image.tags[0] if container.image.tags else container.image.id[:12]

                # Extract primary port
                primary_port = self._extract_primary_port(container.ports)

                docker_containers.append(
                    DockerContainer(
                        container_id=container.short_id,
                        name=container.name,
                        image=image_name,
                        status=container.status,
                        port=primary_port,
                    )
                )

            return ContainerListResponse(
                message=f"Retrieved {len(docker_containers)} containers",
                timestamp=ContainerListResponse.current_timestamp(),
                containers=docker_containers,
            )

        except APIError:
            logger.exception("Docker API error while listing containers")
            return ContainerListResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker API error",
                timestamp=ContainerListResponse.current_timestamp(),
                containers=[],
            )
        except Exception:
            logger.exception("Unexpected error while listing containers")
            return ContainerListResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Unexpected error",
                timestamp=ContainerListResponse.current_timestamp(),
                containers=[],
            )

    def start_container(self, container_id: str) -> ContainerActionResponse:
        """Start a Docker container.

        :param str container_id: The container ID to start
        :return ContainerActionResponse: Response indicating success or failure
        """
        if not self.client:
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker daemon not available",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="start",
            )

        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info("Started container: %s (%s)", container.name, container_id)
            return ContainerActionResponse(
                message=f"Container {container.name} started successfully",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="start",
            )

        except NotFound:
            logger.exception("Container not found: %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message=f"Container not found: {container_id}",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="start",
            )
        except APIError:
            logger.exception("Docker API error while starting container %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker API error",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="start",
            )

    def stop_container(self, container_id: str, timeout: int = 10) -> ContainerActionResponse:
        """Stop a Docker container.

        :param str container_id: The container ID to stop
        :param int timeout: Timeout in seconds before forcefully killing the container
        :return ContainerActionResponse: Response indicating success or failure
        """
        if not self.client:
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker daemon not available",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="stop",
            )

        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            logger.info("Stopped container: %s (%s)", container.name, container_id)
            return ContainerActionResponse(
                message=f"Container {container.name} stopped successfully",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="stop",
            )

        except NotFound:
            logger.exception("Container not found: %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message=f"Container not found: {container_id}",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="stop",
            )
        except APIError:
            logger.exception("Docker API error while stopping container %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker API error",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="stop",
            )

    def restart_container(self, container_id: str, timeout: int = 10) -> ContainerActionResponse:
        """Restart a Docker container.

        :param str container_id: The container ID to restart
        :param int timeout: Timeout in seconds before forcefully killing the container
        :return ContainerActionResponse: Response indicating success or failure
        """
        if not self.client:
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker daemon not available",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="restart",
            )

        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=timeout)
            logger.info("Restarted container: %s (%s)", container.name, container_id)
            return ContainerActionResponse(
                message=f"Container {container.name} restarted successfully",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="restart",
            )

        except NotFound:
            logger.exception("Container not found: %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message=f"Container not found: {container_id}",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="restart",
            )
        except APIError:
            logger.exception("Docker API error while restarting container %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker API error",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="restart",
            )

    def update_container(self, container_id: str) -> ContainerActionResponse:
        """Update a Docker container by pulling latest image and recreating it.

        :param str container_id: The container ID to update
        :return ContainerActionResponse: Response indicating success or failure
        """
        if not self.client:
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker daemon not available",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="update",
            )

        try:
            # Get container details
            container = self.client.containers.get(container_id)
            container_name = container.name

            # Get image information
            image_tags = container.image.tags
            if not image_tags:
                return ContainerActionResponse(
                    code=ResponseCode.INTERNAL_SERVER_ERROR,
                    message="Cannot update container: image has no tags",
                    timestamp=ContainerActionResponse.current_timestamp(),
                    container_id=container_id,
                    action="update",
                )

            image_name = image_tags[0]

            # Get container configuration
            config = container.attrs["Config"]
            host_config = container.attrs["HostConfig"]

            logger.info("Pulling latest image: %s", image_name)

            # Pull latest image
            self.client.images.pull(image_name)

            logger.info("Stopping and removing container: %s", container_name)

            # Stop and remove old container
            container.stop(timeout=10)
            container.remove()

            logger.info("Creating new container with updated image: %s", container_name)

            # Create new container with same configuration
            new_container = self.client.containers.run(
                image=image_name,
                name=container_name,
                ports=host_config.get("PortBindings"),
                volumes=host_config.get("Binds"),
                environment=config.get("Env"),
                network_mode=host_config.get("NetworkMode"),
                restart_policy=host_config.get("RestartPolicy"),
                detach=True,
            )

            logger.info("Container updated successfully: %s (%s)", container_name, new_container.short_id)
            return ContainerActionResponse(
                message=f"Container {container_name} updated successfully",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=new_container.short_id,
                action="update",
            )

        except NotFound:
            logger.exception("Container not found: %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.NOT_FOUND,
                message="Container not found",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="update",
            )
        except APIError:
            logger.exception("Docker API error while updating container %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Docker API error",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="update",
            )
        except Exception:
            logger.exception("Unexpected error while updating container %s", container_id)
            return ContainerActionResponse(
                code=ResponseCode.INTERNAL_SERVER_ERROR,
                message="Unexpected error",
                timestamp=ContainerActionResponse.current_timestamp(),
                container_id=container_id,
                action="update",
            )
