/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor } from "@testing-library/react";

import * as api from "@/lib/api";

import { SystemProvider, useSystem } from "../SystemContext";

// Mock the API module
jest.mock("@/lib/api");

const mockSystemInfo = {
  hostname: "test-host",
  system: "Linux",
  release: "5.10.0",
  version: "test-version",
  machine: "x86_64",
  memory_total: 16.0,
  disk_total: 512.0,
};

const mockSystemMetrics = {
  cpu_usage: 25.5,
  memory_usage: 60.2,
  disk_usage: 45.8,
  uptime: 86400,
  temperature: 42.5,
};

const mockMetricsHistory = {
  history: [
    {
      metrics: mockSystemMetrics,
      timestamp: 1640000000,
    },
  ],
};

describe("SystemContext", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("fetches system info on mount", async () => {
    (api.getSystemInfo as jest.Mock).mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2024-01-01T00:00:00Z",
      info: mockSystemInfo,
    });

    (api.getSystemMetrics as jest.Mock).mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2024-01-01T00:00:00Z",
      metrics: mockSystemMetrics,
    });

    const TestComponent = () => {
      const { systemInfo, isLoading } = useSystem();
      return (
        <div>
          {isLoading ? (
            <div>Loading...</div>
          ) : (
            <div>{systemInfo?.hostname}</div>
          )}
        </div>
      );
    };

    render(
      <SystemProvider>
        <TestComponent />
      </SystemProvider>
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("test-host")).toBeInTheDocument();
    });

    expect(api.getSystemInfo).toHaveBeenCalledTimes(1);
  });

  it("polls current metrics every 5 seconds", async () => {
    jest.useFakeTimers();

    (api.getSystemInfo as jest.Mock).mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2024-01-01T00:00:00Z",
      info: mockSystemInfo,
    });

    (api.getSystemMetrics as jest.Mock).mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2024-01-01T00:00:00Z",
      metrics: mockSystemMetrics,
    });

    const TestComponent = () => {
      const { currentMetrics } = useSystem();
      return <div>{currentMetrics?.cpu_usage}</div>;
    };

    render(
      <SystemProvider>
        <TestComponent />
      </SystemProvider>
    );

    await waitFor(() => {
      expect(api.getSystemMetrics).toHaveBeenCalledTimes(1);
    });

    // Fast-forward 5 seconds
    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(api.getSystemMetrics).toHaveBeenCalledTimes(2);
    });

    jest.useRealTimers();
  });

  it("refreshes history on demand", async () => {
    (api.getSystemInfo as jest.Mock).mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2024-01-01T00:00:00Z",
      info: mockSystemInfo,
    });

    (api.getSystemMetrics as jest.Mock).mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2024-01-01T00:00:00Z",
      metrics: mockSystemMetrics,
    });

    (api.getSystemMetricsHistory as jest.Mock).mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2024-01-01T00:00:00Z",
      history: mockMetricsHistory,
    });

    const TestComponent = () => {
      const { refreshHistory, metricsHistory } = useSystem();
      return (
        <div>
          <button onClick={() => refreshHistory(60)}>Refresh</button>
          <div>{metricsHistory?.history.length || 0}</div>
        </div>
      );
    };

    render(
      <SystemProvider>
        <TestComponent />
      </SystemProvider>
    );

    const button = screen.getByText("Refresh");
    button.click();

    await waitFor(() => {
      expect(api.getSystemMetricsHistory).toHaveBeenCalledWith({
        last_n_seconds: 60,
      });
      expect(screen.getByText("1")).toBeInTheDocument();
    });
  });

  it("handles errors gracefully", async () => {
    (api.getSystemInfo as jest.Mock).mockRejectedValue(
      new Error("Network error")
    );

    (api.getSystemMetrics as jest.Mock).mockRejectedValue(
      new Error("Metrics error")
    );

    const TestComponent = () => {
      const { error, isLoading } = useSystem();
      return (
        <div>
          {isLoading ? <div>Loading...</div> : <div>{error || "No error"}</div>}
        </div>
      );
    };

    render(
      <SystemProvider>
        <TestComponent />
      </SystemProvider>
    );

    await waitFor(() => {
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
      // Should show error from either system info or metrics
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
