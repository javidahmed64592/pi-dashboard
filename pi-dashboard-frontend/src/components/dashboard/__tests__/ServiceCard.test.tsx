import { render, screen } from "@testing-library/react";

import ServiceCard from "@/components/dashboard/ServiceCard";

describe("ServiceCard", () => {
  const defaultProps = {
    name: "test-service.service",
    description: "Test Service",
    path: "/etc/systemd/system/test-service.service",
    status: "running" as const,
    port: 8080,
  };

  it("renders service information correctly", () => {
    render(<ServiceCard {...defaultProps} />);

    expect(screen.getByText("Test Service")).toBeInTheDocument();
    expect(screen.getByText("test-service.service")).toBeInTheDocument();
    expect(
      screen.getByText("/etc/systemd/system/test-service.service")
    ).toBeInTheDocument();
  });

  it("renders external link icon", () => {
    render(<ServiceCard {...defaultProps} />);

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "http://localhost:8080");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");

    // Check for external link icon (svg)
    const svg = link.querySelector("svg");
    expect(svg).toBeInTheDocument();
  });

  it("displays green status indicator when running", () => {
    const { container } = render(<ServiceCard {...defaultProps} />);

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
      <ServiceCard {...defaultProps} status="stopped" />
    );

    const statusIndicator = container.querySelector(
      ".rounded-full.animate-pulse"
    );
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveStyle({
      backgroundColor: "#ff0040",
    });
  });

  describe("Button states when service is running", () => {
    beforeEach(() => {
      render(<ServiceCard {...defaultProps} status="running" />);
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

  describe("Button states when service is stopped", () => {
    beforeEach(() => {
      render(<ServiceCard {...defaultProps} status="stopped" />);
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

  it("renders all four action buttons", () => {
    render(<ServiceCard {...defaultProps} />);

    expect(screen.getByTitle("Start")).toBeInTheDocument();
    expect(screen.getByTitle("Stop")).toBeInTheDocument();
    expect(screen.getByTitle("Restart")).toBeInTheDocument();
    expect(screen.getByTitle("Update")).toBeInTheDocument();
  });

  it("applies hover styles to the card", () => {
    const { container } = render(<ServiceCard {...defaultProps} />);

    const card = container.firstChild;
    expect(card).toHaveClass(
      "hover:border-neon-green",
      "transition-all",
      "shadow-neon"
    );
  });

  it("truncates long paths", () => {
    render(<ServiceCard {...defaultProps} />);

    const pathElement = screen.getByText(
      "/etc/systemd/system/test-service.service"
    );
    expect(pathElement).toHaveClass("truncate");
  });

  it("makes description text clickable with correct link", () => {
    render(<ServiceCard {...defaultProps} port={3000} />);

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "http://localhost:3000");
    expect(link.textContent).toContain("Test Service");
  });

  it("applies correct layout classes", () => {
    const { container } = render(<ServiceCard {...defaultProps} />);

    const mainContainer = container.querySelector(".flex.justify-between");
    expect(mainContainer).toBeInTheDocument();

    const buttonsContainer = container.querySelector(".flex.gap-1\\.5");
    expect(buttonsContainer).toBeInTheDocument();
  });
});
