"""Unit tests for the pi_dashboard.weather_handler module."""

import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient, Response

from pi_dashboard.models import WeatherConfig, WeatherData, WeatherForecastHour
from pi_dashboard.weather_handler import WeatherHandler, ttl_cache


class TestTTLCache:
    """Unit tests for the ttl_cache decorator."""

    def test_ttl_cache_caches_result(self) -> None:
        """Test that ttl_cache caches the result of an async function."""
        call_count = 0

        @ttl_cache(minutes=30)
        async def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call should execute the function
        result1 = asyncio.run(test_func())
        assert result1 == 1
        assert call_count == 1

        # Second call should return cached result
        result2 = asyncio.run(test_func())
        assert result2 == 1
        assert call_count == 1  # Function not called again

    def test_ttl_cache_expires_after_duration(self) -> None:
        """Test that ttl_cache expires after the specified duration."""
        call_count = 0

        @ttl_cache(minutes=30)
        async def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        with patch("pi_dashboard.weather_handler.BaseResponse.current_timestamp") as mock_timestamp:
            # First call at time T
            mock_timestamp.return_value = "2026-01-01T12:00:00.000000Z"
            result1 = asyncio.run(test_func())
            assert result1 == 1
            assert call_count == 1

            # Second call at T+29 minutes (still cached)
            mock_timestamp.return_value = "2026-01-01T12:29:00.000000Z"
            result2 = asyncio.run(test_func())
            assert result2 == 1
            assert call_count == 1

            # Third call at T+31 minutes (cache expired)
            mock_timestamp.return_value = "2026-01-01T12:31:00.000000Z"
            result3 = asyncio.run(test_func())
            assert result3 == 1 + 1
            assert call_count == 1 + 1


