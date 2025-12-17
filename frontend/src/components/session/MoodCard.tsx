import { Panel } from "../layout/Panels";

interface MoodCardProps {
  mood?: string;
  confidence?: number;
  tone?: string;
}

export function MoodCard({ mood = "neutral", confidence = 0, tone = "professional" }: MoodCardProps) {
  return (
    <Panel className="flex flex-col gap-4">
      <div>
        <p className="text-xs uppercase tracking-[0.4em] text-white/40">Mood Signal</p>
        <p className="text-3xl font-semibold mt-2">
          {mood}
          <span className="text-base text-white/60"> {(confidence * 100).toFixed(0)}%</span>
        </p>
      </div>
      <div className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white/70">
        Suggested tone: <span className="font-semibold text-white">{tone}</span>
      </div>
    </Panel>
  );
}
