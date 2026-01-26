"""Weather handler using Open-Meteo API."""

import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

import httpx
from python_template_server.models import BaseResponse

from pi_dashboard.models import (
    WeatherData,
    WeatherForecastHour,
)

logger = logging.getLogger(__name__)


def ttl_cache(minutes: int) -> Callable:
    """Decorator to cache function results with a time-to-live (TTL).

    :param int minutes: Cache duration in minutes
    """

    def decorator(func: Callable) -> Callable:
        cache_data = {"result": None, "timestamp": None}

        @wraps(func)
        async def wrapper(*args: tuple, **kwargs: dict) -> Any:  # noqa: ANN401
            now_str = BaseResponse.current_timestamp()
            now = datetime.fromisoformat(now_str.rstrip("Z"))

            # Check if cache is valid
            if cache_data["result"] is not None and cache_data["timestamp"] is not None:
                # Both timestamps are timezone-aware (UTC), safe to subtract
                cache_age = now - cache_data["timestamp"]
                cache_ttl = timedelta(minutes=minutes)
                if cache_age < cache_ttl:
                    logger.debug("Returning cached %s data (age: %s)", func.__name__, cache_age)
                    return cache_data["result"]

                logger.debug("Cache expired for %s (age: %s)", func.__name__, cache_age)

            # Fetch fresh data
            logger.info("Fetching fresh data for %s", func.__name__)
            result = await func(*args, **kwargs)

            # Update cache
            cache_data["result"] = result
            cache_data["timestamp"] = now

            return result

        return wrapper

    return decorator


class WeatherHandler:
    """Handler for weather data using Open-Meteo API."""

    # Open-Meteo API endpoints
    GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_API = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, latitude: float, longitude: float, location_name: str, forecast_hours: int) -> None:
        """Initialize the WeatherHandler.

        :param float latitude: Latitude coordinate for weather location
        :param float longitude: Longitude coordinate for weather location
        :param str location_name: Human-readable location name
        :param int forecast_hours: Number of hours to include in the forecast
        """
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name
        self.forecast_hours = forecast_hours

    @staticmethod
    async def geocode_location(location: str) -> tuple[float, float] | None:
        """Geocode a location name to latitude/longitude coordinates.

        :param str location: Location name (e.g., "London", "New York", "Tokyo")
        :return tuple[float, float] | None: Tuple of (latitude, longitude) or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    WeatherHandler.GEOCODING_API,
                    params={"name": location, "count": 1, "language": "en", "format": "json"},
                )
                response.raise_for_status()
                data = response.json()

                if "results" in data and len(data["results"]) > 0:
                    result = data["results"][0]
                    latitude = result["latitude"]
                    longitude = result["longitude"]
                    logger.info("Geocoded '%s' to coordinates: %.4f, %.4f", location, latitude, longitude)
                    return (latitude, longitude)

                logger.warning("No geocoding results found for location: %s", location)
                return None

        except Exception:
            logger.exception("Error geocoding location: %s", location)
            return None

    @ttl_cache(minutes=30)
    async def get_weather(self) -> WeatherData:
        """Get current weather data from Open-Meteo API with 30-minute cache.

        :return WeatherData: The fetched weather data
        :raises Exception: If API request fails
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    WeatherHandler.WEATHER_API,
                    params={
                        "latitude": self.latitude,
                        "longitude": self.longitude,
                        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                        "hourly": "temperature_2m,weather_code",
                        "timezone": "auto",
                        "forecast_days": 2,  # Need 2 days to ensure 12 future hours
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Parse current weather
                current = data["current"]
                current_temp = round(current["temperature_2m"], 1)
                current_humidity = current["relative_humidity_2m"]
                current_wind_speed = round(current["wind_speed_10m"], 1)
                current_weather_code = current["weather_code"]

                # Parse hourly forecast (next 12 hours)
                hourly = data["hourly"]
                hourly_times = hourly["time"]
                hourly_temps = hourly["temperature_2m"]
                hourly_codes = hourly["weather_code"]

                # Get next 12 hours starting from current hour
                forecast_hours = []
                current_time_str = current["time"]

                logger.debug("Current time from API: %s", current_time_str)
                logger.debug("First hourly time: %s", hourly_times[0] if hourly_times else "None")
                logger.debug("Total hourly entries: %d", len(hourly_times))

                for i in range(len(hourly_times)):
                    if len(forecast_hours) >= self.forecast_hours:
                        break

                    hourly_time_str = hourly_times[i]
                    # Compare times as strings (YYYY-MM-DDTHH:MM format)
                    # Include current hour and next 11 hours
                    if hourly_time_str >= current_time_str:
                        forecast_time = datetime.fromisoformat(hourly_time_str)
                        forecast_hours.append(
                            WeatherForecastHour(
                                time=forecast_time.strftime("%I%p").lstrip("0"),  # e.g., "3PM"
                                temperature=round(hourly_temps[i], 1),
                                weather_code=hourly_codes[i],
                            )
                        )

                logger.info("Generated %d forecast hours", len(forecast_hours))

                # Calculate high/low from next 24 hours
                high_temp = round(max(hourly_temps[:24]), 1)
                low_temp = round(min(hourly_temps[:24]), 1)

                return WeatherData(
                    location_name=self.location_name,
                    temperature=current_temp,
                    weather_code=current_weather_code,
                    high=high_temp,
                    low=low_temp,
                    humidity=current_humidity,
                    wind_speed=current_wind_speed,
                    forecast=forecast_hours,
                )

        except Exception:
            logger.exception("Error fetching weather from Open-Meteo API")
            raise
