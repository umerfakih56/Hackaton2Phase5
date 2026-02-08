"use client";

import { useCallback, useEffect, useState } from "react";
import {
  completeTask,
  createTask,
  deleteTask,
  getDashboardStats,
  listTasks,
  reopenTask,
  type DashboardStats,
} from "@/lib/api-client";
import { FilterPanel } from "@/components/tasks/filter-panel";
import { SearchBar } from "@/components/tasks/search-bar";
import { TaskForm } from "@/components/tasks/task-form";
import { TaskList } from "@/components/tasks/task-list";
import type { Task, TaskCreateInput, TaskFilters } from "@/lib/types";

const STAT_CARDS = [
  { key: "total", label: "Total", color: "bg-blue-50 text-blue-700" },
  { key: "pending", label: "Pending", color: "bg-yellow-50 text-yellow-700" },
  { key: "completed", label: "Completed", color: "bg-green-50 text-green-700" },
  { key: "overdue", label: "Overdue", color: "bg-red-50 text-red-700" },
  { key: "high_priority", label: "High Priority", color: "bg-orange-50 text-orange-700" },
] as const;

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [formLoading, setFormLoading] = useState(false);
  const [filters, setFilters] = useState<TaskFilters>({
    sort_by: "created_at",
    sort_order: "desc",
  });

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      const [taskResult, statsResult] = await Promise.all([
        listTasks(filters),
        getDashboardStats(),
      ]);
      setTasks(taskResult.tasks);
      setTotal(taskResult.total);
      setStats(statsResult);
    } catch {
      // User may not be authenticated yet
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleSearch = useCallback((q: string) => {
    setFilters((prev) => ({ ...prev, q: q || undefined }));
  }, []);

  async function handleCreate(data: TaskCreateInput) {
    setFormLoading(true);
    try {
      await createTask(data);
      await fetchAll();
    } finally {
      setFormLoading(false);
    }
  }

  async function handleComplete(taskId: number) {
    await completeTask(taskId);
    await fetchAll();
  }

  async function handleReopen(taskId: number) {
    await reopenTask(taskId);
    await fetchAll();
  }

  async function handleDelete(taskId: number) {
    await deleteTask(taskId);
    await fetchAll();
  }

  function applyQuickFilter(preset: string) {
    const today = new Date();
    const todayStr = today.toISOString().split("T")[0];

    switch (preset) {
      case "today": {
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        setFilters((prev) => ({
          ...prev,
          due_from: todayStr,
          due_to: tomorrow.toISOString().split("T")[0],
          status: "pending",
        }));
        break;
      }
      case "week": {
        const weekEnd = new Date(today);
        weekEnd.setDate(weekEnd.getDate() + 7);
        setFilters((prev) => ({
          ...prev,
          due_from: todayStr,
          due_to: weekEnd.toISOString().split("T")[0],
          status: "pending",
        }));
        break;
      }
      case "high":
        setFilters((prev) => ({
          ...prev,
          priority: "high",
          status: "pending",
          due_from: undefined,
          due_to: undefined,
        }));
        break;
      case "all":
        setFilters({ sort_by: "created_at", sort_order: "desc" });
        break;
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Dashboard</h2>
      </div>

      {/* Stat Cards */}
      {stats && (
        <div className="mb-6 grid grid-cols-5 gap-3">
          {STAT_CARDS.map(({ key, label, color }) => (
            <div key={key} className={`rounded-lg p-3 text-center ${color}`}>
              <div className="text-2xl font-bold">
                {stats[key as keyof DashboardStats]}
              </div>
              <div className="text-xs font-medium">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Filters */}
      <div className="mb-4 flex gap-2">
        {[
          { key: "all", label: "All Tasks" },
          { key: "today", label: "Due Today" },
          { key: "week", label: "This Week" },
          { key: "high", label: "High Priority" },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => applyQuickFilter(key)}
            className="rounded-full border border-gray-300 px-3 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50"
          >
            {label}
          </button>
        ))}
      </div>

      <TaskForm onSubmit={handleCreate} loading={formLoading} />

      <div className="mt-4">
        <SearchBar onSearch={handleSearch} />
      </div>

      <div className="mt-3">
        <FilterPanel filters={filters} onChange={setFilters} />
      </div>

      <div className="mt-4">
        <p className="mb-2 text-sm text-gray-500">{total} tasks found</p>
        {loading ? (
          <div className="py-12 text-center text-gray-400">Loading tasks...</div>
        ) : (
          <TaskList
            tasks={tasks}
            onComplete={handleComplete}
            onReopen={handleReopen}
            onDelete={handleDelete}
          />
        )}
      </div>
    </div>
  );
}
