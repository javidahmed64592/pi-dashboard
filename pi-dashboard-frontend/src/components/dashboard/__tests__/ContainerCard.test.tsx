import { render, screen, fireEvent } from "@testing-library/react";

import ContainerCard from "@/components/dashboard/ContainerCard";

describe("ContainerCard", () => {
  const mockHandlers = {
    onStart: jest.fn(),
    onStop: jest.fn(),
    onRestart: jest.fn(),
    onUpdate: jest.fn(),
  };

  const defaultProps = {
    container_id: "abc123",
    name: "pi-dashboard",
    image: "ghcr.io/user/pi-dashboard:latest",
    status: "running" as const,
    ports: [
      { host: "443", container: "443", protocol: "tcp" },
      { host: "8080", container: "80", protocol: "tcp" },
    ],
    ...mockHandlers,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders container information correctly", () => {
    render(<ContainerCard {...defaultProps} />);

    expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
    expect(
      screen.getByText("ghcr.io/user/pi-dashboard:latest")
    ).toBeInTheDocument();
    expect(screen.getByText("Port: 443")).toBeInTheDocument();
  });

  it("renders external link icon when container has ports", () => {
    render(<ContainerCard {...defaultProps} />);

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "http://localhost:443");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");

    // Check for external link icon (svg)
    const svg = link.querySelector("svg");
    expect(svg).toBeInTheDocument();
  });

  it("does not render link when container has no ports", () => {
    render(<ContainerCard {...defaultProps} ports={[]} />);

    const link = screen.queryByRole("link");
    expect(link).not.toBeInTheDocument();
    expect(screen.getByText("pi-dashboard")).toBeInTheDocument();
  });

  it("displays green status indicator when running", () => {
    const { container } = render(<ContainerCard {...defaultProps} />);

    const statusIndicator = container.querySelector(
      ".rounded-full.animate-pulse"
    );
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveStyle({
      backgroundColor: "#00ff41",
    });
  });

  it("displays red status indicator when stopped", () => {
    const { container } = render(
      <ContainerCard {...defaultProps} status="exited" />
    );

    const statusIndicator = container.querySelector(
      ".rounded-full.animate-pulse"
    );
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveStyle({
      backgroundColor: "#ff0040",
    });
  });

  describe("Button states when container is running", () => {
    beforeEach(() => {
      render(<ContainerCard {...defaultProps} status="running" />);
    });

    it("disables start button", () => {
      const startButton = screen.getByTitle("Start");
      expect(startButton).toBeDisabled();
      expect(startButton).toHaveClass("opacity-50", "cursor-not-allowed");
    });

    it("enables stop button", () => {
      const stopButton = screen.getByTitle("Stop");
      expect(stopButton).not.toBeDisabled();
      expect(stopButton).toHaveClass("text-neon-red");
      expect(stopButton).not.toHaveClass("opacity-50");
    });

    it("enables restart button", () => {
      const restartButton = screen.getByTitle("Restart");
      expect(restartButton).not.toBeDisabled();
      expect(restartButton).toHaveClass("text-neon-blue");
      expect(restartButton).not.toHaveClass("opacity-50");
    });

    it("enables update button", () => {
      const updateButton = screen.getByTitle("Update");
      expect(updateButton).not.toBeDisabled();
      expect(updateButton).toHaveClass("text-neon-purple");
    });
  });

  describe("Button states when container is stopped", () => {
    beforeEach(() => {
      render(<ContainerCard {...defaultProps} status="exited" />);
    });

    it("enables start button", () => {
      const startButton = screen.getByTitle("Start");
      expect(startButton).not.toBeDisabled();
      expect(startButton).toHaveClass("text-neon-green");
      expect(startButton).not.toHaveClass("opacity-50");
    });

    it("disables stop button", () => {
      const stopButton = screen.getByTitle("Stop");
      expect(stopButton).toBeDisabled();
      expect(stopButton).toHaveClass("opacity-50", "cursor-not-allowed");
    });

    it("disables restart button", () => {
      const restartButton = screen.getByTitle("Restart");
      expect(restartButton).toBeDisabled();
      expect(restartButton).toHaveClass("opacity-50", "cursor-not-allowed");
    });

    it("enables update button", () => {
      const updateButton = screen.getByTitle("Update");
      expect(updateButton).not.toBeDisabled();
      expect(updateButton).toHaveClass("text-neon-purple");
    });
  });

  describe("Button click handlers", () => {
    it("calls onStart when start button is clicked", () => {
      render(<ContainerCard {...defaultProps} status="exited" />);
      const startButton = screen.getByTitle("Start");
      fireEvent.click(startButton);
      expect(mockHandlers.onStart).toHaveBeenCalledWith("abc123");
    });

    it("calls onStop when stop button is clicked", () => {
      render(<ContainerCard {...defaultProps} status="running" />);
      const stopButton = screen.getByTitle("Stop");
      fireEvent.click(stopButton);
      expect(mockHandlers.onStop).toHaveBeenCalledWith("abc123");
    });

    it("calls onRestart when restart button is clicked", () => {
      render(<ContainerCard {...defaultProps} status="running" />);
      const restartButton = screen.getByTitle("Restart");
      fireEvent.click(restartButton);
      expect(mockHandlers.onRestart).toHaveBeenCalledWith("abc123");
    });

    it("calls onUpdate when update button is clicked", () => {
      render(<ContainerCard {...defaultProps} />);
      const updateButton = screen.getByTitle("Update");
      fireEvent.click(updateButton);
      expect(mockHandlers.onUpdate).toHaveBeenCalledWith("abc123");
    });
  });

  it("renders all four action buttons", () => {
    render(<ContainerCard {...defaultProps} />);

    expect(screen.getByTitle("Start")).toBeInTheDocument();
    expect(screen.getByTitle("Stop")).toBeInTheDocument();
    expect(screen.getByTitle("Restart")).toBeInTheDocument();
    expect(screen.getByTitle("Update")).toBeInTheDocument();
  });

  it("applies hover styles to the card", () => {
    const { container } = render(<ContainerCard {...defaultProps} />);

    const card = container.firstChild;
    expect(card).toHaveClass(
      "hover:border-neon-green",
      "transition-all",
      "shadow-neon"
    );
  });

  it("truncates long image names", () => {
    render(<ContainerCard {...defaultProps} />);

    const imageElement = screen.getByText("ghcr.io/user/pi-dashboard:latest");
    expect(imageElement).toHaveClass("truncate");
  });

  it("makes container name clickable with correct link when ports exist", () => {
    render(<ContainerCard {...defaultProps} />);

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "http://localhost:443");
    expect(link.textContent).toContain("pi-dashboard");
  });

  it("applies correct layout classes", () => {
    const { container } = render(<ContainerCard {...defaultProps} />);

    const mainContainer = container.querySelector(".flex.justify-between");
    expect(mainContainer).toBeInTheDocument();

    const buttonsContainer = container.querySelector(".flex.gap-1\\.5");
    expect(buttonsContainer).toBeInTheDocument();
  });

  it("displays primary port correctly", () => {
    render(<ContainerCard {...defaultProps} />);
    expect(screen.getByText("Port: 443")).toBeInTheDocument();
  });

  it("handles container with no ports", () => {
    render(<ContainerCard {...defaultProps} ports={[]} />);
    expect(screen.queryByText(/Port:/)).not.toBeInTheDocument();
  });
});
