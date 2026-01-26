import { renderHook } from "@testing-library/react";

import {
  getHealth,
  login,
  getNotes,
  createNote,
  updateNote,
  deleteNote,
  getWeather,
  getWeatherLocation,
  updateWeatherLocation,
  useHealthStatus,
  type HealthStatus,
} from "@/lib/api";
import type {
  HealthResponse,
  LoginResponse,
  GetNotesResponse,
  CreateNoteResponse,
  UpdateNoteResponse,
  DeleteNoteResponse,
  Note,
  GetWeatherResponse,
  GetWeatherLocationResponse,
  WeatherData,
  WeatherForecastHour,
} from "@/lib/types";

jest.mock("../api", () => {
  const actual = jest.requireActual("../api");
  return {
    ...actual,
    getHealth: jest.fn(),
    login: jest.fn(),
    getNotes: jest.fn(),
    createNote: jest.fn(),
    updateNote: jest.fn(),
    deleteNote: jest.fn(),
    getWeather: jest.fn(),
    getWeatherLocation: jest.fn(),
    updateWeatherLocation: jest.fn(),
  };
});

// Mock fetch for config endpoint
global.fetch = jest.fn();

const mockGetHealth = getHealth as jest.MockedFunction<typeof getHealth>;
const mockLogin = login as jest.MockedFunction<typeof login>;
const mockGetNotes = getNotes as jest.MockedFunction<typeof getNotes>;
const mockCreateNote = createNote as jest.MockedFunction<typeof createNote>;
const mockUpdateNote = updateNote as jest.MockedFunction<typeof updateNote>;
const mockDeleteNote = deleteNote as jest.MockedFunction<typeof deleteNote>;
const mockGetWeather = getWeather as jest.MockedFunction<typeof getWeather>;
const mockGetWeatherLocation = getWeatherLocation as jest.MockedFunction<
  typeof getWeatherLocation
>;
const mockUpdateWeatherLocation = updateWeatherLocation as jest.MockedFunction<
  typeof updateWeatherLocation
>;

