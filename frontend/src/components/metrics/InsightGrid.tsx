import { Panel, PanelHeader } from "../layout/Panels";
import { StatPill } from "./StatPill";

interface InsightGridProps {
  stats: Record<string, number>;
}

export function InsightGrid({ stats }: InsightGridProps) {
  const entries = Object.entries(stats);

  return (
    <Panel>
      <PanelHeader title="System Pulse" />
      {entries.length === 0 ? (
        <p className="text-sm text-white/60">Stats will appear once the backend is live.</p>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {entries.map(([key, value]) => (
            <StatPill key={key} label={key.replace(/_/g, " ")} value={value.toString()} />
          ))}
        </div>
      )}
    </Panel>
  );
}
