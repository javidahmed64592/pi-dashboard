// TypeScript types matching FastAPI Pydantic models

// Base response types
export interface BaseResponse {
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

// Database
export enum DatabaseAction {
  CREATE = "create",
  UPDATE = "update",
  DELETE = "delete",
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
  id: number | null;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  uptime: number;
  temperature: number;
  timestamp: number;
}

// Note types
export interface NoteEntry {
  id: number | null;
  title: string;
  content: string;
  time_created: number;
  time_updated: number;
}

// Container types
export type DockerContainerStatus =
  | "running"
  | "stopped"
  | "restarting"
  | "exited"
  | "paused"
  | "dead";

export interface DockerContainer {
  container_id: string;
  name: string;
  image: string;
  status: DockerContainerStatus;
  port: string | null;
}

// Response types
export interface HealthResponse extends BaseResponse {}

export interface LoginResponse extends BaseResponse {}

export interface GetSystemInfoResponse extends BaseResponse {
  info: SystemInfo;
}

export interface GetSystemMetricsResponse extends BaseResponse {
  metrics: SystemMetrics;
}

export interface GetSystemMetricsHistoryResponse extends BaseResponse {
  history: SystemMetrics[];
}

export interface NotesListResponse extends BaseResponse {
  notes: NoteEntry[];
}

export interface NotesActionResponse extends BaseResponse {
  note_id: number;
}

export interface GetContainersResponse extends BaseResponse {
  containers: DockerContainer[];
}

export interface DockerContainerActionResponse extends BaseResponse {
  container_id: string;
}

export interface DockerContainerLogsResponse extends BaseResponse {
  container_id: string;
  logs: string[];
}

// Log source types
// Designed to be extended: add more source types here as they become available
// (e.g. "systemd" for journald logs, "file" for plain log files, etc.)
export type LogSourceType = "docker";

export interface DockerLogSource {
  type: "docker";
  containerId: string;
  containerName: string;
}

// Union type — add new source shapes here when extending the log panel
export type LogSource = DockerLogSource;

// Request types
export interface GetSystemMetricsHistoryRequest {
  last_n_seconds: number;
  max_data_points: number;
}

export interface NotesActionRequest {
  action: DatabaseAction;
  note: NoteEntry;
}