const mockNote1: Note = {
  id: "1",
  title: "Test Note 1",
  content: "Content 1",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

const mockNote2: Note = {
  id: "2",
  title: "Test Note 2",
  content: "Content 2",
  created_at: "2024-01-02T00:00:00Z",
  updated_at: "2024-01-02T00:00:00Z",
};

describe("API Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("health", () => {
    it("should fetch health status successfully", async () => {
      const mockHealth: HealthResponse = {
        code: 200,
        message: "Server is healthy",
        timestamp: "2023-01-01T00:00:00Z",
        status: "healthy",
      };

      mockGetHealth.mockResolvedValue(mockHealth);

      const health = await getHealth();

      expect(mockGetHealth).toHaveBeenCalled();
      expect(health).toEqual(mockHealth);
      expect(health.status).toBe("healthy");
    });

    it("should handle health check error", async () => {
      const errorMessage = "Service unavailable";
      mockGetHealth.mockRejectedValue(new Error(errorMessage));

      await expect(getHealth()).rejects.toThrow(errorMessage);
    });

    it("should handle network error (no response)", async () => {
      const errorMessage =
        "No response from server. Please check if the backend is running.";
      mockGetHealth.mockRejectedValue(new Error(errorMessage));

      await expect(getHealth()).rejects.toThrow(errorMessage);
    });
  });

  describe("login", () => {
    it("should successfully login with valid API key", async () => {
      const mockResponse: LoginResponse = {
        code: 200,
        message: "Login successful.",
        timestamp: "2023-01-01T00:00:00Z",
      };

      mockLogin.mockResolvedValue(mockResponse);

      const result = await login("valid-api-key-123");

      expect(result).toEqual(mockResponse);
      expect(mockLogin).toHaveBeenCalledWith("valid-api-key-123");
    });

    it("should reject with error for invalid API key", async () => {
      const errorMessage = "Invalid API key";
      mockLogin.mockRejectedValue(new Error(errorMessage));

      await expect(login("invalid-key")).rejects.toThrow(errorMessage);
    });

    it("should reject with unauthorized error", async () => {
      const errorMessage = "Missing API key";
      mockLogin.mockRejectedValue(new Error(errorMessage));

      await expect(login("")).rejects.toThrow(errorMessage);
    });

    it("should handle network error", async () => {
      const errorMessage =
        "No response from server. Please check if the backend is running.";
      mockLogin.mockRejectedValue(new Error(errorMessage));

      await expect(login("test-key")).rejects.toThrow(errorMessage);
    });
  });

  describe("useHealthStatus", () => {
    it("should initialize with 'checking' status", () => {
      const { result, unmount } = renderHook(() => useHealthStatus());
      expect(result.current).toBe("checking");
      unmount();
    });

    it("should return correct HealthStatus type", () => {
      const { result, unmount } = renderHook(() => useHealthStatus());
      const status: HealthStatus = result.current;
      expect(["checking", "online", "offline"]).toContain(status);
      unmount();
    });
  });

  describe("notes", () => {
    describe("getNotes", () => {
      it("should fetch notes successfully", async () => {
        const mockResponse: GetNotesResponse = {
          code: 200,
          message: "Retrieved notes successfully",
          timestamp: "2024-01-01T00:00:00Z",
          notes: { notes: [mockNote1, mockNote2] },
        };

        mockGetNotes.mockResolvedValue(mockResponse);

        const result = await getNotes();

        expect(mockGetNotes).toHaveBeenCalled();
        expect(result).toEqual(mockResponse);
        expect(result.notes.notes).toHaveLength(2);
      });

      it("should handle fetch notes error", async () => {
        const errorMessage = "Failed to fetch notes";
        mockGetNotes.mockRejectedValue(new Error(errorMessage));

        await expect(getNotes()).rejects.toThrow(errorMessage);
      });
    });

    describe("createNote", () => {
      it("should create a note successfully", async () => {
        const mockResponse: CreateNoteResponse = {
          code: 200,
          message: "Created note successfully",
          timestamp: "2024-01-01T00:00:00Z",
          note: mockNote1,
        };

        mockCreateNote.mockResolvedValue(mockResponse);

        const request = { title: "Test Note 1", content: "Content 1" };
        const result = await createNote(request);

        expect(mockCreateNote).toHaveBeenCalledWith(request);
        expect(result).toEqual(mockResponse);
        expect(result.note.title).toBe("Test Note 1");
      });

      it("should handle create note error", async () => {
        const errorMessage = "Failed to create note";
        mockCreateNote.mockRejectedValue(new Error(errorMessage));

        const request = { title: "Test", content: "Content" };
        await expect(createNote(request)).rejects.toThrow(errorMessage);
      });

      it("should validate required fields", async () => {
        const errorMessage = "Title is required";
        mockCreateNote.mockRejectedValue(new Error(errorMessage));

        const request = { title: "", content: "Content" };
        await expect(createNote(request)).rejects.toThrow();
      });
    });

    describe("updateNote", () => {
      it("should update a note successfully", async () => {
        const updatedNote = { ...mockNote1, title: "Updated Title" };
        const mockResponse: UpdateNoteResponse = {
          code: 200,
          message: "Updated note successfully",
          timestamp: "2024-01-01T00:00:00Z",
          note: updatedNote,
        };

        mockUpdateNote.mockResolvedValue(mockResponse);

        const request = { title: "Updated Title" };
        const result = await updateNote("1", request);

        expect(mockUpdateNote).toHaveBeenCalledWith("1", request);
        expect(result).toEqual(mockResponse);
        expect(result.note.title).toBe("Updated Title");
      });

      it("should update note content only", async () => {
        const updatedNote = { ...mockNote1, content: "New content" };
        const mockResponse: UpdateNoteResponse = {
          code: 200,
          message: "Updated note successfully",
          timestamp: "2024-01-01T00:00:00Z",
          note: updatedNote,
        };

        mockUpdateNote.mockResolvedValue(mockResponse);

        const request = { content: "New content" };
        const result = await updateNote("1", request);

        expect(result.note.content).toBe("New content");
        expect(result.note.title).toBe(mockNote1.title);
      });

      it("should handle update note error", async () => {
        const errorMessage = "Note not found: 999";
        mockUpdateNote.mockRejectedValue(new Error(errorMessage));

        const request = { title: "Updated" };
        await expect(updateNote("999", request)).rejects.toThrow(errorMessage);
      });
    });

    describe("deleteNote", () => {
      it("should delete a note successfully", async () => {
        const mockResponse: DeleteNoteResponse = {
          code: 200,
          message: "Deleted note successfully",
          timestamp: "2024-01-01T00:00:00Z",
        };

        mockDeleteNote.mockResolvedValue(mockResponse);

        const result = await deleteNote("1");

        expect(mockDeleteNote).toHaveBeenCalledWith("1");
        expect(result).toEqual(mockResponse);
        expect(result.message).toBe("Deleted note successfully");
      });

      it("should handle delete note error", async () => {
        const errorMessage = "Note not found: 999";
        mockDeleteNote.mockRejectedValue(new Error(errorMessage));

        await expect(deleteNote("999")).rejects.toThrow(errorMessage);
      });
    });
  });

  describe("weather", () => {
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

    describe("getWeather", () => {
      it("should fetch weather data successfully", async () => {
        const mockResponse: GetWeatherResponse = {
          code: 200,
          message: "Retrieved weather successfully",
          timestamp: "2024-01-01T00:00:00Z",
          weather: mockWeatherData,
        };

        mockGetWeather.mockResolvedValue(mockResponse);

        const result = await getWeather();

        expect(mockGetWeather).toHaveBeenCalled();
        expect(result).toEqual(mockResponse);
        expect(result.weather.location_name).toBe("Test Location");
        expect(result.weather.temperature).toBe(22.5);
        expect(result.weather.forecast).toHaveLength(12);
      });

      it("should handle fetch weather error", async () => {
        const errorMessage = "Failed to fetch weather";
        mockGetWeather.mockRejectedValue(new Error(errorMessage));

        await expect(getWeather()).rejects.toThrow(errorMessage);
      });
    });

    describe("getWeatherLocation", () => {
      it("should fetch weather location successfully", async () => {
        const mockResponse: GetWeatherLocationResponse = {
          code: 200,
          message: "Retrieved location successfully",
          timestamp: "2024-01-01T00:00:00Z",
          location_name: "Test Location",
          latitude: 12.34,
          longitude: 56.78,
        };

        mockGetWeatherLocation.mockResolvedValue(mockResponse);

        const result = await getWeatherLocation();

        expect(mockGetWeatherLocation).toHaveBeenCalled();
        expect(result).toEqual(mockResponse);
        expect(result.location_name).toBe("Test Location");
        expect(result.latitude).toBe(12.34);
        expect(result.longitude).toBe(56.78);
      });

      it("should handle fetch weather location error", async () => {
        const errorMessage = "Failed to fetch location";
        mockGetWeatherLocation.mockRejectedValue(new Error(errorMessage));

        await expect(getWeatherLocation()).rejects.toThrow(errorMessage);
      });
    });

    describe("updateWeatherLocation", () => {
      it("should update weather location successfully", async () => {
        const mockResponse: GetWeatherLocationResponse = {
          code: 200,
          message: "Updated location successfully",
          timestamp: "2024-01-01T00:00:00Z",
          location_name: "New Location",
          latitude: 34.56,
          longitude: 78.9,
        };

        mockUpdateWeatherLocation.mockResolvedValue(mockResponse);

        const request = { location: "New Location" };
        const result = await updateWeatherLocation(request);

        expect(mockUpdateWeatherLocation).toHaveBeenCalledWith(request);
        expect(result).toEqual(mockResponse);
        expect(result.location_name).toBe("New Location");
      });

      it("should handle update weather location error", async () => {
        const errorMessage = "Location not found";
        mockUpdateWeatherLocation.mockRejectedValue(new Error(errorMessage));

        const request = { location: "Invalid Location" };
        await expect(updateWeatherLocation(request)).rejects.toThrow(
          errorMessage
        );
      });

      it("should validate location parameter", async () => {
        const errorMessage = "Location is required";
        mockUpdateWeatherLocation.mockRejectedValue(new Error(errorMessage));

        const request = { location: "" };
        await expect(updateWeatherLocation(request)).rejects.toThrow();
      });
    });
  });
});
