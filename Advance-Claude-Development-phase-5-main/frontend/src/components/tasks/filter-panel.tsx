"use client";

import type { TaskFilters, TaskPriority, TaskStatus } from "@/lib/types";

interface FilterPanelProps {
  filters: TaskFilters;
  onChange: (filters: TaskFilters) => void;
}

export function FilterPanel({ filters, onChange }: FilterPanelProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Status */}
      <select
        value={filters.status ?? ""}
        onChange={(e) =>
          onChange({
            ...filters,
            status: (e.target.value as TaskStatus) || undefined,
          })
        }
        className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
      >
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="completed">Completed</option>
      </select>

      {/* Priority */}
      <select
        value={filters.priority ?? ""}
        onChange={(e) =>
          onChange({
            ...filters,
            priority: (e.target.value as TaskPriority) || undefined,
          })
        }
        className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
      >
        <option value="">All Priorities</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>

      {/* Sort */}
      <select
        value={filters.sort_by ?? "created_at"}
        onChange={(e) =>
          onChange({
            ...filters,
            sort_by: e.target.value as TaskFilters["sort_by"],
          })
        }
        className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
      >
        <option value="created_at">Sort: Created</option>
        <option value="due_date">Sort: Due Date</option>
        <option value="priority">Sort: Priority</option>
        <option value="title">Sort: Title</option>
      </select>

      <button
        onClick={() =>
          onChange({
            ...filters,
            sort_order: filters.sort_order === "asc" ? "desc" : "asc",
          })
        }
        className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
      >
        {filters.sort_order === "asc" ? "Asc" : "Desc"}
      </button>

      {/* Due date range */}
      <input
        type="date"
        value={filters.due_from ?? ""}
        onChange={(e) =>
          onChange({ ...filters, due_from: e.target.value || undefined })
        }
        className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
        placeholder="Due from"
      />
      <input
        type="date"
        value={filters.due_to ?? ""}
        onChange={(e) =>
          onChange({ ...filters, due_to: e.target.value || undefined })
        }
        className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
        placeholder="Due to"
      />
    </div>
  );
}
