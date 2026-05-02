import {
  act,
  render,
  screen,
  waitFor,
  fireEvent,
} from "@testing-library/react";

import LogsPanel from "@/components/dashboard/LogsPanel";
import * as api from "@/lib/api";
import type { ContainerLogsResponse, DockerLogSource } from "@/lib/types";

jest.mock("@/lib/api");

const mockGetContainerLogs = api.getContainerLogs as jest.MockedFunction<
  typeof api.getContainerLogs
>;

describe("LogsPanel", () => {
  const mockDockerSource: DockerLogSource = {
    type: "docker",
    containerId: "abc123",
    containerName: "pi-dashboard",
  };

  const mockLogsResponse: ContainerLogsResponse = {
    message: "Retrieved 3 log lines",
    timestamp: "2024-01-01T00:00:00Z",
    container_id: "abc123",
    logs: [
      "[INFO] Server started",
      "[INFO] Listening on :443",
      "[WARN] High memory usage",
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    mockGetContainerLogs.mockResolvedValue(mockLogsResponse);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("should render the panel header", () => {
    render(<LogsPanel source={null} />);
    expect(screen.getByText("Logs")).toBeInTheDocument();
  });

  it("should show placeholder text when no source is selected", () => {
    render(<LogsPanel source={null} />);
    expect(
      screen.getByText("Select a container to view logs.")
    ).toBeInTheDocument();
  });

  it("should disable the refresh button when no source is selected", () => {
    render(<LogsPanel source={null} />);
    expect(screen.getByRole("button", { name: "Refresh logs" })).toBeDisabled();
  });

  it("should display the source name in the header when a source is provided", async () => {
    render(<LogsPanel source={mockDockerSource} />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /pi-dashboard/i })
      ).toBeInTheDocument();
    });
  });

  it("should fetch and display logs when a source is provided", async () => {
    render(<LogsPanel source={mockDockerSource} />);

    await waitFor(() => {
      expect(screen.getByText("[INFO] Server started")).toBeInTheDocument();
      expect(screen.getByText("[INFO] Listening on :443")).toBeInTheDocument();
      expect(screen.getByText("[WARN] High memory usage")).toBeInTheDocument();
    });

    expect(mockGetContainerLogs).toHaveBeenCalledWith("abc123", 100);
  });

  it("should not fetch logs when source is null", async () => {
    render(<LogsPanel source={null} />);

    await act(async () => {
      jest.advanceTimersByTime(10_000);
    });

    expect(mockGetContainerLogs).not.toHaveBeenCalled();
  });

  it("should re-fetch logs when lines count changes", async () => {
    render(<LogsPanel source={mockDockerSource} />);

    await waitFor(() => {
      expect(mockGetContainerLogs).toHaveBeenCalledWith("abc123", 100);
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Show 250 lines" }));
    });

    await waitFor(() => {
      expect(mockGetContainerLogs).toHaveBeenCalledWith("abc123", 250);
    });
  });

  it("should trigger a manual refresh when the refresh button is clicked", async () => {
    render(<LogsPanel source={mockDockerSource} />);

    // Wait for the initial fetch to complete (button enabled, logs visible)
    await waitFor(() => {
      expect(screen.getByText("[INFO] Server started")).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Refresh logs" })
      ).not.toBeDisabled();
    });

    expect(mockGetContainerLogs).toHaveBeenCalledTimes(1);

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Refresh logs" }));
    });

    await waitFor(() => {
      expect(mockGetContainerLogs).toHaveBeenCalledTimes(2);
    });
  });

  it("should auto-refresh logs after the interval", async () => {
    render(<LogsPanel source={mockDockerSource} />);

    await waitFor(() => {
      expect(mockGetContainerLogs).toHaveBeenCalledTimes(1);
    });

    await act(async () => {
      jest.advanceTimersByTime(10_000);
    });

    await waitFor(() => {
      expect(mockGetContainerLogs).toHaveBeenCalledTimes(2);
    });
  });

  it("should fetch logs for the new source when source changes", async () => {
    const newSource: DockerLogSource = {
      type: "docker",
      containerId: "def456",
      containerName: "homebridge",
    };

    const newLogsResponse: ContainerLogsResponse = {
      ...mockLogsResponse,
      container_id: "def456",
      logs: ["[INFO] Homebridge started"],
    };

    const { rerender } = render(<LogsPanel source={mockDockerSource} />);

    await waitFor(() => {
      expect(mockGetContainerLogs).toHaveBeenCalledWith("abc123", 100);
    });

    mockGetContainerLogs.mockResolvedValue(newLogsResponse);
    rerender(<LogsPanel source={newSource} />);

    await waitFor(() => {
      expect(mockGetContainerLogs).toHaveBeenCalledWith("def456", 100);
      expect(screen.getByText("[INFO] Homebridge started")).toBeInTheDocument();
    });
  });

  it("should display an error message when fetching logs fails", async () => {
    mockGetContainerLogs.mockRejectedValue(new Error("Log fetch failed"));

    render(<LogsPanel source={mockDockerSource} />);

    await waitFor(() => {
      expect(screen.getByText("Log fetch failed")).toBeInTheDocument();
    });
  });

  it("should show 'No log output' when logs array is empty", async () => {
    mockGetContainerLogs.mockResolvedValue({ ...mockLogsResponse, logs: [] });

    render(<LogsPanel source={mockDockerSource} />);

    await waitFor(() => {
      expect(screen.getByText("No log output.")).toBeInTheDocument();
    });
  });
});
