/**
 * Shared TypeScript types matching backend API contracts.
 */

// --- Enums ---

export type TaskStatus = "pending" | "completed";
export type TaskPriority = "high" | "medium" | "low";
export type MessageRole = "user" | "assistant" | "system";

// --- Recurrence ---

export interface RecurrencePattern {
  type: "daily" | "weekly" | "monthly" | "custom";
  days_of_week?: number[];
  day_of_month?: number;
  interval_days?: number;
  parent_task_id?: number | null;
}

// --- Task ---

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  tags: string[];
  due_date: string | null;
  is_recurring: boolean;
  recurrence_pattern: RecurrencePattern | null;
  reminder_offset: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface TaskCreateInput {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string | null;
  reminder_offset?: string | null;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern | null;
}

export interface TaskUpdateInput {
  title?: string | null;
  description?: string | null;
  priority?: TaskPriority | null;
  tags?: string[] | null;
  due_date?: string | null;
  reminder_offset?: string | null;
  is_recurring?: boolean | null;
  recurrence_pattern?: RecurrencePattern | null;
}

// --- Tag ---

export interface Tag {
  id: number;
  name: string;
  task_count: number;
}

// --- Completion ---

export interface CompletionRecord {
  id: number;
  completed_at: string;
  completed_by: string;
}

// --- Chat ---

export interface ChatMessage {
  role: MessageRole;
  content: string;
  created_at?: string;
}

export interface ChatAction {
  tool: string;
  result: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  actions_taken: ChatAction[];
}

// --- Paginated Response ---

export interface PaginatedTasks {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
}

// --- Task Filters ---

export interface TaskFilters {
  q?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  tags?: string[];
  due_from?: string;
  due_to?: string;
  sort_by?: "created_at" | "due_date" | "priority" | "title";
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}
