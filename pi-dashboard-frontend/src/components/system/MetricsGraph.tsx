import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceArea,
} from "recharts";

interface ChartData {
  timestamp: string;
  timestampNum: number;
  value: number | null;
  isGap?: boolean;
}

interface DataGap {
  start: number;
  end: number;
}

type ChartType = "area" | "line";

type ThresholdLevel = "LOW" | "MEDIUM" | "HIGH";

interface ThresholdConfig {
  low: number;
  medium: number;
}

interface MetricsGraphProps {
  title: string;
  data: ChartData[];
  color: string;
  chartType: ChartType;
  yAxisLabel: string;
  yAxisDomain?: [number, number] | undefined;
  hasData: boolean;
  className?: string;
  currentValue?: number | undefined;
  thresholds?: ThresholdConfig | undefined;
  graphId: string;
  gaps?: DataGap[];
}

// Custom tooltip component (defined outside to avoid recreating on each render)
function CustomTooltip({
  active,
  payload,
  color,
  yAxisLabel,
}: {
  active?: boolean;
  payload?: Array<{ payload: ChartData; value: number }>;
  color: string;
  yAxisLabel: string;
}) {
  if (active && payload && payload.length > 0) {
    const dataPoint = payload[0]!.payload as ChartData;
    if (dataPoint.value === null) return null;

    return (
      <div
        style={{
          backgroundColor: "#0a0a0a",
          border: `1px solid ${color}`,
          borderRadius: "4px",
          padding: "8px",
          fontFamily: "monospace",
        }}
      >
        <p style={{ color: "#888888", margin: 0 }}>{dataPoint.timestamp}</p>
        <p style={{ color, margin: "4px 0 0 0", fontWeight: "bold" }}>
          {`${dataPoint.value.toFixed(1)} ${yAxisLabel}`}
        </p>
      </div>
    );
  }
  return null;
}

export default function MetricsGraph({
  title,
  data,
  color,
  chartType,
  yAxisLabel,
  yAxisDomain,
  hasData,
  className = "",
  currentValue,
  thresholds,
  graphId,
  gaps = [],
}: MetricsGraphProps) {
  const gradientId = `${graphId}Gradient`;

  const getThresholdLevel = (): ThresholdLevel | null => {
    if (currentValue === undefined || !thresholds) return null;
    if (currentValue < thresholds.low) return "LOW";
    if (currentValue < thresholds.medium) return "MEDIUM";
    return "HIGH";
  };

  const getThresholdColor = (level: ThresholdLevel | null): string => {
    switch (level) {
      case "LOW":
        return "#00ff41";
      case "MEDIUM":
        return "#ffaa00";
      case "HIGH":
        return "#ff0040";
      default:
        return "#888888";
    }
  };

  // Format tick for x-axis (converts unix timestamp to time string)
  const formatXAxisTick = (value: number): string => {
    const date = new Date(value * 1000);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
      timeZone: "UTC",
    });
  };

  // Compute evenly-spaced x-axis ticks across the full domain so labels
  // appear at regular intervals regardless of where data actually exists.
  const timestampNums = data.map(d => d.timestampNum);
  const domainMin = timestampNums.length > 0 ? Math.min(...timestampNums) : 0;
  const domainMax = timestampNums.length > 0 ? Math.max(...timestampNums) : 0;
  const xAxisTicks: number[] =
    domainMin !== domainMax
      ? Array.from({ length: 7 }, (_, i) =>
          Math.round(domainMin + (i / 6) * (domainMax - domainMin))
        )
      : [domainMin];

  const thresholdLevel = getThresholdLevel();
  const thresholdColor = getThresholdColor(thresholdLevel);

  return (
    <div
      className={`bg-background-secondary border rounded-lg p-3 hover:shadow-neon transition-shadow ${className}`}
      style={{ borderColor: color }}
    >
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-bold font-mono" style={{ color }}>
          {title}
        </h2>
        {thresholdLevel && (
          <span
            className="text-xs font-bold font-mono px-2 py-1 rounded"
            style={{
              color: thresholdColor,
              border: `1px solid ${thresholdColor}`,
            }}
          >
            {thresholdLevel}
          </span>
        )}
      </div>
      {!hasData ? (
        <div className="h-60 flex items-center justify-center text-text-muted opacity-50">
          No data available for the selected time range.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          {chartType === "area" ? (
            <AreaChart data={data}>
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={color} stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
              <XAxis
                dataKey="timestampNum"
                stroke="#888888"
                style={{ fontSize: "12px", fontFamily: "monospace" }}
                type="number"
                domain={[domainMin, domainMax]}
                ticks={xAxisTicks}
                tickFormatter={formatXAxisTick}
                scale="time"
              />
              <YAxis
                stroke="#888888"
                style={{ fontSize: "12px", fontFamily: "monospace" }}
                {...(yAxisDomain && { domain: yAxisDomain })}
                label={{
                  value: yAxisLabel,
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: "#888888" },
                }}
              />
              <Tooltip
                content={
                  <CustomTooltip color={color} yAxisLabel={yAxisLabel} />
                }
              />
              {/* Highlight data gaps with subtle shading */}
              {gaps.map((gap, index) => (
                <ReferenceArea
                  key={`gap-${index}`}
                  x1={gap.start}
                  x2={gap.end}
                  fill="#ff0040"
                  fillOpacity={0.05}
                  strokeOpacity={0.3}
                  stroke="#ff0040"
                  strokeDasharray="3 3"
                />
              ))}
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                fill={`url(#${gradientId})`}
                strokeWidth={2}
                connectNulls={false}
                dot={false}
              />
            </AreaChart>
          ) : (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
              <XAxis
                dataKey="timestampNum"
                stroke="#888888"
                style={{ fontSize: "12px", fontFamily: "monospace" }}
                type="number"
                domain={[domainMin, domainMax]}
                ticks={xAxisTicks}
                tickFormatter={formatXAxisTick}
                scale="time"
              />
              <YAxis
                stroke="#888888"
                style={{ fontSize: "12px", fontFamily: "monospace" }}
                {...(yAxisDomain && { domain: yAxisDomain })}
                label={{
                  value: yAxisLabel,
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: "#888888" },
                }}
              />
              <Tooltip
                content={
                  <CustomTooltip color={color} yAxisLabel={yAxisLabel} />
                }
              />
              {/* Highlight data gaps with subtle shading */}
              {gaps.map((gap, index) => (
                <ReferenceArea
                  key={`gap-${index}`}
                  x1={gap.start}
                  x2={gap.end}
                  fill="#ff0040"
                  fillOpacity={0.05}
                  strokeOpacity={0.3}
                  stroke="#ff0040"
                  strokeDasharray="3 3"
                />
              ))}
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                connectNulls={false}
                dot={false}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      )}
    </div>
  );
}
