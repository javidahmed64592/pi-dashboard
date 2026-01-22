"""Unit tests for the pi_dashboard.system_metrics_handler module."""

import platform
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pi_dashboard.models import SystemInfo
from pi_dashboard.system_metrics_handler import (
    get_host_path,
    get_host_root,
    get_hostname,
    get_system_info,
    get_system_metrics,
    read_cpu_temperature,
    read_uptime,
)


@pytest.fixture(autouse=True)
def clear_caches() -> Generator[None]:
    """Clear function caches before each test."""
    yield
    get_hostname.cache_clear()
    get_host_root.cache_clear()
    get_host_path.cache_clear()


class TestPaths:
    """Tests for path handling functions."""

    def test_get_host_root(self) -> None:
        """Test the get_host_root function."""
        assert get_host_root() == "/"

    def test_get_host_path(self) -> None:
        """Test the get_host_path function."""
        dir_path = "path/to/dir"
        resolved_path = get_host_path(dir_path)
        assert resolved_path == Path(get_host_root()) / dir_path


class TestGetMetric:
    """Tests for system metrics retrieval functions."""

    @pytest.fixture
    def mock_path_exists(self) -> Generator[MagicMock]:
        """Mock pathlib.Path.exists method."""
        with patch("pathlib.Path.exists") as mock_exists:
            yield mock_exists

    @pytest.fixture
    def mock_read_text(self) -> Generator[MagicMock]:
        """Mock pathlib.Path.read_text method."""
        with patch("pathlib.Path.read_text") as mock_read:
            yield mock_read

    def test_get_hostname_with_file(self, mock_path_exists: MagicMock, mock_read_text: MagicMock) -> None:
        """Test the get_hostname function when hostname file exists."""
        mock_path_exists.return_value = True
        mock_read_text.return_value = "test-hostname\n"

        hostname = get_hostname()
        assert hostname == mock_read_text.return_value.strip()

    def test_get_hostname_without_file(self, mock_path_exists: MagicMock) -> None:
        """Test the get_hostname function when hostname file does not exist."""
        mock_path_exists.return_value = False

        hostname = get_hostname()
        assert hostname == platform.node()

    def test_read_cpu_temperature_with_file(self, mock_path_exists: MagicMock, mock_read_text: MagicMock) -> None:
        """Test the read_cpu_temperature function when temperature file exists."""
        mock_path_exists.return_value = True
        mock_read_text.return_value = "55000"

        temperature = read_cpu_temperature()
        assert temperature == int(mock_read_text.return_value) / 1000.0

    def test_read_cpu_temperature_without_file(self, mock_path_exists: MagicMock) -> None:
        """Test the read_cpu_temperature function when temperature file does not exist."""
        mock_path_exists.return_value = False

        temperature = read_cpu_temperature()
        assert temperature == 0.0

    def test_read_uptime_with_file(self, mock_path_exists: MagicMock, mock_read_text: MagicMock) -> None:
        """Test the read_uptime function when uptime file exists."""
        mock_path_exists.return_value = True
        mock_read_text.return_value = "12345.67 89012.34"

        uptime = read_uptime()
        assert uptime == int(float(mock_read_text.return_value.split()[0]))

    def test_read_uptime_without_file(self, mock_path_exists: MagicMock) -> None:
        """Test the read_uptime function when uptime file does not exist."""
        mock_path_exists.return_value = False

        uptime = read_uptime()
        assert uptime == 0


