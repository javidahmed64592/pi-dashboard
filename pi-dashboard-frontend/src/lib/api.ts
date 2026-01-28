import axios from "axios";
import { useEffect, useState } from "react";

import { getApiKey } from "@/lib/auth";
import type {
  HealthResponse,
  LoginResponse,
  GetSystemInfoResponse,
  GetSystemMetricsResponse,
  GetSystemMetricsHistoryRequest,
  GetSystemMetricsHistoryResponse,
  GetNotesResponse,
  CreateNoteRequest,
  CreateNoteResponse,
  UpdateNoteRequest,
  UpdateNoteResponse,
  DeleteNoteResponse,
  GetWeatherResponse,
  GetWeatherLocationResponse,
  UpdateWeatherLocationRequest,
  GetContainersResponse,
  ContainerActionResponse,
} from "@/lib/types";

// Determine the base URL based on environment
const getBaseURL = () => {
  if (typeof window === "undefined") return "";

  // In production static build, API is served from same origin
  if (process.env.NODE_ENV === "production") {
    return window.location.origin;
  }

  // In development, proxy to backend (handled by Next.js rewrites)
  return "";
};

// API client configuration
const api = axios.create({
  baseURL: getBaseURL() + "/api", // This will be proxied in dev, direct in production
  timeout: 60000, // 60 seconds timeout for LLM responses
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include API key
api.interceptors.request.use(
  config => {
    const apiKey = getApiKey();
    if (apiKey) {
      config.headers["X-API-KEY"] = apiKey;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Health status type
export type HealthStatus = "online" | "offline" | "checking";

const extractErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      const errorData = error.response.data;

      // Check for BaseResponse format with message field
      if (errorData?.message) {
        return errorData.message;
      }

      // Check for detail field (common in FastAPI errors)
      if (errorData?.detail) {
        return typeof errorData.detail === "string"
          ? errorData.detail
          : JSON.stringify(errorData.detail);
      }

      // Fallback to generic server error
      return `Server error: ${error.response.status} ${error.response.statusText}`;
    } else if (error.request) {
      return "No response from server. Please check if the backend is running.";
    } else {
      return `Request failed: ${error.message}`;
    }
  }
  return "An unexpected error occurred";
};

// API functions
export const getHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>("/health");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const login = async (apiKey: string): Promise<LoginResponse> => {
  try {
    const response = await api.get<LoginResponse>("/login", {
      headers: {
        "X-API-KEY": apiKey,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

// System API functions
export const getSystemInfo = async (): Promise<GetSystemInfoResponse> => {
  try {
    const response = await api.get<GetSystemInfoResponse>("/system/info");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const getSystemMetrics = async (): Promise<GetSystemMetricsResponse> => {
  try {
    const response = await api.get<GetSystemMetricsResponse>("/system/metrics");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const getSystemMetricsHistory = async (
  request: GetSystemMetricsHistoryRequest
): Promise<GetSystemMetricsHistoryResponse> => {
  try {
    const response = await api.post<GetSystemMetricsHistoryResponse>(
      "/system/metrics/history",
      request
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

// Notes API functions
export const getNotes = async (): Promise<GetNotesResponse> => {
  try {
    const response = await api.get<GetNotesResponse>("/notes");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const createNote = async (
  request: CreateNoteRequest
): Promise<CreateNoteResponse> => {
  try {
    const response = await api.post<CreateNoteResponse>("/notes", request);
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const updateNote = async (
  noteId: string,
  request: UpdateNoteRequest
): Promise<UpdateNoteResponse> => {
  try {
    const response = await api.put<UpdateNoteResponse>(
      `/notes/${noteId}`,
      request
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const deleteNote = async (
  noteId: string
): Promise<DeleteNoteResponse> => {
  try {
    const response = await api.delete<DeleteNoteResponse>(`/notes/${noteId}`);
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

// Weather API functions
export const getWeather = async (): Promise<GetWeatherResponse> => {
  try {
    const response = await api.get<GetWeatherResponse>("/weather");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const getWeatherLocation =
  async (): Promise<GetWeatherLocationResponse> => {
    try {
      const response =
        await api.get<GetWeatherLocationResponse>("/weather/location");
      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  };

export const updateWeatherLocation = async (
  request: UpdateWeatherLocationRequest
): Promise<GetWeatherLocationResponse> => {
  try {
    const response = await api.put<GetWeatherLocationResponse>(
      "/weather/location",
      request
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

// Container API functions
export const getContainers = async (): Promise<GetContainersResponse> => {
  try {
    const response = await api.get<GetContainersResponse>("/containers");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const refreshContainers = async (): Promise<GetContainersResponse> => {
  try {
    const response = await api.post<GetContainersResponse>(
      "/containers/refresh"
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const startContainer = async (
  containerId: string
): Promise<ContainerActionResponse> => {
  try {
    const response = await api.post<ContainerActionResponse>(
      `/containers/${containerId}/start`
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const stopContainer = async (
  containerId: string
): Promise<ContainerActionResponse> => {
  try {
    const response = await api.post<ContainerActionResponse>(
      `/containers/${containerId}/stop`
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const restartContainer = async (
  containerId: string
): Promise<ContainerActionResponse> => {
  try {
    const response = await api.post<ContainerActionResponse>(
      `/containers/${containerId}/restart`
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const updateContainer = async (
  containerId: string
): Promise<ContainerActionResponse> => {
  try {
    const response = await api.post<ContainerActionResponse>(
      `/containers/${containerId}/update`
    );
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

// Health status hook
export function useHealthStatus(): HealthStatus {
  const [status, setStatus] = useState<HealthStatus>("checking");

  useEffect(() => {
    let isMounted = true;

    const checkHealth = async () => {
      try {
        await getHealth();
        if (isMounted) {
          setStatus("online");
        }
      } catch {
        if (isMounted) {
          setStatus("offline");
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // every 30s
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return status;
}

export default api;
