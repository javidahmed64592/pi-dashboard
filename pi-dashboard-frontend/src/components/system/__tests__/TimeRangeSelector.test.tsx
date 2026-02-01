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
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
    );

    expect(screen.getByText("1h")).toBeInTheDocument();
    expect(screen.getByText("4h")).toBeInTheDocument();
    expect(screen.getByText("12h")).toBeInTheDocument();
    expect(screen.getByText("24h")).toBeInTheDocument();
  });

  it("highlights the selected range button", () => {
    render(
      <TimeRangeSelector
        selectedRange={14400}
        onRangeChange={mockOnRangeChange}
      />
    );

    const selectedButton = screen.getByText("4h");
    expect(selectedButton).toHaveClass("bg-neon-green");
    expect(selectedButton).toHaveClass("text-background");
    expect(selectedButton).toHaveClass("border-neon-green");
    expect(selectedButton).toHaveClass("shadow-neon");
  });

  it("applies default styling to non-selected buttons", () => {
    render(
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
    );

    const button = screen.getByText("4h");
    expect(button).toHaveClass("bg-background-secondary");
    expect(button).toHaveClass("text-text-primary");
    expect(button).toHaveClass("border-border");
  });

  it("calls onRangeChange when a button is clicked", () => {
    render(
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
    );

    const button = screen.getByText("4h");
    fireEvent.click(button);

    expect(mockOnRangeChange).toHaveBeenCalledWith(14400);
  });

  it("calls onRangeChange with correct values for all buttons", () => {
    render(
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
    );

    fireEvent.click(screen.getByText("1h"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(3600);

    fireEvent.click(screen.getByText("4h"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(14400);

    fireEvent.click(screen.getByText("12h"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(43200);

    fireEvent.click(screen.getByText("24h"));
    expect(mockOnRangeChange).toHaveBeenCalledWith(86400);
  });

  it("applies correct styling classes to all buttons", () => {
    render(
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
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
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
    );

    let selectedButton = screen.getByText("1h");
    expect(selectedButton).toHaveClass("bg-neon-green");

    rerender(
      <TimeRangeSelector
        selectedRange={43200}
        onRangeChange={mockOnRangeChange}
      />
    );

    selectedButton = screen.getByText("12h");
    expect(selectedButton).toHaveClass("bg-neon-green");

    const unselectedButton = screen.getByText("1h");
    expect(unselectedButton).not.toHaveClass("bg-neon-green");
  });

  it("renders buttons in correct order", () => {
    render(
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons[0]).toHaveTextContent("1h");
    expect(buttons[1]).toHaveTextContent("4h");
    expect(buttons[2]).toHaveTextContent("12h");
    expect(buttons[3]).toHaveTextContent("24h");
  });

  it("maintains button state after multiple clicks", () => {
    render(
      <TimeRangeSelector
        selectedRange={3600}
        onRangeChange={mockOnRangeChange}
      />
    );

    const button = screen.getByText("4h");
    fireEvent.click(button);
    fireEvent.click(button);
    fireEvent.click(button);

    expect(mockOnRangeChange).toHaveBeenCalledTimes(3);
    expect(mockOnRangeChange).toHaveBeenCalledWith(14400);
  });
});
