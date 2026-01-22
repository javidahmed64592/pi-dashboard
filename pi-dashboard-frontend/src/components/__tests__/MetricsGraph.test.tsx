/**
 * @jest-environment jsdom
 */

import { render, screen } from "@testing-library/react";

import MetricsGraph from "../MetricsGraph";

const mockData = [
  { timestamp: "01:00:00", value: 25.5 },
  { timestamp: "01:00:05", value: 30.2 },
  { timestamp: "01:00:10", value: 28.8 },
];

describe("MetricsGraph", () => {
  it("renders graph title", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        graphId="test"
      />
    );

    expect(screen.getByText("CPU Load")).toBeInTheDocument();
  });

  it("displays no data message when hasData is false", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={[]}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={false}
        graphId="test"
      />
    );

    expect(
      screen.getByText("No data available for the selected time range.")
    ).toBeInTheDocument();
  });

  it("renders threshold indicator when provided", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        currentValue={25}
        thresholds={{ low: 30, medium: 60 }}
        graphId="test"
      />
    );

    expect(screen.getByText("LOW")).toBeInTheDocument();
  });

  it("displays MEDIUM threshold when value is between low and medium", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        currentValue={45}
        thresholds={{ low: 30, medium: 60 }}
        graphId="test"
      />
    );

    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  it("displays HIGH threshold when value is above medium", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        currentValue={75}
        thresholds={{ low: 30, medium: 60 }}
        graphId="test"
      />
    );

    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("does not display threshold when currentValue is not provided", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        thresholds={{ low: 30, medium: 60 }}
        graphId="test"
      />
    );

    expect(screen.queryByText("LOW")).not.toBeInTheDocument();
    expect(screen.queryByText("MEDIUM")).not.toBeInTheDocument();
    expect(screen.queryByText("HIGH")).not.toBeInTheDocument();
  });

  it("does not display threshold when thresholds are not provided", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        currentValue={45}
        graphId="test"
      />
    );

    expect(screen.queryByText("LOW")).not.toBeInTheDocument();
    expect(screen.queryByText("MEDIUM")).not.toBeInTheDocument();
    expect(screen.queryByText("HIGH")).not.toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        className="custom-class"
        graphId="test"
      />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("renders with line chart type", () => {
    render(
      <MetricsGraph
        title="Temperature"
        data={mockData}
        color="#ff0040"
        chartType="line"
        yAxisLabel="°C"
        hasData={true}
        graphId="test"
      />
    );

    expect(screen.getByText("Temperature")).toBeInTheDocument();
  });

  it("renders with area chart type", () => {
    render(
      <MetricsGraph
        title="CPU Load"
        data={mockData}
        color="#00bfff"
        chartType="area"
        yAxisLabel="%"
        hasData={true}
        graphId="test"
      />
    );

    expect(screen.getByText("CPU Load")).toBeInTheDocument();
  });
});
