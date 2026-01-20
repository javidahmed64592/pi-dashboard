"""System metrics collection handler for Pi Dashboard.

This module provides functions to collect system metrics from the host system,
even when running inside a Docker container. It uses psutil and direct file
reading from mounted host directories.
"""

import os
import platform
from pathlib import Path

import psutil

from pi_dashboard.models import SystemInfo, SystemMetrics


def get_host_path(relative_path: str) -> Path:
    """Get the path to a host system file from within Docker container.

    If running in Docker with host mounts, accesses files from /host/* paths.
    Otherwise, accesses system files directly.

    :param str relative_path: The relative path (e.g., "proc/uptime")
    :return Path: The full path to the file
    """
    # Check if we're in Docker with host mounts
    host_root = os.getenv("HOST_ROOT", "")
    if host_root and Path(host_root).exists():
        return Path(host_root) / relative_path
    return Path("/") / relative_path


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
        pass
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
        pass
    return 0


def get_system_info() -> SystemInfo:
    """Get system information using platform module.

    When running in Docker, reads hostname from host filesystem.

    :return SystemInfo: System information data
    """
    uname = platform.uname()

    # Try to get host's hostname when running in Docker
    try:
        hostname_file = get_host_path("etc/hostname")
        if hostname_file.exists():
            hostname = hostname_file.read_text().strip()
        else:
            hostname = uname.node
    except (FileNotFoundError, PermissionError):
        hostname = uname.node

    return SystemInfo(
        hostname=hostname,
        system=uname.system,
        release=uname.release,
        version=uname.version,
        machine=uname.machine,
    )


def get_system_metrics() -> SystemMetrics:
    """Get current system metrics.

    Collects CPU, memory, disk usage, uptime, and temperature.
    When running in Docker with host mounts, reads host system metrics.

    :return SystemMetrics: System metrics data
    """
    # CPU usage (as percentage)
    cpu_usage = psutil.cpu_percent(interval=0.1)

    # Memory usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_total = memory.total // (1024 * 1024)  # Convert to MB

    # Disk usage - use host root if available
    host_root = os.getenv("HOST_ROOT", "/")
    disk = psutil.disk_usage(host_root)
    disk_usage = disk.percent
    disk_total = disk.total // (1024 * 1024 * 1024)  # Convert to GB

    # Uptime
    uptime = read_uptime()

    # CPU temperature
    temperature = read_cpu_temperature()

    return SystemMetrics(
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        memory_total=memory_total,
        disk_usage=disk_usage,
        disk_total=disk_total,
        uptime=uptime,
        temperature=temperature,
    )
