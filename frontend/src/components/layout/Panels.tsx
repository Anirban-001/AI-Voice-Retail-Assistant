import { ReactNode } from "react";
import { cn } from "../../lib/utils";

interface PanelProps {
  children: ReactNode;
  className?: string;
}

export function Panel({ children, className }: PanelProps) {
  return (
    <div
      className={cn(
        "bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl p-5 md:p-6",
        "shadow-[0_20px_60px_-30px_rgba(0,0,0,0.9)]",
        className
      )}
    >
      {children}
    </div>
  );
}

export function PanelHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-white/60">{title}</p>
        {subtitle && <p className="text-xs text-white/40 mt-1">{subtitle}</p>}
      </div>
      {action ? <div className="text-white/80 text-sm">{action}</div> : null}
    </div>
  );
}
