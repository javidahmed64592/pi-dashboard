interface UptimeDisplayProps {
  uptime: number | undefined;
}

export default function UptimeDisplay({ uptime }: UptimeDisplayProps) {
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

  if (!uptime) {
    return <div />;
  }

  return (
    <div className="bg-background-secondary border border-neon-green rounded-lg px-4 py-2 shadow-neon">
      <div className="text-xs text-text-muted font-mono">SYSTEM UPTIME</div>
      <div className="text-xl font-bold text-neon-green font-mono">
        {formatUptime(uptime)}
      </div>
    </div>
  );
}
