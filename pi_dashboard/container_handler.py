"""Docker container management handler."""

import logging

import docker
from docker.errors import APIError

from pi_dashboard.models import DockerContainer

logger = logging.getLogger(__name__)


class ContainerHandler:
    """Handler for Docker container operations."""

    def __init__(self) -> None:
        """Initialize the ContainerHandler."""
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info("Successfully connected to Docker daemon")
        except Exception:
            logger.exception("Failed to connect to Docker daemon")
            self.client = None

    @staticmethod
    def _extract_primary_port(ports: dict) -> str | None:
        """Extract the primary (first) port from Docker container.

        :param dict ports: Docker ports dictionary
        :return str | None: The first host port as a string, or None if no ports
        """
        if not ports:
            return None

        for host_bindings in ports.values():
            if host_bindings is None:
                continue

            for binding in host_bindings:
                host_port = binding.get("HostPort", "")
                if host_port:
                    return str(host_port)

        return None

    def _check_docker_available(self) -> None:
        """Check if Docker daemon is available.

        :raises APIError: If Docker daemon is not available
        """
        if not self.client:
            msg = "Docker daemon not available"
            logger.error(msg)
            raise APIError(msg)

    def list_containers(self) -> list[DockerContainer]:
        """List all Docker containers.

        :return list[DockerContainer]: List of containers
        """
        self._check_docker_available()

        containers = self.client.containers.list(all=True)
        docker_containers: list[DockerContainer] = []

        for container in containers:
            image_name = container.image.tags[0] if container.image.tags else container.image.id[:12]
            primary_port = ContainerHandler._extract_primary_port(container.ports)

            docker_containers.append(
                DockerContainer(
                    container_id=container.short_id,
                    name=container.name,
                    image=image_name,
                    status=container.status,
                    port=primary_port,
                )
            )

        return docker_containers

    def start_container(self, container_id: str) -> str:
        """Start a Docker container.

        :param str container_id: The container ID to start
        :return str: The name of the started container
        """
        self._check_docker_available()

        container = self.client.containers.get(container_id)
        container.start()
        logger.info("Started container: %s (%s)", container.name, container_id)
        return str(container.name)

    def stop_container(self, container_id: str, timeout: int) -> str:
        """Stop a Docker container.

        :param str container_id: The container ID to stop
        :param int timeout: Timeout in seconds before forcefully killing the container
        :return str: The name of the stopped container
        """
        self._check_docker_available()

        container = self.client.containers.get(container_id)
        container.stop(timeout=timeout)
        logger.info("Stopped container: %s (%s)", container.name, container_id)
        return str(container.name)

    def restart_container(self, container_id: str, timeout: int) -> str:
        """Restart a Docker container.

        :param str container_id: The container ID to restart
        :param int timeout: Timeout in seconds before forcefully killing the container
        :return str: The name of the restarted container
        """
        self._check_docker_available()

        container = self.client.containers.get(container_id)
        container.restart(timeout=timeout)
        logger.info("Restarted container: %s (%s)", container.name, container_id)
        return str(container.name)

    def update_container(self, container_id: str, timeout: int) -> tuple[str, str]:
        """Update a Docker container by pulling latest image and recreating it.

        :param str container_id: The container ID to update
        :param int timeout: Timeout in seconds before forcefully killing the container
        :return tuple[str, str]: Tuple of (container_name, new_container_id)
        """
        self._check_docker_available()

        container = self.client.containers.get(container_id)
        container_name = container.name

        # Get image information
        image_tags = container.image.tags
        if not image_tags:
            msg = f"Container {container_name} has an image with no tags; cannot update."
            logger.error(msg)
            raise APIError(msg)

        image_name = image_tags[0]

        # Get container configuration
        config = container.attrs["Config"]
        host_config = container.attrs["HostConfig"]

        logger.info("Pulling latest image: %s", image_name)
        self.client.images.pull(image_name)

        # Stop and remove old container
        logger.info("Stopping and removing container: %s", container_name)
        container.stop(timeout=timeout)
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
        return container_name, new_container.short_id
