import { useSystem } from "@/contexts/SystemContext";

interface MetricCardProps {
  label: string;
  value: number | undefined;
  unit: string;
  total?: number | undefined;
  totalUnit?: string;
  thresholds?: { low: number; medium: number };
}

function MetricCard({
  label,
  value,
  unit,
  total,
  totalUnit,
  thresholds,
}: MetricCardProps) {
  const getThresholdColor = (): string => {
    if (value === undefined || !thresholds) return "#888888";
    if (value < thresholds.low) return "#00ff41";
    if (value < thresholds.medium) return "#ffaa00";
    return "#ff0040";
  };

  const borderColor = getThresholdColor();

  return (
    <div
      className="relative bg-background-secondary rounded-full p-5 flex flex-col items-center justify-center aspect-square border-2 shadow-neon transition-all hover:scale-105"
      style={{ borderColor, boxShadow: `0 0 20px ${borderColor}40` }}
    >
      <div className="text-sm font-bold text-text-muted font-mono mb-2 uppercase tracking-wider">
        {label}
      </div>
      <div
        className="text-3xl font-extrabold font-mono leading-none"
        style={{ color: borderColor }}
      >
        {value !== undefined ? `${value.toFixed(1)}${unit}` : "--"}
      </div>
      {total !== undefined && (
        <div className="text-xs text-text-muted font-mono mt-2">
          ({total.toFixed(1)}
          {totalUnit})
        </div>
      )}
    </div>
  );
}

export default function MiniSystemSummary() {
  const { currentMetrics, systemInfo } = useSystem();

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <h2 className="text-lg font-bold text-neon-green font-mono mb-4">
        SYSTEM SUMMARY
      </h2>
      <div className="grid grid-cols-4 gap-3">
        <MetricCard
          label="CPU"
          value={currentMetrics?.cpu_usage}
          unit="%"
          thresholds={{ low: 30, medium: 60 }}
        />
        <MetricCard
          label="MEMORY"
          value={currentMetrics?.memory_usage}
          unit="%"
          total={systemInfo?.memory_total}
          totalUnit="GB"
          thresholds={{ low: 30, medium: 60 }}
        />
        <MetricCard
          label="DISK"
          value={currentMetrics?.disk_usage}
          unit="%"
          total={systemInfo?.disk_total}
          totalUnit="GB"
          thresholds={{ low: 30, medium: 60 }}
        />
        <MetricCard
          label="TEMP"
          value={currentMetrics?.temperature}
          unit="°C"
          thresholds={{ low: 35, medium: 50 }}
        />
      </div>
    </div>
  );
}
