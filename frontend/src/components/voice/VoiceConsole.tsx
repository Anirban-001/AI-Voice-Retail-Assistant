import { Mic, Square, Volume2, AlertCircle } from "lucide-react";
import { Panel, PanelHeader } from "../layout/Panels";
import { Waveform } from "./Waveform";
import { cn } from "../../lib/utils";

interface VoiceConsoleProps {
  isStreaming: boolean;
  transcript: string;
  onToggle: () => void;
  error?: string | null;
}

export function VoiceConsole({ isStreaming, transcript, onToggle, error }: VoiceConsoleProps) {
  return (
    <Panel className="flex flex-col gap-4">
      <PanelHeader
        title="Voice Director"
        subtitle="Real-time voice interaction with AI agents"
        action={
          <button
            type="button"
            onClick={onToggle}
            className={cn(
              "flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all duration-300 shadow-lg",
              isStreaming
                ? "bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 animate-pulse"
                : "bg-gradient-to-r from-[#1B5F8C] to-[#2368af] text-white hover:from-[#2368af] hover:to-[#1B5F8C] hover:shadow-xl"
            )}
          >
            {isStreaming ? (
              <>
                <Square size={16} className="fill-current" /> 
                <span>Stop</span>
              </>
            ) : (
              <>
                <Mic size={16} /> 
                <span>Go Live</span>
              </>
            )}
          </button>
        }
      />
      
      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 flex items-start gap-2 text-sm text-red-200">
          <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      <div className={cn(
        "min-h-[140px] rounded-2xl border transition-all duration-300 p-5",
        isStreaming 
          ? "border-[#2368af]/50 bg-gradient-to-br from-[#2368af]/10 to-[#1B5F8C]/5 shadow-lg shadow-[#2368af]/20" 
          : "border-white/10 bg-black/30"
      )}>
        <div className="flex items-start gap-3">
          {isStreaming && (
            <Volume2 size={20} className="text-[#2368af] mt-1 flex-shrink-0 animate-pulse" />
          )}
          <p className={cn(
            "text-sm leading-relaxed",
            isStreaming ? "text-white" : "text-white/70"
          )}>
            {transcript || "Press 'Go Live' to activate voice interaction. Speak naturally and the AI agents will respond."}
          </p>
        </div>
      </div>
      
      <div className="flex justify-center py-2">
        <Waveform active={isStreaming} />
      </div>
      
      {isStreaming && (
        <div className="text-center">
          <p className="text-xs text-white/50 uppercase tracking-wider">
            🎤 Voice Session Active
          </p>
        </div>
      )}
    </Panel>
  );
}
