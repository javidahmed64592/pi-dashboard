import { act, render, screen, waitFor } from "@testing-library/react";

import WeatherWidget from "@/components/dashboard/WeatherWidget";
import * as api from "@/lib/api";
import type {
  GetWeatherResponse,
  WeatherData,
  WeatherForecastHour,
} from "@/lib/types";

// Mock the API
jest.mock("@/lib/api");

const mockGetWeather = api.getWeather as jest.MockedFunction<
  typeof api.getWeather
>;

describe("WeatherWidget", () => {
  const mockForecast: WeatherForecastHour[] = [
    { time: "12PM", temperature: 22.5, weather_code: 1 },
    { time: "1PM", temperature: 23.0, weather_code: 1 },
    { time: "2PM", temperature: 24.5, weather_code: 2 },
    { time: "3PM", temperature: 25.0, weather_code: 2 },
    { time: "4PM", temperature: 24.0, weather_code: 3 },
    { time: "5PM", temperature: 23.5, weather_code: 3 },
    { time: "6PM", temperature: 22.0, weather_code: 61 },
    { time: "7PM", temperature: 21.0, weather_code: 61 },
    { time: "8PM", temperature: 20.5, weather_code: 63 },
    { time: "9PM", temperature: 19.5, weather_code: 63 },
    { time: "10PM", temperature: 19.0, weather_code: 45 },
    { time: "11PM", temperature: 18.5, weather_code: 45 },
  ];

  const mockWeatherData: WeatherData = {
    location_name: "Test Location",
    temperature: 22.5,
    weather_code: 1,
    high: 25.0,
    low: 17.5,
    humidity: 65,
    wind_speed: 12.5,
    forecast: mockForecast,
  };

  const mockWeatherResponse: GetWeatherResponse = {
    message: "Retrieved weather successfully",
    timestamp: "2024-01-01T00:00:00Z",
    weather: mockWeatherData,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("should render loading state initially", () => {
    mockGetWeather.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<WeatherWidget />);

    expect(screen.getByText("WEATHER")).toBeInTheDocument();
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should render weather data successfully", async () => {
    mockGetWeather.mockResolvedValue(mockWeatherResponse);

    render(<WeatherWidget />);

    await waitFor(() => {
      expect(screen.getByText("WEATHER")).toBeInTheDocument();
      expect(screen.getByText("Test Location")).toBeInTheDocument();
    });

    // Check current weather display
    expect(screen.getByText("22.5°C")).toBeInTheDocument();
    expect(screen.getByText("Mainly clear")).toBeInTheDocument();
    // Emoji appears in both main display and forecast, so use getAllByText
    const emojis = screen.getAllByText("🌤️");
    expect(emojis.length).toBeGreaterThanOrEqual(1);

    // Check high/low temperatures
    expect(screen.getByText("High:")).toBeInTheDocument();
    expect(screen.getByText("25°C")).toBeInTheDocument();
    expect(screen.getByText("Low:")).toBeInTheDocument();
    expect(screen.getByText("17.5°C")).toBeInTheDocument();

    // Check humidity and wind
    expect(screen.getByText("Humidity:")).toBeInTheDocument();
    expect(screen.getByText("65%")).toBeInTheDocument();
    expect(screen.getByText("Wind:")).toBeInTheDocument();
    expect(screen.getByText("12.5 km/h")).toBeInTheDocument();

    // Check forecast header
    expect(screen.getByText("12-HOUR FORECAST")).toBeInTheDocument();
  });

  it("should render error state when fetch fails", async () => {
    const errorMessage = "Failed to fetch weather";
    mockGetWeather.mockRejectedValue(new Error(errorMessage));

    render(<WeatherWidget />);

    await waitFor(() => {
      expect(screen.getByText("WEATHER")).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it("should display correct weather code mappings", async () => {
    const testCases = [
      { code: 0, emoji: "☀️", description: "Clear sky" },
      { code: 2, emoji: "⛅", description: "Partly cloudy" },
      { code: 61, emoji: "🌦️", description: "Light rain" },
      { code: 95, emoji: "⛈️", description: "Thunderstorm" },
    ];

    for (const testCase of testCases) {
      const weatherData = {
        ...mockWeatherData,
        weather_code: testCase.code,
      };
      mockGetWeather.mockResolvedValue({
        ...mockWeatherResponse,
        weather: weatherData,
      });

      const { unmount } = render(<WeatherWidget />);

      await waitFor(() => {
        // Emoji may appear multiple times (main display + forecast)
        const emojis = screen.getAllByText(testCase.emoji);
        expect(emojis.length).toBeGreaterThanOrEqual(1);
        expect(screen.getByText(testCase.description)).toBeInTheDocument();
      });

      unmount();
    }
  });

  it("should display every 3rd hour from forecast (4 slots)", async () => {
    mockGetWeather.mockResolvedValue(mockWeatherResponse);

    render(<WeatherWidget />);

    await waitFor(() => {
      expect(screen.getByText("Test Location")).toBeInTheDocument();
    });

    // Should display hours at indices 0, 3, 6, 9
    expect(screen.getByText("12PM")).toBeInTheDocument();
    expect(screen.getByText("3PM")).toBeInTheDocument();
    expect(screen.getByText("6PM")).toBeInTheDocument();
    expect(screen.getByText("9PM")).toBeInTheDocument();

    // Should display corresponding temperatures (without degree symbol in forecast)
    expect(screen.getByText("22.5°")).toBeInTheDocument();
    expect(screen.getByText("25°")).toBeInTheDocument();
    expect(screen.getByText("22°")).toBeInTheDocument();
    expect(screen.getByText("19.5°")).toBeInTheDocument();

    // Should NOT display other hours
    expect(screen.queryByText("1PM")).not.toBeInTheDocument();
    expect(screen.queryByText("2PM")).not.toBeInTheDocument();
  });

  it("should refresh weather every 30 minutes", async () => {
    mockGetWeather.mockResolvedValue(mockWeatherResponse);

    render(<WeatherWidget />);

    await waitFor(() => {
      expect(mockGetWeather).toHaveBeenCalledTimes(1);
    });

    // Fast-forward 30 minutes
    await act(async () => {
      jest.advanceTimersByTime(30 * 60 * 1000);
    });

    await waitFor(() => {
      expect(mockGetWeather).toHaveBeenCalledTimes(2);
    });

    // Fast-forward another 30 minutes
    await act(async () => {
      jest.advanceTimersByTime(30 * 60 * 1000);
    });

    await waitFor(() => {
      expect(mockGetWeather).toHaveBeenCalledTimes(3);
    });
  });

  it("should clean up interval on unmount", async () => {
    mockGetWeather.mockResolvedValue(mockWeatherResponse);

    const { unmount } = render(<WeatherWidget />);

    await waitFor(() => {
      expect(mockGetWeather).toHaveBeenCalledTimes(1);
    });

    unmount();

    // Fast-forward time after unmount
    jest.advanceTimersByTime(30 * 60 * 1000);

    // Should not call again after unmount
    expect(mockGetWeather).toHaveBeenCalledTimes(1);
  });

  it("should handle unknown weather codes gracefully", async () => {
    const weatherData = {
      ...mockWeatherData,
      weather_code: 9999, // Invalid code
    };
    mockGetWeather.mockResolvedValue({
      ...mockWeatherResponse,
      weather: weatherData,
    });

    render(<WeatherWidget />);

    await waitFor(() => {
      expect(screen.getByText("❓")).toBeInTheDocument();
      expect(screen.getByText("Unknown")).toBeInTheDocument();
    });
  });

  it("should display null weather as error state", async () => {
    mockGetWeather.mockResolvedValue({
      ...mockWeatherResponse,
      weather: null as unknown as WeatherData,
    });

    render(<WeatherWidget />);

    await waitFor(() => {
      expect(screen.getByText("No weather data available")).toBeInTheDocument();
    });
  });

  it("should display forecast weather code emojis correctly", async () => {
    mockGetWeather.mockResolvedValue(mockWeatherResponse);

    render(<WeatherWidget />);

    await waitFor(() => {
      expect(screen.getByText("Test Location")).toBeInTheDocument();
    });

    // The forecast should show emojis for indices 0, 3, 6, 9
    // index 0: code 1 = 🌤️
    // index 3: code 2 = ⛅
    // index 6: code 61 = 🌦️
    // index 9: code 63 = 🌧️

    const emojis = screen.getAllByText(/[🌤️⛅🌦️🌧️]/);
    // Should have at least 4 forecast emojis + 1 current weather emoji
    expect(emojis.length).toBeGreaterThanOrEqual(4);
  });
});
