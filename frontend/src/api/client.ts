// Thin typed API client for the APIlytics backend.
// Base URL comes from VITE_API_BASE_URL (see frontend/.env.example).

import type {
  AlertsResponse,
  DevContext,
  EndpointsResponse,
  SummaryResponse,
  Window,
} from "../types/api";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    let detail: string;
    try {
      const body = await res.json();
      detail = typeof body?.detail === "string"
        ? body.detail
        : JSON.stringify(body?.detail ?? body);
    } catch {
      detail = await res.text();
    }
    throw new Error(`HTTP ${res.status} ${path}: ${detail.slice(0, 200)}`);
  }
  return (await res.json()) as T;
}

export const api = {
  baseUrl: BASE_URL,

  health: () => getJSON<{ status: string }>("/health"),

  devContext: () => getJSON<DevContext>("/api/v1/dev/context"),

  summary: (window: Window, projectId: string) =>
    getJSON<SummaryResponse>(
      `/api/v1/summary?window=${window}&project_id=${projectId}`,
    ),

  endpoints: (window: Window, projectId: string, limit = 20) =>
    getJSON<EndpointsResponse>(
      `/api/v1/endpoints?window=${window}&limit=${limit}&project_id=${projectId}`,
    ),

  alerts: (window: Window, projectId: string, limit = 50) =>
    getJSON<AlertsResponse>(
      `/api/v1/alerts?window=${window}&limit=${limit}&project_id=${projectId}`,
    ),
};
