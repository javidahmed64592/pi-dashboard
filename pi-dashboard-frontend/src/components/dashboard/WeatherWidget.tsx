"use client";

import { useEffect, useState } from "react";

import { getWeather } from "@/lib/api";
import type { WeatherData } from "@/lib/types";

// Convert WMO weather codes to emoji and description
// Based on: https://open-meteo.com/en/docs
const getWeatherInfo = (
  code: number
): { emoji: string; description: string } => {
  const weatherMap: Record<number, { emoji: string; description: string }> = {
    0: { emoji: "☀️", description: "Clear sky" },
    1: { emoji: "🌤️", description: "Mainly clear" },
    2: { emoji: "⛅", description: "Partly cloudy" },
    3: { emoji: "☁️", description: "Overcast" },
    45: { emoji: "🌫️", description: "Foggy" },
    48: { emoji: "🌫️", description: "Foggy" },
    51: { emoji: "🌦️", description: "Light drizzle" },
    53: { emoji: "🌦️", description: "Drizzle" },
    55: { emoji: "🌧️", description: "Heavy drizzle" },
    56: { emoji: "🌨️", description: "Freezing drizzle" },
    57: { emoji: "🌨️", description: "Freezing drizzle" },
    61: { emoji: "🌦️", description: "Light rain" },
    63: { emoji: "🌧️", description: "Rain" },
    65: { emoji: "🌧️", description: "Heavy rain" },
    66: { emoji: "🌨️", description: "Freezing rain" },
    67: { emoji: "🌨️", description: "Freezing rain" },
    71: { emoji: "🌨️", description: "Light snow" },
    73: { emoji: "❄️", description: "Snow" },
    75: { emoji: "❄️", description: "Heavy snow" },
    77: { emoji: "🌨️", description: "Snow grains" },
    80: { emoji: "🌦️", description: "Light showers" },
    81: { emoji: "🌧️", description: "Showers" },
    82: { emoji: "⛈️", description: "Heavy showers" },
    85: { emoji: "🌨️", description: "Light snow showers" },
    86: { emoji: "❄️", description: "Heavy snow showers" },
    95: { emoji: "⛈️", description: "Thunderstorm" },
    96: { emoji: "⛈️", description: "Thunderstorm with hail" },
    99: { emoji: "⛈️", description: "Thunderstorm with hail" },
  };

  return weatherMap[code] || { emoji: "❓", description: "Unknown" };
};

export default function WeatherWidget() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getWeather();
        setWeather(response.weather);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch weather"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();

    // Refresh weather every 30 minutes
    const interval = setInterval(fetchWeather, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
        <h2 className="text-lg font-bold text-neon-blue font-mono mb-4">
          WEATHER
        </h2>
        <div className="text-center text-text-muted font-mono">Loading...</div>
      </div>
    );
  }

  if (error || !weather) {
    return (
      <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
        <h2 className="text-lg font-bold text-neon-blue font-mono mb-4">
          WEATHER
        </h2>
        <div className="text-center text-red-400 font-mono text-sm">
          {error || "No weather data available"}
        </div>
      </div>
    );
  }

  const currentWeatherInfo = getWeatherInfo(weather.weather_code);

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-neon-blue font-mono">WEATHER</h2>
        <div className="text-xs text-text-muted font-mono">
          {weather.location_name}
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-4xl font-bold text-text-primary font-mono">
            {weather.temperature}°C
          </div>
          <div className="text-sm text-text-muted font-mono">
            {currentWeatherInfo.description}
          </div>
        </div>
        <div className="text-6xl">{currentWeatherInfo.emoji}</div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-xs font-mono">
          <span className="text-text-muted">High:</span>{" "}
          <span className="text-text-primary">{weather.high}°C</span>
        </div>
        <div className="text-xs font-mono">
          <span className="text-text-muted">Low:</span>{" "}
          <span className="text-text-primary">{weather.low}°C</span>
        </div>
        <div className="text-xs font-mono">
          <span className="text-text-muted">Humidity:</span>{" "}
          <span className="text-text-primary">{weather.humidity}%</span>
        </div>
        <div className="text-xs font-mono">
          <span className="text-text-muted">Wind:</span>{" "}
          <span className="text-text-primary">{weather.wind_speed} km/h</span>
        </div>
      </div>

      <div className="border-t border-border pt-3">
        <div className="text-xs text-text-muted font-mono mb-2">
          12-HOUR FORECAST
        </div>
        <div className="flex justify-between">
          {weather.forecast
            .filter((_, index) => index % 3 === 0)
            .slice(0, 4)
            .map((hour, index) => (
              <div key={index} className="text-center">
                <div className="text-xs text-text-muted font-mono">
                  {hour.time}
                </div>
                <div className="text-2xl my-1">
                  {getWeatherInfo(hour.weather_code).emoji}
                </div>
                <div className="text-xs text-text-primary font-mono">
                  {hour.temperature}°
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
