/**
 * @jest-environment jsdom
 */

import { render, screen } from "@testing-library/react";

import UptimeDisplay from "../UptimeDisplay";

describe("UptimeDisplay", () => {
  it("formats uptime with days, hours, and minutes", () => {
    const uptime = 90061; // 1 day, 1 hour, 1 minute, 1 second
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("SYSTEM UPTIME")).toBeInTheDocument();
    expect(screen.getByText("1d 1h 1m")).toBeInTheDocument();
  });

  it("formats uptime with hours and minutes", () => {
    const uptime = 3661; // 1 hour, 1 minute, 1 second
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("0d 1h 1m")).toBeInTheDocument();
  });

  it("formats uptime with minutes", () => {
    const uptime = 125; // 2 minutes, 5 seconds
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("0d 0h 2m")).toBeInTheDocument();
  });

  it("formats uptime with zero days, hours, and minutes", () => {
    const uptime = 45; // 45 seconds
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("0d 0h 0m")).toBeInTheDocument();
  });

  it("renders empty div for zero uptime", () => {
    const uptime = 0;
    const { container } = render(<UptimeDisplay uptime={uptime} />);

    expect(container.firstChild).toBeEmptyDOMElement();
  });

  it("formats large uptime correctly", () => {
    const uptime = 2592000; // 30 days
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("30d 0h 0m")).toBeInTheDocument();
  });

  it("renders nothing when uptime is undefined", () => {
    const { container } = render(<UptimeDisplay uptime={undefined} />);

    expect(container.firstChild).toBeEmptyDOMElement();
  });

  it("has correct styling classes", () => {
    const uptime = 100;
    const { container } = render(<UptimeDisplay uptime={uptime} />);

    const displayDiv = container.firstChild;
    expect(displayDiv).toHaveClass("bg-background-secondary");
    expect(displayDiv).toHaveClass("border");
    expect(displayDiv).toHaveClass("border-neon-green");
    expect(displayDiv).toHaveClass("rounded-lg");
    expect(displayDiv).toHaveClass("shadow-neon");
  });

  it("displays uptime label with correct styling", () => {
    const uptime = 60;
    render(<UptimeDisplay uptime={uptime} />);

    const label = screen.getByText("SYSTEM UPTIME");
    expect(label).toHaveClass("text-xs");
    expect(label).toHaveClass("text-text-muted");
    expect(label).toHaveClass("font-mono");
  });

  it("displays uptime value with correct styling", () => {
    const uptime = 60;
    render(<UptimeDisplay uptime={uptime} />);

    const value = screen.getByText("0d 0h 1m");
    expect(value).toHaveClass("text-xl");
    expect(value).toHaveClass("font-bold");
    expect(value).toHaveClass("text-neon-green");
    expect(value).toHaveClass("font-mono");
  });
});
