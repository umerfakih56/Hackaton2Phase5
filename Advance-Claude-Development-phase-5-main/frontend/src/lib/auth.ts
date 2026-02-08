/**
 * Better Auth client configuration.
 *
 * Phase V simplified: accepts a UUID token as the user identifier.
 * In production, Better Auth handles full JWT validation.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

/** Return auth headers for API calls. */
export function getAuthHeaders(userId: string): Record<string, string> {
  return {
    Authorization: `Bearer ${userId}`,
    "Content-Type": "application/json",
  };
}

/** Retrieve the stored user ID from localStorage. */
export function getUserId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("todo_user_id");
}

/** Persist a user ID to localStorage. */
export function setUserId(userId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("todo_user_id", userId);
}

/** Clear stored auth state. */
export function clearAuth(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("todo_user_id");
}

export { BACKEND_URL };
