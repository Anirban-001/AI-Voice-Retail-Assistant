import { ChatBubble } from "./ChatBubble";
import type { ChatMessage } from "../../lib/types";

interface ChatTimelineProps {
  messages: ChatMessage[];
}

export function ChatTimeline({ messages }: ChatTimelineProps) {
  if (!messages.length) {
    return (
      <div className="text-center text-white/60 py-10 text-sm">
        Start the conversation to brief the retail assistant.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {messages.map((message) => (
        <ChatBubble 
          key={message.id} 
          role={message.role} 
          content={message.content}
          isVoice={message.isVoice}
        />
      ))}
    </div>
  );
}