class TestGeocodeLocation:
    """Unit tests for the geocode_location static method."""

    @pytest.fixture
    def mock_geocoding_response(self, mock_weather_config: WeatherConfig) -> dict:
        """Provide a mock geocoding API response."""
        return {
            "results": [
                {
                    "latitude": mock_weather_config.latitude,
                    "longitude": mock_weather_config.longitude,
                    "name": mock_weather_config.location_name,
                }
            ]
        }

    @pytest.fixture
    def mock_httpx_client(self, mock_geocoding_response: dict) -> Generator[AsyncMock]:
        """Mock the httpx.AsyncClient."""
        with patch("pi_dashboard.weather_handler.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock(spec=AsyncClient)
            mock_response = MagicMock(spec=Response)
            mock_response.json.return_value = mock_geocoding_response
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_geocode_location_success(self, mock_httpx_client: AsyncMock, mock_weather_config: WeatherConfig) -> None:
        """Test successful geocoding of a location."""
        result = asyncio.run(WeatherHandler.geocode_location(mock_weather_config.location_name))

        assert result is not None
        assert result == (mock_weather_config.latitude, mock_weather_config.longitude)
        mock_httpx_client.get.assert_called_once()

    def test_geocode_location_no_results(self, mock_httpx_client: AsyncMock) -> None:
        """Test geocoding when no results are found."""
        mock_httpx_client.get.return_value.json.return_value = {"results": []}

        result = asyncio.run(WeatherHandler.geocode_location("NonexistentPlace"))

        assert result is None


class TestGetWeather:
    """Unit tests for the get_weather method."""

    @pytest.fixture
    def mock_weather_handler(self, mock_weather_config: WeatherConfig) -> WeatherHandler:
        """Provide a WeatherHandler instance for testing."""
        return WeatherHandler(
            latitude=mock_weather_config.latitude,
            longitude=mock_weather_config.longitude,
            location_name=mock_weather_config.location_name,
            forecast_hours=mock_weather_config.forecast_hours,
        )

    @pytest.fixture
    def mock_weather_api_response(self, mock_weather_data: WeatherData) -> dict:
        """Provide a mock weather API response."""
        return {
            "current": {
                "time": "2026-01-26T12:00",
                "temperature_2m": mock_weather_data.temperature,
                "relative_humidity_2m": mock_weather_data.humidity,
                "wind_speed_10m": mock_weather_data.wind_speed,
                "weather_code": mock_weather_data.weather_code,
            },
            "hourly": {
                "time": [
                    "2026-01-26T12:00",
                    "2026-01-26T13:00",
                    "2026-01-26T14:00",
                    "2026-01-26T15:00",
                    "2026-01-26T16:00",
                    "2026-01-26T17:00",
                    "2026-01-26T18:00",
                    "2026-01-26T19:00",
                    "2026-01-26T20:00",
                    "2026-01-26T21:00",
                    "2026-01-26T22:00",
                    "2026-01-26T23:00",
                    "2026-01-27T00:00",
                    "2026-01-27T01:00",
                ],
                "temperature_2m": [h.temperature for h in mock_weather_data.forecast]
                + [mock_weather_data.high, mock_weather_data.low],
                "weather_code": [h.weather_code for h in mock_weather_data.forecast] + [45, 45],
            },
        }

    @pytest.fixture
    def mock_httpx_client(self, mock_weather_api_response: dict) -> Generator[AsyncMock]:
        """Mock the httpx.AsyncClient."""
        with patch("pi_dashboard.weather_handler.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock(spec=AsyncClient)
            mock_response = MagicMock(spec=Response)
            mock_response.json.return_value = mock_weather_api_response
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_get_weather(
        self, mock_weather_handler: WeatherHandler, mock_httpx_client: AsyncMock, mock_weather_data: WeatherData
    ) -> None:
        """Test successful weather data retrieval."""
        result = asyncio.run(mock_weather_handler.get_weather())

        assert isinstance(result, WeatherData)
        assert result.location_name == mock_weather_data.location_name
        assert result.temperature == mock_weather_data.temperature
        assert result.weather_code == mock_weather_data.weather_code
        assert result.high == mock_weather_data.high
        assert result.low == mock_weather_data.low
        assert result.humidity == mock_weather_data.humidity
        assert result.wind_speed == mock_weather_data.wind_speed
        assert len(result.forecast) == len(mock_weather_data.forecast)
        assert all(isinstance(hour, WeatherForecastHour) for hour in result.forecast)

    def test_get_weather_forecast_hours_limit(
        self, mock_weather_handler: WeatherHandler, mock_httpx_client: AsyncMock, mock_weather_data: WeatherData
    ) -> None:
        """Test that forecast is limited to configured number of hours."""
        result = asyncio.run(mock_weather_handler.get_weather())

        assert len(result.forecast) == mock_weather_handler.forecast_hours
        # Verify first forecast entry
        assert result.forecast[0].time == mock_weather_data.forecast[0].time
        assert result.forecast[0].temperature == mock_weather_data.forecast[0].temperature
        assert result.forecast[0].weather_code == mock_weather_data.forecast[0].weather_code

    def test_get_weather_time_formatting(
        self, mock_weather_handler: WeatherHandler, mock_httpx_client: AsyncMock
    ) -> None:
        """Test that forecast times are formatted correctly."""
        result = asyncio.run(mock_weather_handler.get_weather())

        # Check time formatting (should be like "12PM", "1PM", not "12:00PM")
        for hour in result.forecast:
            assert "PM" in hour.time or "AM" in hour.time
            # Should not have leading zeros
            if hour.time.startswith("0"):
                pytest.fail(f"Time has leading zero: {hour.time}")

    def test_get_weather_high_low_calculation(
        self, mock_weather_handler: WeatherHandler, mock_httpx_client: AsyncMock, mock_weather_data: WeatherData
    ) -> None:
        """Test that high/low temperatures are calculated correctly from 24-hour forecast."""
        result = asyncio.run(mock_weather_handler.get_weather())

        # Based on mock data
        assert result.high == mock_weather_data.high
        assert result.low == mock_weather_data.low
