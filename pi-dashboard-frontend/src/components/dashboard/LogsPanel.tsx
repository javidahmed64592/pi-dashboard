"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { getContainerLogs } from "@/lib/api";
import type { LogSource } from "@/lib/types";

const LINE_OPTIONS = [100, 250, 500, 1000] as const;
const AUTO_REFRESH_INTERVAL_MS = 10_000;

interface LogsPanelProps {
  source: LogSource | null;
}

export default function LogsPanel({ source }: LogsPanelProps) {
  const [lines, setLines] = useState<number>(100);
  const [logs, setLogs] = useState<string[]>([]);
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const logAreaRef = useRef<HTMLDivElement>(null);

  const fetchLogs = useCallback(
    async (logSource: LogSource, lineCount: number) => {
      setIsLoadingLogs(true);
      setError(null);
      try {
        if (logSource.type === "docker") {
          const response = await getContainerLogs(
            logSource.containerId,
            lineCount
          );
          setLogs(response.logs);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch logs");
      } finally {
        setIsLoadingLogs(false);
      }
    },
    []
  );

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (logAreaRef.current) {
      logAreaRef.current.scrollTop = logAreaRef.current.scrollHeight;
    }
  }, [logs]);

  // Clear logs when source changes
  useEffect(() => {
    setLogs([]);
    setError(null);
  }, [source]);

  // Fetch on source or lines change
  useEffect(() => {
    if (!source) return;
    fetchLogs(source, lines);
  }, [source, lines, fetchLogs]);

  // Auto-refresh
  useEffect(() => {
    if (!source) return;
    const interval = setInterval(() => {
      fetchLogs(source, lines);
    }, AUTO_REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [source, lines, fetchLogs]);

  const handleRefresh = () => {
    if (source) fetchLogs(source, lines);
  };

  const handleLinesChange = (value: number) => {
    setLogs([]);
    setLines(value);
  };

  return (
    <div className="bg-background-secondary border border-border rounded-lg shadow-neon flex flex-col h-full min-h-64">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border flex-shrink-0">
        <h2 className="text-sm font-bold text-neon-green font-mono tracking-widest uppercase truncate min-w-0">
          Logs
          {source && (
            <span className="text-text-muted normal-case tracking-normal font-normal">
              {" "}
              — {source.containerName}
            </span>
          )}
        </h2>
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="flex gap-1">
            {LINE_OPTIONS.map(n => (
              <button
                key={n}
                onClick={() => handleLinesChange(n)}
                className={`px-2 py-1 rounded border transition-all font-mono text-xs ${
                  lines === n
                    ? "bg-neon-green text-background border-neon-green"
                    : "bg-background text-text-primary border-border hover:border-neon-green"
                }`}
                aria-label={`Show ${n} lines`}
              >
                {n}
              </button>
            ))}
          </div>
          <button
            onClick={handleRefresh}
            disabled={!source || isLoadingLogs}
            className={`p-1.5 rounded transition-all ${
              source && !isLoadingLogs
                ? "text-neon-blue hover:bg-neon-blue hover:text-background cursor-pointer"
                : "text-text-muted cursor-not-allowed opacity-50"
            }`}
            title="Refresh logs"
            aria-label="Refresh logs"
          >
            <svg
              className={`w-4 h-4 ${isLoadingLogs ? "animate-spin" : ""}`}
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
        </div>
      </div>

      {/* Log output */}
      <div
        ref={logAreaRef}
        className="flex-1 overflow-y-auto p-3 font-mono text-xs leading-relaxed min-h-0 bg-background"
        style={{ scrollbarWidth: "thin" }}
        aria-live="polite"
        aria-label="Log output"
      >
        {error ? (
          <p className="text-neon-red">{error}</p>
        ) : !source ? (
          <p className="text-text-muted">Select a container to view logs.</p>
        ) : isLoadingLogs && logs.length === 0 ? (
          <p className="text-text-muted animate-pulse">Loading logs…</p>
        ) : logs.length === 0 ? (
          <p className="text-text-muted">No log output.</p>
        ) : (
          logs.map((line, idx) => (
            <div
              key={idx}
              className="text-text-primary whitespace-pre-wrap break-all"
            >
              {line}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
