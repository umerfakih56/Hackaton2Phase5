"use client";

import type { Task } from "@/lib/types";
import { TaskCard } from "./task-card";

interface TaskListProps {
  tasks: Task[];
  onComplete?: (taskId: number) => void;
  onReopen?: (taskId: number) => void;
  onDelete?: (taskId: number) => void;
}

export function TaskList({ tasks, onComplete, onReopen, onDelete }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="py-12 text-center text-gray-400">
        No tasks found. Create one to get started.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onComplete={onComplete}
          onReopen={onReopen}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
