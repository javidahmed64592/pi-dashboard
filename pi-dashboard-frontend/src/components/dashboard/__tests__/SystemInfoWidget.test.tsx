import { render, screen } from "@testing-library/react";

import SystemInfoWidget from "@/components/dashboard/SystemInfoWidget";
import { useSystem } from "@/contexts/SystemContext";

// Mock the SystemContext
jest.mock("../../../contexts/SystemContext", () => ({
  useSystem: jest.fn(),
}));

const mockUseSystem = useSystem as jest.MockedFunction<typeof useSystem>;

describe("SystemInfoWidget", () => {
  const mockSystemInfo = {
    hostname: "raspberrypi",
    system: "Linux",
    release: "6.1.0-rpi4-rpi-v8",
    version: "#1 SMP PREEMPT Debian 1:6.1.0-1 (2023-01-01)",
    machine: "aarch64",
    memory_total: 8.0,
    disk_total: 128.0,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders system information title", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<SystemInfoWidget />);

    expect(screen.getByText("SYSTEM INFO")).toBeInTheDocument();
  });

  it("displays all system fields correctly", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<SystemInfoWidget />);

    expect(screen.getByText("System:")).toBeInTheDocument();
    expect(screen.getByText("Linux")).toBeInTheDocument();

    expect(screen.getByText("Release:")).toBeInTheDocument();
    expect(screen.getByText("6.1.0-rpi4-rpi-v8")).toBeInTheDocument();

    expect(screen.getByText("Version:")).toBeInTheDocument();
    expect(
      screen.getByText("#1 SMP PREEMPT Debian 1:6.1.0-1 (2023-01-01)")
    ).toBeInTheDocument();

    expect(screen.getByText("Machine:")).toBeInTheDocument();
    expect(screen.getByText("aarch64")).toBeInTheDocument();
  });

  it("shows loading state when system info is not available", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: null,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: true,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<SystemInfoWidget />);

    expect(
      screen.getByText("Loading system information...")
    ).toBeInTheDocument();
  });

  it("shows loading message when error occurs", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: null,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: "Failed to fetch system info",
      refreshHistory: jest.fn(),
    });

    render(<SystemInfoWidget />);

    // Component doesn't show error message, just loading state
    expect(
      screen.getByText("Loading system information...")
    ).toBeInTheDocument();
  });

  it("applies correct styling classes", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<SystemInfoWidget />);

    // Check for card styling
    const card = container.querySelector(
      ".bg-background-secondary.border.border-border"
    );
    expect(card).toBeInTheDocument();

    // Check for rounded corners
    expect(card).toHaveClass("rounded-lg");

    // Check for shadow effect
    expect(card).toHaveClass("shadow-neon");
  });

  it("uses monospace font for all text", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<SystemInfoWidget />);

    const monoElements = container.querySelectorAll(".font-mono");
    expect(monoElements.length).toBeGreaterThan(0);
  });

  it("renders field labels with correct styling", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<SystemInfoWidget />);

    const labels = ["System:", "Release:", "Version:", "Machine:"];

    labels.forEach(label => {
      const labelElement = screen.getByText(label);
      expect(labelElement).toHaveClass("text-text-muted");
    });
  });

  it("renders field values with correct styling", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<SystemInfoWidget />);

    const linuxValue = screen.getByText("Linux");
    expect(linuxValue).toHaveClass("text-text-primary");
  });

  it("uses space-y layout for fields", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<SystemInfoWidget />);

    const layout = container.querySelector(".space-y-2");
    expect(layout).toBeInTheDocument();
  });

  it("handles missing individual fields gracefully", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: {
        ...mockSystemInfo,
        release: "",
        machine: "",
      },
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<SystemInfoWidget />);

    // Should still render labels
    expect(screen.getByText("Release:")).toBeInTheDocument();
    expect(screen.getByText("Machine:")).toBeInTheDocument();
  });

  it("applies padding and spacing correctly", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<SystemInfoWidget />);

    const card = container.querySelector(".p-4");
    expect(card).toBeInTheDocument();

    const layout = container.querySelector(".space-y-2");
    expect(layout).toBeInTheDocument();
  });

  it("has consistent border styling with other dashboard widgets", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<SystemInfoWidget />);

    const card = container.firstChild;
    expect(card).toHaveClass("border-border");
  });
});
