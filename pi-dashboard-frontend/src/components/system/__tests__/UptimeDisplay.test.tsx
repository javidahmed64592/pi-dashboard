/**
 * @jest-environment jsdom
 */

import { render, screen } from "@testing-library/react";

import UptimeDisplay from "../UptimeDisplay";

describe("UptimeDisplay", () => {
  it("formats uptime with days, hours, minutes, and seconds", () => {
    const uptime = 90061; // 1 day, 1 hour, 1 minute, 1 second
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("SYSTEM UPTIME")).toBeInTheDocument();
    expect(screen.getByText("1d 1h 1m 1s")).toBeInTheDocument();
  });

  it("formats uptime with only hours, minutes, and seconds", () => {
    const uptime = 3661; // 1 hour, 1 minute, 1 second
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("1h 1m 1s")).toBeInTheDocument();
  });

  it("formats uptime with only minutes and seconds", () => {
    const uptime = 125; // 2 minutes, 5 seconds
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("2m 5s")).toBeInTheDocument();
  });

  it("formats uptime with only seconds", () => {
    const uptime = 45; // 45 seconds
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("45s")).toBeInTheDocument();
  });

  it("renders empty div for zero uptime", () => {
    const uptime = 0;
    const { container } = render(<UptimeDisplay uptime={uptime} />);

    expect(container.firstChild).toBeEmptyDOMElement();
  });

  it("formats large uptime correctly", () => {
    const uptime = 2592000; // 30 days
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("30d")).toBeInTheDocument();
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

    const value = screen.getByText("1m");
    expect(value).toHaveClass("text-xl");
    expect(value).toHaveClass("font-bold");
    expect(value).toHaveClass("text-neon-green");
    expect(value).toHaveClass("font-mono");
  });

  it("formats mixed time components correctly", () => {
    const uptime = 183723; // 2 days, 3 hours, 2 minutes, 3 seconds
    render(<UptimeDisplay uptime={uptime} />);

    expect(screen.getByText("2d 3h 2m 3s")).toBeInTheDocument();
  });
});
