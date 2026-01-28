import {
  act,
  render,
  screen,
  waitFor,
  fireEvent,
} from "@testing-library/react";

import ContainerWidget from "@/components/dashboard/ContainerWidget";
import * as api from "@/lib/api";
import type {
  GetContainersResponse,
  DockerContainer,
  ContainerActionResponse,
} from "@/lib/types";

// Mock the API
jest.mock("@/lib/api");

const mockGetContainers = api.getContainers as jest.MockedFunction<
  typeof api.getContainers
>;
const mockRefreshContainers = api.refreshContainers as jest.MockedFunction<
  typeof api.refreshContainers
>;
const mockStartContainer = api.startContainer as jest.MockedFunction<
  typeof api.startContainer
>;
const mockStopContainer = api.stopContainer as jest.MockedFunction<
  typeof api.stopContainer
>;
const mockRestartContainer = api.restartContainer as jest.MockedFunction<
  typeof api.restartContainer
>;
const mockUpdateContainer = api.updateContainer as jest.MockedFunction<
  typeof api.updateContainer
>;

describe("ContainerWidget", () => {
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
    {
      container_id: "ghi789",
      name: "plex",
      image: "plexinc/pms-docker:latest",
      status: "exited",
      port: "32400",
    },
  ];

  const mockContainersResponse: GetContainersResponse = {
    message: "Retrieved containers successfully",
    timestamp: "2024-01-01T00:00:00Z",
    containers: mockContainers,
  };

  const mockActionResponse: ContainerActionResponse = {
    message: "Action completed successfully",
    timestamp: "2024-01-01T00:00:00Z",
    container_id: "abc123",
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("should render loading state initially", () => {
    mockGetContainers.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<ContainerWidget />);

    expect(screen.getByText("CONTAINERS")).toBeInTheDocument();
    expect(screen.getByText("Loading containers...")).toBeInTheDocument();
  });

  it("should render containers successfully", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
      expect(screen.getByText("homebridge")).toBeInTheDocument();
      expect(screen.getByText("plex")).toBeInTheDocument();
    });

    expect(mockGetContainers).toHaveBeenCalledTimes(1);
  });

  it("should sort containers with running first, then by port ascending", async () => {
    const unsortedContainers: DockerContainer[] = [
      {
        container_id: "3",
        name: "container-c",
        image: "image-c:latest",
        status: "exited",
        port: "8080",
      },
      {
        container_id: "2",
        name: "container-b",
        image: "image-b:latest",
        status: "running",
        port: "9000",
      },
      {
        container_id: "1",
        name: "container-a",
        image: "image-a:latest",
        status: "running",
        port: "443",
      },
    ];

    mockGetContainers.mockResolvedValue({
      ...mockContainersResponse,
      containers: unsortedContainers,
    });

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("container-a")).toBeInTheDocument();
    });

    // Get all container cards in order
    const containerNames = screen
      .getAllByRole("heading", { level: 3 })
      .map(el => el.textContent);

    // Should be sorted: running first (by port), then exited
    expect(containerNames[0]).toContain("container-a"); // Running, port 443
    expect(containerNames[1]).toContain("container-b"); // Running, port 9000
    expect(containerNames[2]).toContain("container-c"); // Exited, port 8080
  });

  it("should sort containers without ports to the end", async () => {
    const containersWithoutPorts: DockerContainer[] = [
      {
        container_id: "1",
        name: "no-ports",
        image: "image:latest",
        status: "running",
        port: null,
      },
      {
        container_id: "2",
        name: "with-ports",
        image: "image:latest",
        status: "running",
        port: "8080",
      },
    ];

    mockGetContainers.mockResolvedValue({
      ...mockContainersResponse,
      containers: containersWithoutPorts,
    });

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("with-ports")).toBeInTheDocument();
    });

    const containerNames = screen
      .getAllByRole("heading", { level: 3 })
      .map(el => el.textContent);

    // Container with port should come first
    expect(containerNames[0]).toContain("with-ports");
    expect(containerNames[1]).toContain("no-ports");
  });

  it("should display error message on fetch failure", async () => {
    mockGetContainers.mockRejectedValue(new Error("Network error"));

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
  });

  it("should display 'No containers found' when empty", async () => {
    mockGetContainers.mockResolvedValue({
      ...mockContainersResponse,
      containers: [],
    });

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("No containers found")).toBeInTheDocument();
    });
  });

  it("should call startContainer when start button is clicked", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);
    mockStartContainer.mockResolvedValue(mockActionResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("plex")).toBeInTheDocument();
    });

    // Find all start buttons and click the one for the stopped container (plex)
    const startButtons = screen.getAllByTitle("Start");
    const plexStartButton = startButtons.find(
      btn => !btn.hasAttribute("disabled")
    );

    if (plexStartButton) {
      fireEvent.click(plexStartButton);
    }

    await waitFor(() => {
      expect(mockStartContainer).toHaveBeenCalledWith("ghi789");
      expect(mockGetContainers).toHaveBeenCalledTimes(2); // Initial load + reload after start
    });
  });

  it("should call stopContainer when stop button is clicked", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);
    mockStopContainer.mockResolvedValue(mockActionResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
    });

    // Find all stop buttons and click the first enabled one
    const stopButtons = screen.getAllByTitle("Stop");
    const enabledStopButton = stopButtons.find(
      btn => !btn.hasAttribute("disabled")
    );

    if (enabledStopButton) {
      fireEvent.click(enabledStopButton);
    }

    await waitFor(() => {
      expect(mockStopContainer).toHaveBeenCalledWith("abc123");
      expect(mockGetContainers).toHaveBeenCalledTimes(2);
    });
  });

  it("should call restartContainer when restart button is clicked", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);
    mockRestartContainer.mockResolvedValue(mockActionResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
    });

    const restartButtons = screen.getAllByTitle("Restart");
    const enabledRestartButton = restartButtons.find(
      btn => !btn.hasAttribute("disabled")
    );

    if (enabledRestartButton) {
      fireEvent.click(enabledRestartButton);
    }

    await waitFor(() => {
      expect(mockRestartContainer).toHaveBeenCalledWith("abc123");
      expect(mockGetContainers).toHaveBeenCalledTimes(2);
    });
  });

  it("should call updateContainer when update button is clicked", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);
    mockUpdateContainer.mockResolvedValue(mockActionResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
    });

    const updateButtons = screen.getAllByTitle("Update");
    if (updateButtons[0]) {
      fireEvent.click(updateButtons[0]);
    }

    await waitFor(() => {
      expect(mockUpdateContainer).toHaveBeenCalledWith("abc123");
      expect(mockGetContainers).toHaveBeenCalledTimes(2);
    });
  });

  it("should refresh containers when refresh button is clicked", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);
    mockRefreshContainers.mockResolvedValue(mockContainersResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
    });

    const refreshButton = screen.getByTitle("Refresh containers");
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockRefreshContainers).toHaveBeenCalledTimes(1);
    });
  });

  it("should disable refresh button while loading", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);
    mockRefreshContainers.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
    });

    const refreshButton = screen.getByTitle("Refresh containers");
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(refreshButton).toBeDisabled();
    });
  });

  it("should refresh containers every 30 seconds", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(mockGetContainers).toHaveBeenCalledTimes(1);
    });

    // Fast-forward 30 seconds
    act(() => {
      jest.advanceTimersByTime(30000);
    });

    await waitFor(() => {
      expect(mockGetContainers).toHaveBeenCalledTimes(2);
    });

    // Fast-forward another 30 seconds
    act(() => {
      jest.advanceTimersByTime(30000);
    });

    await waitFor(() => {
      expect(mockGetContainers).toHaveBeenCalledTimes(3);
    });
  });

  it("should render container cards with correct props", async () => {
    mockGetContainers.mockResolvedValue(mockContainersResponse);

    render(<ContainerWidget />);

    await waitFor(() => {
      expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
    });

    // Verify container images are displayed
    expect(
      screen.getByText("ghcr.io/user/pi-dashboard:latest")
    ).toBeInTheDocument();
    expect(
      screen.getByText("homebridge/homebridge:latest")
    ).toBeInTheDocument();
    expect(screen.getByText("plexinc/pms-docker:latest")).toBeInTheDocument();

    // Verify ports are displayed
    expect(screen.getByText("Port: 443")).toBeInTheDocument();
    expect(screen.getByText("Port: 8581")).toBeInTheDocument();
    expect(screen.getByText("Port: 32400")).toBeInTheDocument();
  });
});
