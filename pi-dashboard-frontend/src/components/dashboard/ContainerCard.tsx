interface ContainerCardProps {
  container_id: string;
  name: string;
  image: string;
  status: "running" | "exited" | "created" | "restarting" | "paused";
  port: string | null;
  isLoading?: boolean;
  onStart?: (id: string) => void;
  onStop?: (id: string) => void;
  onRestart?: (id: string) => void;
  onUpdate?: (id: string) => void;
  onViewLogs?: (id: string) => void;
}

export default function ContainerCard({
  container_id,
  name,
  image,
  status,
  port,
  isLoading = false,
  onStart,
  onStop,
  onRestart,
  onUpdate,
  onViewLogs,
}: ContainerCardProps) {
  const statusColor = status === "running" ? "#00ff41" : "#ff0040";
  const isRunning = status === "running";

  return (
    <div
      className={`bg-background-secondary border rounded-lg p-4 shadow-neon transition-all relative ${
        isLoading
          ? "border-neon-blue animate-pulse"
          : "border-border hover:border-neon-green"
      }`}
    >
      {isLoading && (
        <div
          className="absolute inset-0 rounded-lg pointer-events-none"
          style={{
            background:
              "repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0, 191, 255, 0.1) 2px, rgba(0, 191, 255, 0.1) 4px)",
            animation: "scanning 2s linear infinite",
          }}
        />
      )}
      <style jsx>{`
        @keyframes scanning {
          0% {
            background-position: 0 0;
          }
          100% {
            background-position: 40px 0;
          }
        }
      `}</style>
      <div className="flex justify-between gap-4">
        <div className="flex-1 min-w-0 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-text-primary font-mono">
              {port ? (
                <a
                  href={`https://${window.location.hostname}:${port}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 group hover:text-neon-green transition-colors"
                >
                  {name}
                  <svg
                    className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </a>
              ) : (
                <span>{name}</span>
              )}
            </h3>
            <p className="text-xs text-text-muted font-mono mt-1 truncate">
              {image}
            </p>
          </div>
          <div className="text-xs text-text-muted font-mono">
            {port && <span>Port: {port}</span>}
          </div>
        </div>

        <div className="flex flex-col justify-between items-end">
          <div
            className="w-3 h-3 rounded-full animate-pulse flex-shrink-0"
            style={{
              backgroundColor: statusColor,
              boxShadow: `0 0 10px ${statusColor}`,
            }}
          />
          <div className="flex gap-1.5">
            <button
              className={`p-2 rounded transition-all ${
                !isRunning && !isLoading
                  ? "text-neon-green hover:bg-neon-green hover:text-background cursor-pointer"
                  : "text-text-muted cursor-not-allowed opacity-50"
              }`}
              title="Start"
              disabled={isRunning || isLoading}
              onClick={() => onStart?.(container_id)}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </button>
            <button
              className={`p-2 rounded transition-all ${
                isRunning && !isLoading
                  ? "text-neon-red hover:bg-neon-red hover:text-background cursor-pointer"
                  : "text-text-muted cursor-not-allowed opacity-50"
              }`}
              title="Stop"
              disabled={!isRunning || isLoading}
              onClick={() => onStop?.(container_id)}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
                />
              </svg>
            </button>
            <button
              className={`p-2 rounded transition-all ${
                isRunning && !isLoading
                  ? "text-neon-blue hover:bg-neon-blue hover:text-background cursor-pointer"
                  : "text-text-muted cursor-not-allowed opacity-50"
              }`}
              title="Restart"
              disabled={!isRunning || isLoading}
              onClick={() => onRestart?.(container_id)}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
            <button
              className={`p-2 rounded transition-all ${
                !isLoading
                  ? "text-neon-purple hover:bg-neon-purple hover:text-background cursor-pointer"
                  : "text-text-muted cursor-not-allowed opacity-50"
              }`}
              title="Update"
              disabled={isLoading}
              onClick={() => onUpdate?.(container_id)}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            </button>
            <button
              className="p-2 rounded transition-all text-neon-green hover:bg-neon-green hover:text-background cursor-pointer"
              title="View Logs"
              onClick={() => onViewLogs?.(container_id)}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
