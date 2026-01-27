"use client";

import { useEffect, useState } from "react";

import ContainerCard from "@/components/dashboard/ContainerCard";
import {
  getContainers,
  refreshContainers,
  startContainer,
  stopContainer,
  restartContainer,
  updateContainer,
} from "@/lib/api";
import type { DockerContainer } from "@/lib/types";

export default function ContainerWidget() {
  const [containers, setContainers] = useState<DockerContainer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadContainers = async () => {
    try {
      setError(null);
      const response = await getContainers();

      // Sort containers: running first (by port ascending), then offline
      const sortedContainers = [...response.containers].sort((a, b) => {
        const aIsRunning = a.status === "running";
        const bIsRunning = b.status === "running";

        // If one is running and the other isn't, running comes first
        if (aIsRunning && !bIsRunning) return -1;
        if (!aIsRunning && bIsRunning) return 1;

        // Both have same running status, sort by port number
        const aPort =
          a.ports.length > 0 && a.ports[0] && a.ports[0].host
            ? parseInt(a.ports[0].host)
            : 99999;
        const bPort =
          b.ports.length > 0 && b.ports[0] && b.ports[0].host
            ? parseInt(b.ports[0].host)
            : 99999;

        return aPort - bPort;
      });

      setContainers(sortedContainers);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load containers"
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadContainers();
    // Refresh containers every 30 seconds
    const interval = setInterval(loadContainers, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async (id: string) => {
    try {
      await startContainer(id);
      await loadContainers();
    } catch (err) {
      console.error("Failed to start container:", err);
    }
  };

  const handleStop = async (id: string) => {
    try {
      await stopContainer(id);
      await loadContainers();
    } catch (err) {
      console.error("Failed to stop container:", err);
    }
  };

  const handleRestart = async (id: string) => {
    try {
      await restartContainer(id);
      await loadContainers();
    } catch (err) {
      console.error("Failed to restart container:", err);
    }
  };

  const handleUpdate = async (id: string) => {
    try {
      await updateContainer(id);
      await loadContainers();
    } catch (err) {
      console.error("Failed to update container:", err);
    }
  };

  const handleRefresh = async () => {
    try {
      setIsLoading(true);
      const response = await refreshContainers();

      // Sort containers after refresh
      const sortedContainers = [...response.containers].sort((a, b) => {
        const aIsRunning = a.status === "running";
        const bIsRunning = b.status === "running";

        if (aIsRunning && !bIsRunning) return -1;
        if (!aIsRunning && bIsRunning) return 1;

        const aPort =
          a.ports.length > 0 && a.ports[0] && a.ports[0].host
            ? parseInt(a.ports[0].host)
            : 99999;
        const bPort =
          b.ports.length > 0 && b.ports[0] && b.ports[0].host
            ? parseInt(b.ports[0].host)
            : 99999;

        return aPort - bPort;
      });

      setContainers(sortedContainers);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to refresh containers"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-neon-green font-mono">
          CONTAINERS
        </h2>
        <button
          onClick={handleRefresh}
          disabled={isLoading}
          className="p-2 text-neon-blue hover:bg-neon-blue hover:text-background rounded transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          title="Refresh containers"
        >
          <svg
            className={`w-5 h-5 ${isLoading ? "animate-spin" : ""}`}
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
      <div className="space-y-3 overflow-y-auto flex-1">
        {isLoading && containers.length === 0 ? (
          <div className="text-text-muted font-mono text-sm">
            Loading containers...
          </div>
        ) : error ? (
          <div className="text-neon-red font-mono text-sm">{error}</div>
        ) : containers.length === 0 ? (
          <div className="text-text-muted font-mono text-sm">
            No containers found
          </div>
        ) : (
          containers.map(container => (
            <ContainerCard
              key={container.container_id}
              container_id={container.container_id}
              name={container.name}
              image={container.image}
              status={
                container.status as
                  | "running"
                  | "exited"
                  | "created"
                  | "restarting"
                  | "paused"
              }
              ports={container.ports}
              onStart={handleStart}
              onStop={handleStop}
              onRestart={handleRestart}
              onUpdate={handleUpdate}
            />
          ))
        )}
      </div>
    </div>
  );
}