class TestSystemMetricsHandler:
    """Tests for the system metrics handler functions."""

    @pytest.fixture
    def mock_platform_uname(self, mock_system_info: SystemInfo) -> Generator[MagicMock]:
        """Mock platform.uname function."""
        with patch("platform.uname") as mock_uname:
            mock_uname.return_value = MagicMock(
                system=mock_system_info.system,
                release=mock_system_info.release,
                version=mock_system_info.version,
                machine=mock_system_info.machine,
            )
            yield mock_uname

    @pytest.fixture
    def mock_virtual_memory(self, mock_system_info: SystemInfo) -> Generator[MagicMock]:
        """Mock psutil.virtual_memory function."""
        with patch("pi_dashboard.system_metrics_handler.virtual_memory") as mock_vm:
            mock_vm.return_value = MagicMock(total=mock_system_info.memory_total * 1024 * 1024 * 1024, percent=60.0)
            yield mock_vm

    @pytest.fixture
    def mock_disk_usage(self, mock_system_info: SystemInfo) -> Generator[MagicMock]:
        """Mock psutil.disk_usage function."""
        with patch("pi_dashboard.system_metrics_handler.disk_usage") as mock_du:
            mock_du.return_value = MagicMock(total=mock_system_info.disk_total * 1024 * 1024 * 1024, percent=70.0)
            yield mock_du

    @pytest.fixture
    def mock_cpu_percent(self) -> Generator[MagicMock]:
        """Mock psutil.cpu_percent function."""
        with patch("pi_dashboard.system_metrics_handler.cpu_percent") as mock_cpu:
            mock_cpu.return_value = 50.0
            yield mock_cpu

    @pytest.fixture
    def mock_get_hostname(self, mock_system_info: SystemInfo) -> Generator[MagicMock]:
        """Mock the get_hostname function."""
        with patch("pi_dashboard.system_metrics_handler.get_hostname") as mock_hostname:
            mock_hostname.return_value = mock_system_info.hostname
            yield mock_hostname

    @pytest.fixture
    def mock_read_uptime(self) -> Generator[MagicMock]:
        """Mock the read_uptime function."""
        with patch("pi_dashboard.system_metrics_handler.read_uptime") as mock_uptime:
            mock_uptime.return_value = 123456
            yield mock_uptime

    @pytest.fixture
    def mock_read_cpu_temperature(self) -> Generator[MagicMock]:
        """Mock the read_cpu_temperature function."""
        with patch("pi_dashboard.system_metrics_handler.read_cpu_temperature") as mock_temp:
            mock_temp.return_value = 55.0
            yield mock_temp

    def test_get_system_info(
        self,
        mock_system_info: SystemInfo,
        mock_platform_uname: MagicMock,
        mock_virtual_memory: MagicMock,
        mock_disk_usage: MagicMock,
        mock_get_hostname: MagicMock,
    ) -> None:
        """Test the get_system_info function."""
        result = get_system_info()

        # Verify all fields match the mocked values
        assert result.hostname == mock_system_info.hostname
        assert result.system == mock_system_info.system
        assert result.release == mock_system_info.release
        assert result.version == mock_system_info.version
        assert result.machine == mock_system_info.machine
        assert result.memory_total == mock_system_info.memory_total
        assert result.disk_total == mock_system_info.disk_total

        # Verify mocks were called
        mock_platform_uname.assert_called_once()
        mock_virtual_memory.assert_called_once()
        mock_disk_usage.assert_called_once()
        mock_get_hostname.assert_called_once()

    def test_get_system_metrics(
        self,
        mock_cpu_percent: MagicMock,
        mock_virtual_memory: MagicMock,
        mock_disk_usage: MagicMock,
        mock_read_uptime: MagicMock,
        mock_read_cpu_temperature: MagicMock,
    ) -> None:
        """Test the get_system_metrics function."""
        result = get_system_metrics()

        # Verify all fields match the mocked values
        assert result.cpu_usage == mock_cpu_percent.return_value
        assert result.memory_usage == mock_virtual_memory.return_value.percent
        assert result.disk_usage == mock_disk_usage.return_value.percent
        assert result.uptime == mock_read_uptime.return_value
        assert result.temperature == mock_read_cpu_temperature.return_value

        # Verify mocks were called with correct arguments
        mock_cpu_percent.assert_called_once_with(interval=0.1)
        mock_virtual_memory.assert_called()
        mock_disk_usage.assert_called()
        mock_read_uptime.assert_called_once()
        mock_read_cpu_temperature.assert_called_once()
