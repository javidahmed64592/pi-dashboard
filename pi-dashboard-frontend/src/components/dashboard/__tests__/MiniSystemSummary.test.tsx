import { render, screen } from "@testing-library/react";

import MiniSystemSummary from "@/components/dashboard/MiniSystemSummary";
import { useSystem } from "@/contexts/SystemContext";

// Mock the SystemContext
jest.mock("../../../contexts/SystemContext", () => ({
  useSystem: jest.fn(),
}));

const mockUseSystem = useSystem as jest.MockedFunction<typeof useSystem>;

describe("MiniSystemSummary", () => {
  const mockSystemInfo = {
    hostname: "raspberrypi",
    system: "Linux",
    release: "6.1.0-rpi4-rpi-v8",
    version: "#1 SMP PREEMPT Debian 1:6.1.0-1 (2023-01-01)",
    machine: "aarch64",
    memory_total: 8.0,
    disk_total: 128.0,
  };

  const mockCurrentMetrics = {
    cpu_usage: 25.5,
    memory_usage: 50.0,
    disk_usage: 50.0,
    uptime: 86400,
    temperature: 45.2,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders all four metric cards", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<MiniSystemSummary />);

    expect(screen.getByText("CPU")).toBeInTheDocument();
    expect(screen.getByText("MEMORY")).toBeInTheDocument();
    expect(screen.getByText("DISK")).toBeInTheDocument();
    expect(screen.getByText("TEMP")).toBeInTheDocument();
  });

  it("displays CPU load percentage correctly", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<MiniSystemSummary />);

    expect(screen.getByText("25.5%")).toBeInTheDocument();
  });

  it("displays CPU temperature correctly", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<MiniSystemSummary />);

    expect(screen.getByText("45.2°C")).toBeInTheDocument();
  });

  it("displays memory usage correctly", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<MiniSystemSummary />);

    // Check for MEMORY label to identify the right card
    expect(screen.getByText("MEMORY")).toBeInTheDocument();
    expect(screen.getByText("(8.0GB)")).toBeInTheDocument();
  });

  it("displays disk usage correctly", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<MiniSystemSummary />);

    // Check for DISK label to identify the right card
    expect(screen.getByText("DISK")).toBeInTheDocument();
    expect(screen.getByText("(128.0GB)")).toBeInTheDocument();
  });

  it("shows loading state when metrics are not available", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: null,
      metricsHistory: null,
      isLoading: true,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<MiniSystemSummary />);

    const loadingTexts = screen.getAllByText("--");
    expect(loadingTexts.length).toBeGreaterThan(0);
  });

  describe("Threshold colors", () => {
    it("applies green color for low CPU usage", () => {
      mockUseSystem.mockReturnValue({
        systemInfo: mockSystemInfo,
        currentMetrics: { ...mockCurrentMetrics, cpu_usage: 20 },
        metricsHistory: null,
        isLoading: false,
        error: null,
        refreshHistory: jest.fn(),
      });

      const { container } = render(<MiniSystemSummary />);

      // Low threshold (<30) should use green color
      expect(container.innerHTML).toContain("#00ff41");
    });

    it("applies orange color for medium CPU usage", () => {
      mockUseSystem.mockReturnValue({
        systemInfo: mockSystemInfo,
        currentMetrics: { ...mockCurrentMetrics, cpu_usage: 75 },
        metricsHistory: null,
        isLoading: false,
        error: null,
        refreshHistory: jest.fn(),
      });

      const { container } = render(<MiniSystemSummary />);

      // Medium threshold should use orange color
      expect(container.innerHTML).toContain("#ffaa00");
    });

    it("applies red color for high CPU usage", () => {
      mockUseSystem.mockReturnValue({
        systemInfo: mockSystemInfo,
        currentMetrics: { ...mockCurrentMetrics, cpu_usage: 95 },
        metricsHistory: null,
        isLoading: false,
        error: null,
        refreshHistory: jest.fn(),
      });

      const { container } = render(<MiniSystemSummary />);

      // High threshold should use red color
      expect(container.innerHTML).toContain("#ff0040");
    });
  });

  it("renders circular cards with correct aspect ratio", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<MiniSystemSummary />);

    const cards = container.querySelectorAll(".aspect-square");
    expect(cards.length).toBe(4);

    cards.forEach(card => {
      expect(card).toHaveClass("rounded-full");
    });
  });

  it("applies hover effects to cards", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<MiniSystemSummary />);

    const cards = container.querySelectorAll(".aspect-square");
    cards.forEach(card => {
      expect(card).toHaveClass("hover:scale-105", "transition-all");
    });
  });

  it("uses grid layout with 4 columns", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<MiniSystemSummary />);

    const grid = container.querySelector(".grid-cols-4");
    expect(grid).toBeInTheDocument();
  });

  it("handles missing system info gracefully", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: null,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    render(<MiniSystemSummary />);

    // Should show -- for total capacities when systemInfo is missing
    expect(screen.getByText("25.5%")).toBeInTheDocument();
    expect(screen.getByText("45.2°C")).toBeInTheDocument();
  });

  it("applies consistent text sizing", () => {
    mockUseSystem.mockReturnValue({
      systemInfo: mockSystemInfo,
      currentMetrics: mockCurrentMetrics,
      metricsHistory: null,
      isLoading: false,
      error: null,
      refreshHistory: jest.fn(),
    });

    const { container } = render(<MiniSystemSummary />);

    // Check for text-xs labels
    const labels = container.querySelectorAll(".text-xs");
    expect(labels.length).toBeGreaterThan(0);

    // Check for text-2xl values
    const values = container.querySelectorAll(".text-2xl");
    expect(values.length).toBe(4);
  });
});
