/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent } from "@testing-library/react";

import TimeRangeSelector from "../TimeRangeSelector";

describe("TimeRangeSelector", () => {
  const mockOnRangeChange = jest.fn();

  beforeEach(() => {
    mockOnRangeChange.mockClear();
  });

  it("renders all time range buttons", () => {
    render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    expect(screen.getByText("1m")).toBeInTheDocument();
    expect(screen.getByText("5m")).toBeInTheDocument();
    expect(screen.getByText("15m")).toBeInTheDocument();
    expect(screen.getByText("30m")).toBeInTheDocument();
  });

  it("highlights the selected range button", () => {
    render(
      <TimeRangeSelector
        selectedRange={300}
        onRangeChange={mockOnRangeChange}
      />
    );

    const selectedButton = screen.getByText("5m");
    expect(selectedButton).toHaveClass("bg-neon-green");
    expect(selectedButton).toHaveClass("text-background");
    expect(selectedButton).toHaveClass("border-neon-green");
    expect(selectedButton).toHaveClass("shadow-neon");
  });

  it("applies default styling to non-selected buttons", () => {
    render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    const button = screen.getByText("5m");
    expect(button).toHaveClass("bg-background-secondary");
    expect(button).toHaveClass("text-text-primary");
    expect(button).toHaveClass("border-border");
  });

  it("calls onRangeChange when a button is clicked", () => {
    render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    const button = screen.getByText("5m");
    fireEvent.click(button);

    expect(mockOnRangeChange).toHaveBeenCalledWith(300);
  });

  it("calls onRangeChange with correct values for all buttons", () => {
    render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    fireEvent.click(screen.getByText("1m"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(60);

    fireEvent.click(screen.getByText("5m"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(300);

    fireEvent.click(screen.getByText("15m"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(900);

    fireEvent.click(screen.getByText("30m"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(1800);
  });

  it("applies correct styling classes to all buttons", () => {
    render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    const buttons = screen.getAllByRole("button");
    buttons.forEach(button => {
      expect(button).toHaveClass("px-3");
      expect(button).toHaveClass("py-2");
      expect(button).toHaveClass("rounded");
      expect(button).toHaveClass("border");
      expect(button).toHaveClass("transition-all");
      expect(button).toHaveClass("font-mono");
      expect(button).toHaveClass("text-sm");
    });
  });

  it("changes selection when different time range is selected", () => {
    const { rerender } = render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    let selectedButton = screen.getByText("1m");
    expect(selectedButton).toHaveClass("bg-neon-green");

    rerender(
      <TimeRangeSelector
        selectedRange={900}
        onRangeChange={mockOnRangeChange}
      />
    );

    selectedButton = screen.getByText("15m");
    expect(selectedButton).toHaveClass("bg-neon-green");

    const unselectedButton = screen.getByText("1m");
    expect(unselectedButton).not.toHaveClass("bg-neon-green");
  });

  it("renders buttons in correct order", () => {
    render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons[0]).toHaveTextContent("1m");
    expect(buttons[1]).toHaveTextContent("5m");
    expect(buttons[2]).toHaveTextContent("15m");
    expect(buttons[3]).toHaveTextContent("30m");
  });

  it("maintains button state after multiple clicks", () => {
    render(
      <TimeRangeSelector selectedRange={60} onRangeChange={mockOnRangeChange} />
    );

    const button = screen.getByText("5m");
    fireEvent.click(button);
    fireEvent.click(button);
    fireEvent.click(button);

    expect(mockOnRangeChange).toHaveBeenCalledTimes(3);
    expect(mockOnRangeChange).toHaveBeenCalledWith(300);
  });
});
