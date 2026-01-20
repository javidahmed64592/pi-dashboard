"""System metrics collection handler for Pi Dashboard.

This module provides functions to collect system metrics from the host system,
even when running inside a Docker container. It uses psutil and direct file
reading from mounted host directories.
"""

import logging
import os
import platform
from pathlib import Path

import psutil

from pi_dashboard.models import SystemInfo, SystemMetrics

logger = logging.getLogger(__name__)


def get_host_root() -> str:
    """Get the host root path for metrics collection.

    :return str: The host root path
    """
    return os.getenv("HOST_ROOT", "/")


def get_host_path(relative_path: str) -> Path:
    """Get the path to a host system file from within Docker container.

    If running in Docker with host mounts, accesses files from /host/* paths.
    Otherwise, accesses system files directly.

    :param str relative_path: The relative path (e.g., "proc/uptime")
    :return Path: The full path to the file
    """
    return Path(get_host_root()) / relative_path


def get_hostname() -> str:
    """Get the system hostname, attempting to read from host filesystem if in Docker.

    :return str: The system hostname
    """
    hostname = platform.node()
    try:
        hostname_file = get_host_path("etc/hostname")
        if hostname_file.exists():
            hostname = hostname_file.read_text().strip()
    except PermissionError:
        logger.warning("Could not read hostname from host filesystem", exc_info=True)
    except Exception:
        logger.exception("Unexpected error reading hostname from host filesystem")
    return hostname


def read_cpu_temperature() -> float:
    """Read CPU temperature from thermal zone.

    :return float: CPU temperature in Celsius, or 0.0 if unavailable
    """
    try:
        thermal_file = get_host_path("sys/class/thermal/thermal_zone0/temp")
        if thermal_file.exists():
            temp_millidegrees = int(thermal_file.read_text().strip())
            return temp_millidegrees / 1000.0
    except (FileNotFoundError, ValueError, PermissionError):
        logger.warning("Could not read CPU temperature from file", exc_info=True)
    except Exception:
        logger.exception("Unexpected error reading CPU temperature")
    return 0.0


def read_uptime() -> int:
    """Read system uptime from /proc/uptime.

    :return int: System uptime in seconds, or 0 if unavailable
    """
    try:
        uptime_file = get_host_path("proc/uptime")
        if uptime_file.exists():
            uptime_str = uptime_file.read_text().strip().split()[0]
            return int(float(uptime_str))
    except (FileNotFoundError, ValueError, IndexError, PermissionError):
        logger.warning("Could not read system uptime from file", exc_info=True)
    except Exception:
        logger.exception("Unexpected error reading system uptime")
    return 0


def get_system_info() -> SystemInfo:
    """Get system information using platform module.

    When running in Docker, reads hostname from host filesystem.

    :return SystemInfo: System information data
    """
    uname = platform.uname()

    return SystemInfo(
        hostname=get_hostname(),
        system=uname.system,
        release=uname.release,
        version=uname.version,
        machine=uname.machine,
        memory_total=psutil.virtual_memory().total / (1024 * 1024 * 1024),  # Convert to GB
        disk_total=psutil.disk_usage(get_host_root()).total / (1024 * 1024 * 1024),  # Convert to GB
    )


def get_system_metrics() -> SystemMetrics:
    """Get current system metrics.

    Collects CPU, memory, disk usage, uptime, and temperature.
    When running in Docker with host mounts, reads host system metrics.

    :return SystemMetrics: System metrics data
    """
    return SystemMetrics(
        cpu_usage=psutil.cpu_percent(interval=0.1),
        memory_usage=psutil.virtual_memory().percent,
        disk_usage=psutil.disk_usage(get_host_root()).percent,
        uptime=read_uptime(),
        temperature=read_cpu_temperature(),
    )
