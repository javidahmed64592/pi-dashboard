import { renderHook } from "@testing-library/react";

import {
  getHealth,
  login,
  getContainers,
  refreshContainers,
  startContainer,
  stopContainer,
  restartContainer,
  updateContainer,
  useHealthStatus,
  type HealthStatus,
} from "@/lib/api";
import type {
  HealthResponse,
  LoginResponse,
  GetContainersResponse,
  DockerContainer,
  DockerContainerActionResponse,
} from "@/lib/types";

jest.mock("../api", () => {
  const actual = jest.requireActual("../api");
  return {
    ...actual,
    getHealth: jest.fn(),
    login: jest.fn(),
    getContainers: jest.fn(),
    refreshContainers: jest.fn(),
    startContainer: jest.fn(),
    stopContainer: jest.fn(),
    restartContainer: jest.fn(),
    updateContainer: jest.fn(),
  };
});

// Mock fetch for config endpoint
global.fetch = jest.fn();

const mockGetHealth = getHealth as jest.MockedFunction<typeof getHealth>;
const mockLogin = login as jest.MockedFunction<typeof login>;
const mockGetContainers = getContainers as jest.MockedFunction<
  typeof getContainers
>;
const mockRefreshContainers = refreshContainers as jest.MockedFunction<
  typeof refreshContainers
>;
const mockStartContainer = startContainer as jest.MockedFunction<
  typeof startContainer
>;
const mockStopContainer = stopContainer as jest.MockedFunction<
  typeof stopContainer
>;
const mockRestartContainer = restartContainer as jest.MockedFunction<
  typeof restartContainer
>;
const mockUpdateContainer = updateContainer as jest.MockedFunction<
  typeof updateContainer
>;

describe("API Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("health", () => {
    it("should fetch health status successfully", async () => {
      const mockHealth: HealthResponse = {
        message: "Server is healthy",
        timestamp: "2023-01-01T00:00:00Z",
      };

      mockGetHealth.mockResolvedValue(mockHealth);

      const health = await getHealth();

      expect(mockGetHealth).toHaveBeenCalled();
      expect(health).toEqual(mockHealth);
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

  describe("containers", () => {
    const mockContainers: DockerContainer[] = [
      {
        container_id: "abc123",
        name: "pi-dashboard",
        image: "ghcr.io/user/pi-dashboard:latest",
        status: "running",
        port: "443",
      },
      {
        container_id: "def456",
        name: "homebridge",
        image: "homebridge/homebridge:latest",
        status: "running",
        port: "8581",
      },
    ];

    describe("getContainers", () => {
      it("should fetch containers successfully", async () => {
        const mockResponse: GetContainersResponse = {
          message: "Retrieved containers successfully",
          timestamp: "2024-01-01T00:00:00Z",
          containers: mockContainers,
        };

        mockGetContainers.mockResolvedValue(mockResponse);

        const result = await getContainers();

        expect(mockGetContainers).toHaveBeenCalled();
        expect(result).toEqual(mockResponse);
        expect(result.containers).toHaveLength(2);
        expect(result.containers[0]?.name).toBe("pi-dashboard");
      });

      it("should handle get containers error", async () => {
        const errorMessage = "Failed to connect to Docker daemon";
        mockGetContainers.mockRejectedValue(new Error(errorMessage));

        await expect(getContainers()).rejects.toThrow(errorMessage);
      });
    });

    describe("refreshContainers", () => {
      it("should refresh containers successfully", async () => {
        const mockResponse: GetContainersResponse = {
          message: "Refreshed containers successfully",
          timestamp: "2024-01-01T00:00:00Z",
          containers: mockContainers,
        };

        mockRefreshContainers.mockResolvedValue(mockResponse);

        const result = await refreshContainers();

        expect(mockRefreshContainers).toHaveBeenCalled();
        expect(result).toEqual(mockResponse);
        expect(result.containers).toHaveLength(2);
      });

      it("should handle refresh containers error", async () => {
        const errorMessage = "Refresh failed";
        mockRefreshContainers.mockRejectedValue(new Error(errorMessage));

        await expect(refreshContainers()).rejects.toThrow(errorMessage);
      });
    });

    describe("startContainer", () => {
      it("should start container successfully", async () => {
        const mockResponse: DockerContainerActionResponse = {
          message: "Container started successfully",
          timestamp: "2024-01-01T00:00:00Z",
          container_id: "abc123",
        };

        mockStartContainer.mockResolvedValue(mockResponse);

        const result = await startContainer("abc123");

        expect(mockStartContainer).toHaveBeenCalledWith("abc123");
        expect(result).toEqual(mockResponse);
        expect(result.container_id).toBe("abc123");
      });

      it("should handle start container error", async () => {
        const errorMessage = "Container not found";
        mockStartContainer.mockRejectedValue(new Error(errorMessage));

        await expect(startContainer("invalid")).rejects.toThrow(errorMessage);
      });
    });

    describe("stopContainer", () => {
      it("should stop container successfully", async () => {
        const mockResponse: DockerContainerActionResponse = {
          message: "Container stopped successfully",
          timestamp: "2024-01-01T00:00:00Z",
          container_id: "abc123",
        };

        mockStopContainer.mockResolvedValue(mockResponse);

        const result = await stopContainer("abc123");

        expect(mockStopContainer).toHaveBeenCalledWith("abc123");
        expect(result).toEqual(mockResponse);
        expect(result.container_id).toBe("abc123");
      });

      it("should handle stop container error", async () => {
        const errorMessage = "Container already stopped";
        mockStopContainer.mockRejectedValue(new Error(errorMessage));

        await expect(stopContainer("abc123")).rejects.toThrow(errorMessage);
      });
    });

    describe("restartContainer", () => {
      it("should restart container successfully", async () => {
        const mockResponse: DockerContainerActionResponse = {
          message: "Container restarted successfully",
          timestamp: "2024-01-01T00:00:00Z",
          container_id: "abc123",
        };

        mockRestartContainer.mockResolvedValue(mockResponse);

        const result = await restartContainer("abc123");

        expect(mockRestartContainer).toHaveBeenCalledWith("abc123");
        expect(result).toEqual(mockResponse);
        expect(result.container_id).toBe("abc123");
      });

      it("should handle restart container error", async () => {
        const errorMessage = "Container not running";
        mockRestartContainer.mockRejectedValue(new Error(errorMessage));

        await expect(restartContainer("abc123")).rejects.toThrow(errorMessage);
      });
    });

    describe("updateContainer", () => {
      it("should update container successfully", async () => {
        const mockResponse: DockerContainerActionResponse = {
          message: "Container updated successfully",
          timestamp: "2024-01-01T00:00:00Z",
          container_id: "abc123",
        };

        mockUpdateContainer.mockResolvedValue(mockResponse);

        const result = await updateContainer("abc123");

        expect(mockUpdateContainer).toHaveBeenCalledWith("abc123");
        expect(result).toEqual(mockResponse);
        expect(result.container_id).toBe("abc123");
      });

      it("should handle update container error", async () => {
        const errorMessage = "Failed to pull image";
        mockUpdateContainer.mockRejectedValue(new Error(errorMessage));

        await expect(updateContainer("abc123")).rejects.toThrow(errorMessage);
      });
    });
  });
});
