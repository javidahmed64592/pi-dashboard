type TimeRange = 3600 | 14400 | 43200 | 86400;

interface TimeRangeSelectorProps {
  selectedRange: TimeRange;
  onRangeChange: (range: TimeRange) => void;
}

const TIME_RANGES: { label: string; seconds: TimeRange }[] = [
  { label: "1h", seconds: 3600 },
  { label: "4h", seconds: 14400 },
  { label: "12h", seconds: 43200 },
  { label: "24h", seconds: 86400 },
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
