// TypeScript types matching FastAPI Pydantic models

// Base response types
export interface BaseResponse {
  code: number;
  message: string;
  timestamp: string;
}

// Authentication types
export interface LoginResponse extends BaseResponse {}

export interface AuthContextType {
  apiKey: string | null;
  isAuthenticated: boolean;
  login: (apiKey: string) => Promise<void>;
  logout: () => void;
}

// Response types
export interface HealthResponse extends BaseResponse {
  status: string;
}
