interface ServiceCardProps {
  name: string;
  description: string;
  path: string;
  status: "running" | "stopped";
  port: number;
}

export default function ServiceCard({
  name,
  description,
  path,
  status,
  port,
}: ServiceCardProps) {
  const statusColor = status === "running" ? "#00ff41" : "#ff0040";

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon hover:border-neon-green transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-text-primary font-mono">
            {description}
          </h3>
          <p className="text-xs text-text-muted font-mono mt-1">{name}</p>
        </div>
        <div
          className="w-3 h-3 rounded-full animate-pulse"
          style={{
            backgroundColor: statusColor,
            boxShadow: `0 0 10px ${statusColor}`,
          }}
        />
      </div>

      <div className="text-xs text-text-muted font-mono mb-4 truncate">
        {path}
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        <button className="px-3 py-1 text-xs font-mono bg-neon-green text-background rounded hover:bg-opacity-80 transition-all">
          Start
        </button>
        <button className="px-3 py-1 text-xs font-mono bg-neon-red text-background rounded hover:bg-opacity-80 transition-all">
          Stop
        </button>
        <button className="px-3 py-1 text-xs font-mono bg-neon-blue text-background rounded hover:bg-opacity-80 transition-all">
          Restart
        </button>
        <button className="px-3 py-1 text-xs font-mono bg-neon-purple text-background rounded hover:bg-opacity-80 transition-all">
          Update
        </button>
      </div>

      <a
        href={`http://localhost:${port}`}
        target="_blank"
        rel="noopener noreferrer"
        className="text-xs font-mono text-neon-green hover:text-neon-blue transition-colors"
      >
        Open App →
      </a>
    </div>
  );
}
