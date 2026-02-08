"use client";

import { ChatPanel } from "@/components/chat/chat-panel";

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Chat</h2>
        <p className="text-sm text-gray-500">
          Manage your tasks using natural language
        </p>
      </div>
      <div className="flex-1 overflow-hidden rounded-lg border border-gray-200 bg-white">
        <ChatPanel />
      </div>
    </div>
  );
}
