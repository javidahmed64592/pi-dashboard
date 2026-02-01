"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";

import {
  getSystemInfo,
  getSystemMetrics,
  getSystemMetricsHistory,
} from "@/lib/api";
import type {
  SystemInfo,
  SystemMetrics,
  SystemMetricsHistory,
} from "@/lib/types";

import { useAuth } from "./AuthContext";

interface SystemContextType {
  systemInfo: SystemInfo | null;
  currentMetrics: SystemMetrics | null;
  metricsHistory: SystemMetricsHistory | null;
  isLoading: boolean;
  error: string | null;
  refreshHistory: (timeRangeSeconds: number) => Promise<void>;
}

const SystemContext = createContext<SystemContextType | undefined>(undefined);

export function SystemProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [currentMetrics, setCurrentMetrics] = useState<SystemMetrics | null>(
    null
  );
  const [metricsHistory, setMetricsHistory] =
    useState<SystemMetricsHistory | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch system info when authenticated, clear when not
  useEffect(() => {
    if (!isAuthenticated) {
      setSystemInfo(null);
      setIsLoading(false);
      return;
    }

    const fetchSystemInfo = async () => {
      try {
        const response = await getSystemInfo();
        setSystemInfo(response.info);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch system info"
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchSystemInfo();
  }, [isAuthenticated]);

  // Poll current metrics every 5 seconds (only when authenticated)
  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    const fetchMetrics = async () => {
      try {
        const response = await getSystemMetrics();
        setCurrentMetrics(response.metrics);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch metrics"
        );
      }
    };

    // Fetch immediately
    fetchMetrics();

    const interval = setInterval(fetchMetrics, 5000);

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  // Function to refresh history (called from system page)
  const refreshHistory = useCallback(async (timeRangeSeconds: number) => {
    try {
      const response = await getSystemMetricsHistory({
        last_n_seconds: timeRangeSeconds,
      });
      setMetricsHistory(response.history);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch history");
    }
  }, []);

  const value: SystemContextType = {
    systemInfo,
    currentMetrics,
    metricsHistory,
    isLoading,
    error,
    refreshHistory,
  };

  return (
    <SystemContext.Provider value={value}>{children}</SystemContext.Provider>
  );
}

export function useSystem(): SystemContextType {
  const context = useContext(SystemContext);
  if (context === undefined) {
    throw new Error("useSystem must be used within a SystemProvider");
  }
  return context;
}
