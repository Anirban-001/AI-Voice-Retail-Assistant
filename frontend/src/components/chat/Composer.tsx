import { FormEvent, useState } from "react";
import { SendHorizontal, Mic, Square } from "lucide-react";
import { cn } from "../../lib/utils";

interface ComposerProps {
  disabled?: boolean;
  onSend: (value: string) => Promise<void> | void;
  isVoiceActive?: boolean;
  onVoiceToggle?: () => void;
  voiceStatus?: string;
  liveTranscript?: string;
  onTranscriptChange?: (value: string) => void;
  isVoiceStopped?: boolean;
  onVoiceStop?: () => void;
}

export function Composer({ disabled, onSend, isVoiceActive, onVoiceToggle, voiceStatus, liveTranscript, onTranscriptChange, isVoiceStopped, onVoiceStop }: ComposerProps) {
  const [value, setValue] = useState("");
  const [isSending, setIsSending] = useState(false);

  const currentValue = liveTranscript || value;

  const handleChange = (newValue: string) => {
    setValue(newValue);
    onTranscriptChange?.(newValue);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim() || isSending) return;

    setIsSending(true);
    try {
      await onSend(value.trim());
      setValue("");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="space-y-2">
      {isVoiceActive && voiceStatus && (
        <div className="rounded-xl border border-[#2368af]/50 bg-gradient-to-r from-[#2368af]/10 to-[#1B5F8C]/5 px-4 py-2 flex items-center gap-2">
          <div className="flex items-center gap-2 flex-1">
            <div className="h-2 w-2 rounded-full bg-[#2368af] animate-pulse" />
            <span className="text-xs text-white/90">{voiceStatus}</span>
          </div>
          {isVoiceStopped && liveTranscript ? (
            <button
              type="button"
              onClick={onVoiceStop}
              className="text-xs px-3 py-1 rounded-lg bg-[#2368af] hover:bg-[#1B5F8C] text-white transition-colors font-medium"
            >
              ✓ STOP
            </button>
          ) : (
            <button
              type="button"
              onClick={onVoiceToggle}
              className="text-xs text-white/70 hover:text-white transition-colors"
            >
              Click to stop
            </button>
          )}
        </div>
      )}
      
      <form
        onSubmit={handleSubmit}
        className={cn(
          "flex items-center gap-3 rounded-2xl border bg-black/30 px-3 py-2 transition-all",
          isVoiceActive 
            ? "border-[#2368af]/50 shadow-lg shadow-[#2368af]/20" 
            : "border-white/10",
          disabled && "opacity-60"
        )}
      >
        {onVoiceToggle && (
          <button
            type="button"
            onClick={onVoiceToggle}
            disabled={disabled}
            className={cn(
              "flex h-9 w-9 items-center justify-center rounded-full transition-all",
              isVoiceActive
                ? "bg-red-500 hover:bg-red-600 text-white animate-pulse"
                : "bg-[#2368af] hover:bg-[#1B5F8C] text-white"
            )}
            title={isVoiceActive ? "Stop voice" : "Start voice"}
          >
            {isVoiceActive ? <Square size={16} className="fill-current" /> : <Mic size={16} />}
          </button>
        )}
        
        <textarea
          rows={2}
          value={currentValue}
          onChange={(event) => handleChange(event.target.value)}
          placeholder={isVoiceActive ? "🎤 Speaking..." : "Type or speak your message..."}
          className="flex-1 resize-none bg-transparent text-sm text-white placeholder:text-white/40 focus:outline-none"
          disabled={disabled || isSending || isVoiceActive}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e as any);
            }
          }}
        />
        <button
          type="submit"
          disabled={!value.trim() || disabled || isSending}
          className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#F38630] to-[#F7B733] text-[#1A1C1D] disabled:opacity-30 transition-all hover:shadow-lg"
        >
          <SendHorizontal size={18} />
        </button>
      </form>
    </div>
  );
}
