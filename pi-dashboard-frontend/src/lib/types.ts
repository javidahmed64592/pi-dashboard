// TypeScript types matching FastAPI Pydantic models

// Base response types
export interface BaseResponse {
  code: number;
  message: string;
  timestamp: string;
}

// Authentication types
export interface AuthContextType {
  apiKey: string | null;
  isAuthenticated: boolean;
  login: (apiKey: string) => Promise<void>;
  logout: () => void;
}

// System types
export interface SystemInfo {
  hostname: string;
  system: string;
  release: string;
  version: string;
  machine: string;
  memory_total: number;
  disk_total: number;
}

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  uptime: number;
  temperature: number;
}

export interface SystemMetricsHistoryEntry {
  metrics: SystemMetrics;
  timestamp: number;
}

export interface SystemMetricsHistory {
  history: SystemMetricsHistoryEntry[];
}

// Response types
export interface HealthResponse extends BaseResponse {
  status: string;
}

export interface LoginResponse extends BaseResponse {}

export interface GetSystemInfoResponse extends BaseResponse {
  info: SystemInfo;
}

export interface GetSystemMetricsResponse extends BaseResponse {
  metrics: SystemMetrics;
}

export interface GetSystemMetricsHistoryResponse extends BaseResponse {
  history: SystemMetricsHistory;
}

// Request types
export interface GetSystemMetricsHistoryRequest {
  last_n_seconds: number;
}
