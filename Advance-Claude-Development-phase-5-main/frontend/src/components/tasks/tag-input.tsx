"use client";

import { useCallback, useEffect, useState } from "react";
import { listTags } from "@/lib/api-client";
import type { Tag } from "@/lib/types";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
}

export function TagInput({ value, onChange }: TagInputProps) {
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState<Tag[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const fetchSuggestions = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }
    try {
      const result = await listTags(query);
      setSuggestions(result.tags.filter((t) => !value.includes(t.name)));
    } catch {
      setSuggestions([]);
    }
  }, [value]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (input.trim()) fetchSuggestions(input);
    }, 200);
    return () => clearTimeout(timer);
  }, [input, fetchSuggestions]);

  function addTag(tagName: string) {
    const clean = tagName.trim().toLowerCase();
    if (clean && !value.includes(clean)) {
      onChange([...value, clean]);
    }
    setInput("");
    setSuggestions([]);
    setShowSuggestions(false);
  }

  function removeTag(tagName: string) {
    onChange(value.filter((t) => t !== tagName));
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if ((e.key === "Enter" || e.key === ",") && input.trim()) {
      e.preventDefault();
      addTag(input);
    }
    if (e.key === "Backspace" && !input && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  }

  return (
    <div className="relative">
      <div className="flex flex-wrap items-center gap-1 rounded-md border border-gray-300 px-2 py-1.5">
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-0.5 rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="text-blue-500 hover:text-blue-700"
            >
              &times;
            </button>
          </span>
        ))}
        <input
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setShowSuggestions(true);
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
          placeholder={value.length === 0 ? "Add tags..." : ""}
          className="flex-1 border-none text-sm outline-none min-w-[80px]"
        />
      </div>

      {showSuggestions && suggestions.length > 0 && (
        <ul className="absolute z-10 mt-1 w-full rounded-md border border-gray-200 bg-white shadow-lg">
          {suggestions.map((tag) => (
            <li key={tag.id}>
              <button
                type="button"
                className="flex w-full items-center justify-between px-3 py-1.5 text-sm hover:bg-gray-50"
                onMouseDown={() => addTag(tag.name)}
              >
                <span>{tag.name}</span>
                <span className="text-xs text-gray-400">
                  {tag.task_count} tasks
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
