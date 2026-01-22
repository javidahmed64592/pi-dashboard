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
} from "recharts";

interface ChartData {
  timestamp: string;
  value: number;
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
}: MetricsGraphProps) {
  const gradientId = `${title.replace(/\s+/g, "")}Gradient`;

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
                dataKey="timestamp"
                stroke="#888888"
                style={{ fontSize: "12px", fontFamily: "monospace" }}
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
                contentStyle={{
                  backgroundColor: "#0a0a0a",
                  border: `1px solid ${color}`,
                  borderRadius: "4px",
                  fontFamily: "monospace",
                }}
                labelStyle={{ color: "#888888" }}
                itemStyle={{ color }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                fill={`url(#${gradientId})`}
                strokeWidth={2}
              />
            </AreaChart>
          ) : (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
              <XAxis
                dataKey="timestamp"
                stroke="#888888"
                style={{ fontSize: "12px", fontFamily: "monospace" }}
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
                contentStyle={{
                  backgroundColor: "#0a0a0a",
                  border: `1px solid ${color}`,
                  borderRadius: "4px",
                  fontFamily: "monospace",
                }}
                labelStyle={{ color: "#888888" }}
                itemStyle={{ color }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      )}
    </div>
  );
}
