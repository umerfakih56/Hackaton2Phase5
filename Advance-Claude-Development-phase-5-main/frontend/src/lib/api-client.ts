/**
 * API client for the Todo Chatbot backend.
 *
 * All requests go through the FastAPI backend; no direct Kafka/Dapr
 * access from the frontend (per constitution Principle 4).
 */

import { BACKEND_URL, getAuthHeaders, getUserId } from "./auth";
import type {
  ChatResponse,
  CompletionRecord,
  PaginatedTasks,
  Tag,
  Task,
  TaskCreateInput,
  TaskFilters,
  TaskUpdateInput,
} from "./types";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function requireUserId(): string {
  const userId = getUserId();
  if (!userId) throw new ApiError(401, "Not authenticated");
  return userId;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const userId = requireUserId();
  const url = `${BACKEND_URL}${path}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(userId),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(res.status, body);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Tasks ──────────────────────────────────────────────

export async function listTasks(
  filters: TaskFilters = {},
): Promise<PaginatedTasks> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value === undefined || value === null) continue;
    if (Array.isArray(value)) {
      for (const v of value) params.append(key, v);
    } else {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return request<PaginatedTasks>(`/api/tasks${qs ? `?${qs}` : ""}`);
}

export async function getTask(taskId: number): Promise<Task> {
  return request<Task>(`/api/tasks/${taskId}`);
}

export async function createTask(data: TaskCreateInput): Promise<Task> {
  return request<Task>("/api/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTask(
  taskId: number,
  data: TaskUpdateInput,
): Promise<Task> {
  return request<Task>(`/api/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function completeTask(taskId: number): Promise<Task> {
  return request<Task>(`/api/tasks/${taskId}/complete`, { method: "POST" });
}

export async function reopenTask(taskId: number): Promise<Task> {
  return request<Task>(`/api/tasks/${taskId}/reopen`, { method: "POST" });
}

export async function deleteTask(taskId: number): Promise<void> {
  return request<void>(`/api/tasks/${taskId}`, { method: "DELETE" });
}

// ── Dashboard ─────────────────────────────────────────

export interface DashboardStats {
  total: number;
  pending: number;
  completed: number;
  overdue: number;
  high_priority: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return request<DashboardStats>("/api/tasks/dashboard");
}

// ── Tags ───────────────────────────────────────────────

export async function listTags(q?: string): Promise<{ tags: Tag[] }> {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  return request<{ tags: Tag[] }>(`/api/tags${qs}`);
}

// ── Completions ────────────────────────────────────────

export async function getCompletions(
  taskId: number,
): Promise<{ completions: CompletionRecord[] }> {
  return request<{ completions: CompletionRecord[] }>(
    `/api/tasks/${taskId}/completions`,
  );
}

// ── Chat ───────────────────────────────────────────────

export async function sendChatMessage(
  message: string,
  conversationId?: string | null,
): Promise<ChatResponse> {
  const userId = requireUserId();
  return request<ChatResponse>(`/api/${userId}/chat`, {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId ?? null }),
  });
}
