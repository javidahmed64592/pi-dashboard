"""Container router for Pi Dashboard."""

import logging
from typing import Annotated

from docker.errors import APIError, NotFound
from fastapi import HTTPException, Query, Request
from python_template_server.models import ResponseCode
from python_template_server.routers import BaseRouter

from pi_dashboard.docker_container_handler import DockerContainerHandler
from pi_dashboard.models import DockerContainerActionResponse, DockerContainerListResponse, DockerContainerLogsResponse

logger = logging.getLogger(__name__)


class ContainerRouter(BaseRouter):
    """Router for the container endpoints."""

    def configure_router(self, container_handler: DockerContainerHandler) -> None:
        """Configure the router with necessary dependencies."""
        self._container_handler = container_handler

    def setup_routes(self) -> None:
        """Set up the API routes for the container endpoints."""
        self.add_route(
            endpoint="/",
            handler_function=self.list_containers,
            response_model=DockerContainerListResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/refresh",
            handler_function=self.refresh_containers,
            response_model=DockerContainerListResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/{container_id}/start",
            handler_function=self.start_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/{container_id}/stop",
            handler_function=self.stop_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/{container_id}/restart",
            handler_function=self.restart_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/{container_id}/update",
            handler_function=self.update_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/{container_id}/logs",
            handler_function=self.get_container_logs,
            response_model=DockerContainerLogsResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )

    async def list_containers(self, request: Request) -> DockerContainerListResponse:
        """List all Docker containers.

        :return DockerContainerListResponse: Response containing list of containers
        """
        try:
            containers = self._container_handler.list_containers()
            return DockerContainerListResponse(
                message=f"Retrieved {len(containers)} containers",
                containers=containers,
            )
        except Exception as e:
            logger.exception("Unexpected error while listing containers")
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def refresh_containers(self, request: Request) -> DockerContainerListResponse:
        """Refresh container list from Docker daemon.

        :return DockerContainerListResponse: Response containing refreshed list of containers
        """
        try:
            containers = self._container_handler.list_containers()
            return DockerContainerListResponse(
                message=f"Retrieved {len(containers)} containers",
                containers=containers,
            )
        except Exception as e:
            logger.exception("Unexpected error while refreshing containers")
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def start_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Start a Docker container.

        :param str container_id: The container ID to start
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self._container_handler.start_container(container_id=container_id)
            return DockerContainerActionResponse(
                message=f"Container {container_name} started successfully",
                container_id=container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while starting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while starting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def stop_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Stop a Docker container.

        :param str container_id: The container ID to stop
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self._container_handler.stop_container(container_id=container_id, timeout=10)
            return DockerContainerActionResponse(
                message=f"Container {container_name} stopped successfully",
                container_id=container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while stopping container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while stopping container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def restart_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Restart a Docker container.

        :param str container_id: The container ID to restart
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self._container_handler.restart_container(container_id=container_id, timeout=10)
            return DockerContainerActionResponse(
                message=f"Container {container_name} restarted successfully",
                container_id=container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while restarting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while restarting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def update_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Update a Docker container by pulling latest image and recreating it.

        :param str container_id: The container ID to update
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name, new_container_id = self._container_handler.update_container(
                container_id=container_id, timeout=10
            )
            return DockerContainerActionResponse(
                message=f"Container {container_name} updated successfully",
                container_id=new_container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="Container not found",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while updating container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while updating container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def get_container_logs(
        self,
        request: Request,
        container_id: str,
        lines: Annotated[int, Query(ge=1, le=1000)],
    ) -> DockerContainerLogsResponse:
        """Get logs for a Docker container.

        :param str container_id: The container ID
        :param int lines: Number of log lines to retrieve (1-1000)
        :return DockerContainerLogsResponse: Response containing log lines
        """
        try:
            log_lines = self._container_handler.get_container_logs(container_id=container_id, lines=lines)
            return DockerContainerLogsResponse(
                message=f"Retrieved {len(log_lines)} log lines for container {container_id}",
                container_id=container_id,
                logs=log_lines,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while fetching logs for container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while fetching logs for container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e
