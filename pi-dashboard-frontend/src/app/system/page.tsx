"use client";

import { useEffect, useState } from "react";

import MetricsGraph from "@/components/system/MetricsGraph";
import TimeRangeSelector, {
  type TimeRange,
} from "@/components/system/TimeRangeSelector";
import UptimeDisplay from "@/components/system/UptimeDisplay";
import { useSystem } from "@/contexts/SystemContext";
import type { SystemMetrics } from "@/lib/types";

interface ChartData {
  timestamp: string;
  timestampNum: number;
  value: number | null;
}

interface DataGap {
  start: number;
  end: number;
}

export default function SystemPage() {
  const { currentMetrics, metricsHistory, systemInfo, refreshHistory } =
    useSystem();
  const [selectedRange, setSelectedRange] = useState<TimeRange>(3600);

  // Poll history based on selected time range
  useEffect(() => {
    // Initial fetch
    refreshHistory(selectedRange);

    // Poll every 30 seconds
    const interval = setInterval(() => {
      refreshHistory(selectedRange);
    }, 30000);

    return () => clearInterval(interval);
  }, [selectedRange, refreshHistory]);

  // Format timestamp for chart
  const formatTime = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "UTC",
    });
  };

  // Convert history to chart data with gaps filled
  const convertToChartData = (
    history: SystemMetrics[] | undefined | null,
    metricKey: keyof Omit<SystemMetrics, "id" | "timestamp" | "uptime">,
    timeRange: number
  ): { data: ChartData[]; gaps: DataGap[] } => {
    if (!history || history.length === 0) {
      return { data: [], gaps: [] };
    }

    const latestTimestamp = Math.max(...history.map(entry => entry.timestamp));
    const startTime = latestTimestamp - timeRange;

    // Filter to time range and sort by timestamp ascending
    const points = history
      .filter(entry => entry.timestamp >= startTime)
      .sort((a, b) => a.timestamp - b.timestamp);

    if (points.length === 0) {
      return { data: [], gaps: [] };
    }

    const MIN_GAP_DURATION = 300; // 5 minutes in seconds
    const gaps: DataGap[] = [];
    const data: ChartData[] = [];

    // Add anchor at start of time range so x-axis always spans the full range
    data.push({
      timestamp: formatTime(startTime),
      timestampNum: startTime,
      value: null,
    });

    // Check for initial gap (server wasn't running at start of the selected range)
    const firstTimestamp = points[0]!.timestamp;
    if (firstTimestamp - startTime >= MIN_GAP_DURATION) {
      gaps.push({ start: startTime, end: firstTimestamp });
    }

    // Walk through actual data points, detecting gaps between consecutive entries
    for (let i = 0; i < points.length; i++) {
      const current = points[i]!;

      if (i > 0) {
        const prev = points[i - 1]!;
        const gapDuration = current.timestamp - prev.timestamp;
        if (gapDuration >= MIN_GAP_DURATION) {
          // Insert a null to break the drawn line at the gap boundary
          data.push({
            timestamp: formatTime(prev.timestamp + 1),
            timestampNum: prev.timestamp + 1,
            value: null,
          });
          gaps.push({ start: prev.timestamp, end: current.timestamp });
        }
      }

      data.push({
        timestamp: formatTime(current.timestamp),
        timestampNum: current.timestamp,
        value: Number(current[metricKey].toFixed(1)),
      });
    }

    return { data, gaps };
  };

  const cpuResult = convertToChartData(
    metricsHistory,
    "cpu_usage",
    selectedRange
  );
  const tempResult = convertToChartData(
    metricsHistory,
    "temperature",
    selectedRange
  );
  const memoryResult = convertToChartData(
    metricsHistory,
    "memory_usage",
    selectedRange
  );
  const diskResult = convertToChartData(
    metricsHistory,
    "disk_usage",
    selectedRange
  );

  const cpuData = cpuResult.data;
  const tempData = tempResult.data;
  const memoryData = memoryResult.data;
  const diskData = diskResult.data;

  const cpuGaps = cpuResult.gaps;
  const tempGaps = tempResult.gaps;
  const memoryGaps = memoryResult.gaps;
  const diskGaps = diskResult.gaps;

  const hasData = cpuData.length > 0;

  return (
    <div className="h-full overflow-y-auto space-y-5">
      {/* Uptime and Time Range Selector Row */}
      <div className="flex justify-between items-center">
        <UptimeDisplay uptime={currentMetrics?.uptime} />
        <TimeRangeSelector
          selectedRange={selectedRange}
          onRangeChange={setSelectedRange}
        />
      </div>

      {/* Graphs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <MetricsGraph
          title="CPU Load"
          data={cpuData}
          color="#00bfff"
          chartType="area"
          yAxisLabel="%"
          yAxisDomain={[0, 100]}
          hasData={hasData}
          currentValue={currentMetrics?.cpu_usage}
          thresholds={{ low: 30, medium: 60 }}
          graphId="cpuLoad"
          gaps={cpuGaps}
        />

        <MetricsGraph
          title="CPU Temperature"
          data={tempData}
          color="#ff0040"
          chartType="line"
          yAxisLabel="°C"
          yAxisDomain={[0, 80]}
          hasData={hasData}
          currentValue={currentMetrics?.temperature}
          thresholds={{ low: 40, medium: 60 }}
          className={
            currentMetrics && currentMetrics.temperature > 60
              ? "animate-pulse"
              : ""
          }
          graphId="cpuTemp"
          gaps={tempGaps}
        />

        <MetricsGraph
          title={`Memory Usage${systemInfo ? ` (Total: ${systemInfo.memory_total.toFixed(1)}GB)` : ""}`}
          data={memoryData}
          color="#bf00ff"
          chartType="area"
          yAxisLabel="%"
          yAxisDomain={[0, 100]}
          hasData={hasData}
          currentValue={currentMetrics?.memory_usage}
          thresholds={{ low: 30, medium: 60 }}
          graphId="memory"
          gaps={memoryGaps}
        />

        <MetricsGraph
          title={`Disk Usage${systemInfo ? ` (Total: ${systemInfo.disk_total.toFixed(1)}GB)` : ""}`}
          data={diskData}
          color="#00ff41"
          chartType="area"
          yAxisLabel="%"
          yAxisDomain={[0, 100]}
          hasData={hasData}
          currentValue={currentMetrics?.disk_usage}
          thresholds={{ low: 30, medium: 60 }}
          graphId="disk"
          gaps={diskGaps}
        />
      </div>
    </div>
  );
}
