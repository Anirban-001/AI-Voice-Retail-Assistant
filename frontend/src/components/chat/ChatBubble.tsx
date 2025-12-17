import { Mic } from "lucide-react";
import { cn } from "../../lib/utils";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  isVoice?: boolean;
}

export function ChatBubble({ role, content, isVoice }: ChatBubbleProps) {
  const isUser = role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isUser
            ? "bg-gradient-to-r from-[#F38630] to-[#F7B733] text-[#1A1C1D]"
            : "bg-white/8 border border-white/10"
        )}
      >
        {isVoice && (
          <div className="flex items-center gap-1.5 mb-1.5 text-xs opacity-70">
            <Mic size={12} />
            <span>Voice message</span>
          </div>
        )}
        {content}
      </div>
    </div>
  );
}
