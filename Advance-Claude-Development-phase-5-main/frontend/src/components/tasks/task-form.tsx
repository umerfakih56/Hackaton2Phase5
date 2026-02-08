"use client";

import { useState } from "react";
import type { TaskCreateInput, TaskPriority } from "@/lib/types";

interface TaskFormProps {
  onSubmit: (data: TaskCreateInput) => void;
  loading?: boolean;
}

export function TaskForm({ onSubmit, loading }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [tagsInput, setTagsInput] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [reminderOffset, setReminderOffset] = useState("");
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrenceType, setRecurrenceType] = useState<"daily" | "weekly" | "monthly" | "custom">("daily");
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>([]);
  const [dayOfMonth, setDayOfMonth] = useState(1);
  const [intervalDays, setIntervalDays] = useState(2);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;

    const tags = tagsInput
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    let recurrence_pattern = null;
    if (isRecurring) {
      if (recurrenceType === "daily") recurrence_pattern = { type: "daily" as const };
      else if (recurrenceType === "weekly") recurrence_pattern = { type: "weekly" as const, days_of_week: daysOfWeek };
      else if (recurrenceType === "monthly") recurrence_pattern = { type: "monthly" as const, day_of_month: dayOfMonth };
      else recurrence_pattern = { type: "custom" as const, interval_days: intervalDays };
    }

    onSubmit({
      title: title.trim(),
      description: description.trim() || null,
      priority,
      tags: tags.length > 0 ? tags : undefined,
      due_date: dueDate ? new Date(dueDate).toISOString() : null,
      reminder_offset: reminderOffset || null,
      is_recurring: isRecurring || undefined,
      recurrence_pattern,
    });

    setTitle("");
    setDescription("");
    setPriority("medium");
    setTagsInput("");
    setDueDate("");
    setReminderOffset("");
    setIsRecurring(false);
    setRecurrenceType("daily");
    setDaysOfWeek([]);
    setDayOfMonth(1);
    setIntervalDays(2);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-gray-200 bg-white p-4">
      <div>
        <input
          type="text"
          placeholder="Task title..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          required
        />
      </div>

      <div>
        <textarea
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        />
      </div>

      <div className="flex gap-3">
        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Priority
          </label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          >
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            placeholder="work, urgent"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="flex gap-3">
        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Due Date
          </label>
          <input
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Reminder
          </label>
          <select
            value={reminderOffset}
            onChange={(e) => setReminderOffset(e.target.value)}
            disabled={!dueDate}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none disabled:opacity-50"
          >
            <option value="">No reminder</option>
            <option value="15m">15 minutes before</option>
            <option value="30m">30 minutes before</option>
            <option value="1h">1 hour before</option>
            <option value="2h">2 hours before</option>
            <option value="1d">1 day before</option>
          </select>
        </div>
      </div>

      {/* Recurrence */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-xs font-medium text-gray-600">
          <input
            type="checkbox"
            checked={isRecurring}
            onChange={(e) => setIsRecurring(e.target.checked)}
            className="rounded border-gray-300"
          />
          Recurring task
        </label>

        {isRecurring && (
          <div className="flex gap-3 rounded-md border border-gray-200 bg-gray-50 p-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Pattern</label>
              <select
                value={recurrenceType}
                onChange={(e) => setRecurrenceType(e.target.value as typeof recurrenceType)}
                className="rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="custom">Custom interval</option>
              </select>
            </div>

            {recurrenceType === "weekly" && (
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Days</label>
                <div className="flex gap-1">
                  {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map((day, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() =>
                        setDaysOfWeek((prev) =>
                          prev.includes(i) ? prev.filter((d) => d !== i) : [...prev, i]
                        )
                      }
                      className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                        daysOfWeek.includes(i)
                          ? "bg-blue-600 text-white"
                          : "bg-gray-200 text-gray-600"
                      }`}
                    >
                      {day}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {recurrenceType === "monthly" && (
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Day of month</label>
                <input
                  type="number"
                  min={1}
                  max={31}
                  value={dayOfMonth}
                  onChange={(e) => setDayOfMonth(Number(e.target.value))}
                  className="w-16 rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            )}

            {recurrenceType === "custom" && (
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Every N days</label>
                <input
                  type="number"
                  min={1}
                  value={intervalDays}
                  onChange={(e) => setIntervalDays(Number(e.target.value))}
                  className="w-16 rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            )}
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={loading || !title.trim()}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Adding..." : "Add Task"}
      </button>
    </form>
  );
}
