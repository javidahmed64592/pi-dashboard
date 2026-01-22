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

interface MetricsGraphProps {
  title: string;
  data: ChartData[];
  color: string;
  chartType: ChartType;
  yAxisLabel: string;
  yAxisDomain?: [number, number];
  hasData: boolean;
  className?: string;
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
}: MetricsGraphProps) {
  const gradientId = `${title.replace(/\s+/g, "")}Gradient`;

  return (
    <div
      className={`bg-background-secondary border rounded-lg p-3 hover:shadow-neon transition-shadow ${className}`}
      style={{ borderColor: color }}
    >
      <h2 className="text-lg font-bold mb-3 font-mono" style={{ color }}>
        {title}
      </h2>
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
