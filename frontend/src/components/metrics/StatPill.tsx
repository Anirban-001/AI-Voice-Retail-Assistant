interface StatPillProps {
  label: string;
  value: string;
  accent?: string;
}

export function StatPill({ label, value, accent = "#F38630" }: StatPillProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.3em] text-white/50">{label}</p>
      <p className="text-2xl font-semibold" style={{ color: accent }}>
        {value}
      </p>
    </div>
  );
}
