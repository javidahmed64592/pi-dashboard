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

// Notes types
export interface Note {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface NotesCollection {
  notes: Note[];
}

// Weather types
export interface WeatherForecastHour {
  time: string;
  temperature: number;
  weather_code: number;
}

export interface WeatherData {
  location_name: string;
  temperature: number;
  weather_code: number;
  high: number;
  low: number;
  humidity: number;
  wind_speed: number;
  forecast: WeatherForecastHour[];
}
// Container types
export interface DockerContainer {
  container_id: string;
  name: string;
  image: string;
  status: string;
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
  history: SystemMetricsHistory;
}

export interface GetNotesResponse extends BaseResponse {
  notes: NotesCollection;
}

export interface CreateNoteResponse extends BaseResponse {
  note: Note;
}

export interface UpdateNoteResponse extends BaseResponse {
  note: Note;
}

export interface DeleteNoteResponse extends BaseResponse {}

export interface GetWeatherResponse extends BaseResponse {
  weather: WeatherData;
}

export interface GetWeatherLocationResponse extends BaseResponse {
  location_name: string;
  latitude: number;
  longitude: number;
}

export interface GetContainersResponse extends BaseResponse {
  containers: DockerContainer[];
}

export interface ContainerActionResponse extends BaseResponse {
  container_id: string;
}

// Request types
export interface GetSystemMetricsHistoryRequest {
  last_n_seconds: number;
}

export interface CreateNoteRequest {
  title: string;
  content: string;
}

export interface UpdateNoteRequest {
  title?: string;
  content?: string;
}

export interface UpdateWeatherLocationRequest {
  location: string;
}
