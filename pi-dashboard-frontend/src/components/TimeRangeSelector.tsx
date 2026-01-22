type TimeRange = 60 | 300 | 900 | 1800;

interface TimeRangeSelectorProps {
  selectedRange: TimeRange;
  onRangeChange: (range: TimeRange) => void;
}

const TIME_RANGES: { label: string; seconds: TimeRange }[] = [
  { label: "1m", seconds: 60 },
  { label: "5m", seconds: 300 },
  { label: "15m", seconds: 900 },
  { label: "30m", seconds: 1800 },
];

export default function TimeRangeSelector({
  selectedRange,
  onRangeChange,
}: TimeRangeSelectorProps) {
  return (
    <div className="flex gap-2">
      {TIME_RANGES.map(range => (
        <button
          key={range.seconds}
          onClick={() => onRangeChange(range.seconds)}
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
  );
}

export type { TimeRange };
