const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* ------------------------------------------------------------------ */
/*  Token helpers                                                      */
/* ------------------------------------------------------------------ */

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("sg_token");
}

export function setToken(token: string) {
  localStorage.setItem("sg_token", token);
}

export function clearToken() {
  localStorage.removeItem("sg_token");
}

/* ------------------------------------------------------------------ */
/*  Generic fetch wrapper                                              */
/* ------------------------------------------------------------------ */

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (browser sets multipart boundary)
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || body.error || `API error ${res.status}`);
  }

  return res.json() as Promise<T>;
}

/* ------------------------------------------------------------------ */
/*  Auth                                                               */
/* ------------------------------------------------------------------ */

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: { id: string; name: string; email: string; created_at: string };
}

export async function register(name: string, email: string, password: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getMe() {
  return apiFetch<AuthResponse["user"]>("/api/me");
}

/* ------------------------------------------------------------------ */
/*  Dashboard & Analytics                                               */
/* ------------------------------------------------------------------ */

export interface DashboardStats {
  overview: {
    total_alerts: number;
    unresolved_alerts: number;
    total_detections: number;
    registered_media: number;
    registered_fingerprints: number;
    total_users: number;
    enforcement_actions: number;
  };
  severity: Record<string, number>;
  recent_7_days: {
    alerts: number;
    detections: number;
  };
  enforcement: {
    takedowns: number;
    high_severity_alerts: number;
  };
  top_channels: Array<{ channel: string; violations: number }>;
  generated_at: string;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/api/analytics/dashboard");
}

/* ------------------------------------------------------------------ */
/*  Alerts & Enforcement                                                */
/* ------------------------------------------------------------------ */

export interface Alert {
  _id: string;
  type: string;
  channel_name?: string;
  message_id?: number;
  similarity_score?: number;
  matched_content?: string;
  media_path?: string;
  timestamp?: string;
  severity?: string;
  resolved?: boolean;
  created_at?: string;
}

export async function getAlerts(params?: {
  severity?: string;
  resolved?: boolean;
  limit?: number;
  skip?: number;
}): Promise<Alert[]> {
  const q = new URLSearchParams();
  if (params?.severity) q.set("severity", params.severity);
  if (params?.resolved !== undefined) q.set("resolved", String(params.resolved));
  if (params?.limit) q.set("limit", String(params.limit));
  if (params?.skip) q.set("skip", String(params.skip));
  const qs = q.toString();
  return apiFetch<Alert[]>(`/api/alerts${qs ? `?${qs}` : ""}`);
}

export async function resolveAlert(alertId: string) {
  return apiFetch(`/api/alerts/${alertId}/resolve`, { method: "PATCH" });
}

export async function getAresHistory(limit = 20) {
  const res = await apiFetch<{ logs: any[]; count: number }>(`/api/enforcement/logs?limit=${limit}`);
  return res.logs;
}

/* ------------------------------------------------------------------ */
/*  Telegram                                                           */
/* ------------------------------------------------------------------ */

export async function getTelegramStatus() {
  return apiFetch<{ 
    running: boolean; 
    api_id: string; 
    session_exists: boolean;
    stats: {
      total_matches: number;
      unique_channels: number;
      media_captured: number;
      forensic_storage_mb: number;
      average_confidence: number;
      last_match_time: string;
    }
  }>("/api/telegram/status");
}

export async function startTelegram() {
  return apiFetch("/api/telegram/start-monitor", { method: "POST" });
}

export async function stopTelegram() {
  return apiFetch("/api/telegram/stop-monitor", { method: "POST" });
}

/* ------------------------------------------------------------------ */
/*  Matches / Detections                                               */
/* ------------------------------------------------------------------ */

export async function getMatches(limit = 50, skip = 0) {
  const res = await apiFetch<{ results: any[]; count: number }>(`/api/detection/results?limit=${limit}&skip=${skip}`);
  return res.results;
}

/* ------------------------------------------------------------------ */
/*  ARES Enforcement                                                   */
/* ------------------------------------------------------------------ */

export interface AresInput {
  match_id: string;
  content_id: string;
  match_confidence: number;
  transformation_index: number;
  view_velocity: number;
  platform: string;
  uploader_id: string;
  uploader_reputation: number;
  jurisdiction: string;
  is_commercial: boolean;
}

export interface AresResult {
  action_id: string;
  category: string;
  severity_score: number;
  ai_analysis: {
    model: string;
    reasoning: string;
    parody_probability: number;
    commercial_intent: string;
    suggested_action: string;
  };
  blockchain_hash: string;
}

export async function analyzeAres(data: AresInput): Promise<AresResult> {
  return apiFetch<AresResult>("/api/enforcement/alert", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/* ------------------------------------------------------------------ */
/*  Deepfake Detection                                                 */
/* ------------------------------------------------------------------ */

export interface DeepfakeResult {
  prediction: number;
  probability: number;
  label: string;
  model_available: boolean;
}

export async function predictVideo(file: File): Promise<DeepfakeResult> {
  const fd = new FormData();
  fd.append("file", file);
  return apiFetch<DeepfakeResult>("/api/deepfake/analyze", {
    method: "POST",
    body: fd,
  });
}

/* ------------------------------------------------------------------ */
/*  Content Registration                                               */
/* ------------------------------------------------------------------ */

export async function registerContent(file: File, contentName: string) {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("content_name", contentName);
  return apiFetch<{ status: string; content_name: string; media_type: string; fingerprint_dim: number }>(
    "/api/media/register",
    { method: "POST", body: fd }
  );
}
