"use client";

import { useEffect, useState } from "react";

import MetricsGraph from "@/components/system/MetricsGraph";
import TimeRangeSelector, {
  type TimeRange,
} from "@/components/system/TimeRangeSelector";
import UptimeDisplay from "@/components/system/UptimeDisplay";
import { useSystem } from "@/contexts/SystemContext";
import type { SystemMetricsHistoryEntry } from "@/lib/types";

interface ChartData {
  timestamp: string;
  value: number;
}

export default function SystemPage() {
  const { currentMetrics, metricsHistory, systemInfo, refreshHistory } =
    useSystem();
  const [selectedRange, setSelectedRange] = useState<TimeRange>(60);

  // Poll history based on selected time range
  useEffect(() => {
    // Initial fetch
    refreshHistory(selectedRange);

    // Poll every 5 seconds
    const interval = setInterval(() => {
      refreshHistory(selectedRange);
    }, 5000);

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

  // Convert history to chart data
  const convertToChartData = (
    history: SystemMetricsHistoryEntry[] | undefined,
    metricKey: keyof SystemMetricsHistoryEntry["metrics"]
  ): ChartData[] => {
    if (!history || history.length === 0) return [];
    return history.map(entry => ({
      timestamp: formatTime(entry.timestamp),
      value: Number(entry.metrics[metricKey].toFixed(1)),
    }));
  };

  const cpuData = convertToChartData(metricsHistory?.history, "cpu_usage");
  const tempData = convertToChartData(metricsHistory?.history, "temperature");
  const memoryData = convertToChartData(
    metricsHistory?.history,
    "memory_usage"
  );
  const diskData = convertToChartData(metricsHistory?.history, "disk_usage");

  const hasData = cpuData.length > 0;

  return (
    <div className="space-y-5">
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
        />

        <MetricsGraph
          title="CPU Temperature"
          data={tempData}
          color="#ff0040"
          chartType="line"
          yAxisLabel="°C"
          yAxisDomain={[0, 70]}
          hasData={hasData}
          currentValue={currentMetrics?.temperature}
          thresholds={{ low: 35, medium: 50 }}
          className={
            currentMetrics && currentMetrics.temperature > 50
              ? "animate-pulse"
              : ""
          }
          graphId="cpuTemp"
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
        />
      </div>
    </div>
  );
}
