"use client";

import { useEffect, useState } from "react";

import MetricsGraph from "@/components/MetricsGraph";
import { useSystem } from "@/contexts/SystemContext";
import type { SystemMetricsHistoryEntry } from "@/lib/types";

type TimeRange = 60 | 300 | 900 | 1800;

interface ChartData {
  timestamp: string;
  value: number;
}

const TIME_RANGES: { label: string; seconds: TimeRange }[] = [
  { label: "1m", seconds: 60 },
  { label: "5m", seconds: 300 },
  { label: "15m", seconds: 900 },
  { label: "30m", seconds: 1800 },
];

export default function SystemPage() {
  const { currentMetrics, metricsHistory, refreshHistory } = useSystem();
  const [selectedRange, setSelectedRange] = useState<TimeRange>(60);

  // Poll history based on selected time range
  useEffect(() => {
    // Initial fetch
    refreshHistory(selectedRange);

    // Poll every second
    const interval = setInterval(() => {
      refreshHistory(selectedRange);
    }, 1000);

    return () => clearInterval(interval);
  }, [selectedRange, refreshHistory]);

  // Format uptime from seconds to readable string
  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

    return parts.join(" ");
  };

  // Format timestamp for chart
  const formatTime = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
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
        {/* Uptime Display */}
        {currentMetrics ? (
          <div className="bg-background-secondary border border-neon-green rounded-lg px-4 py-2 shadow-neon">
            <div className="text-xs text-text-muted font-mono">
              SYSTEM UPTIME
            </div>
            <div className="text-xl font-bold text-neon-green font-mono">
              {formatUptime(currentMetrics.uptime)}
            </div>
          </div>
        ) : (
          <div />
        )}

        {/* Time Range Selector */}
        <div className="flex gap-2">
          {TIME_RANGES.map(range => (
            <button
              key={range.seconds}
              onClick={() => setSelectedRange(range.seconds)}
              className={`px-3 py-2 rounded border transition-all font-mono text-sm ${
                selectedRange === range.seconds
                  ? "bg-neon-green text-background border-neon-green shadow-neon"
                  : "bg-background-secondary text-text-primary border-border hover:border-neon-green"
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
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
        />

        <MetricsGraph
          title="CPU Temperature"
          data={tempData}
          color="#ff0040"
          chartType="line"
          yAxisLabel="°C"
          hasData={hasData}
          className={
            currentMetrics && currentMetrics.temperature > 50
              ? "animate-pulse"
              : ""
          }
        />

        <MetricsGraph
          title="Memory Usage"
          data={memoryData}
          color="#bf00ff"
          chartType="area"
          yAxisLabel="%"
          yAxisDomain={[0, 100]}
          hasData={hasData}
        />

        <MetricsGraph
          title="Disk Usage"
          data={diskData}
          color="#00ff41"
          chartType="line"
          yAxisLabel="%"
          yAxisDomain={[0, 100]}
          hasData={hasData}
        />
      </div>
    </div>
  );
}
