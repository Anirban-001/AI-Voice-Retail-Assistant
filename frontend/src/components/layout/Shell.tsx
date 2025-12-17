import { ReactNode } from "react";
import { cn } from "../../lib/utils";

interface ShellProps {
  children: ReactNode;
  className?: string;
}

export function Shell({ children, className }: ShellProps) {
  return (
    <div
      className={cn(
        "min-h-screen bg-[#04060f] text-white px-6 py-6 md:px-10 xl:px-16",
        "relative overflow-hidden",
        className
      )}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute w-[60vw] h-[60vw] -top-40 -left-10 bg-[#1B5F8C]/30 blur-[120px]" />
        <div className="absolute w-[40vw] h-[40vw] bottom-0 right-0 bg-[#F38630]/20 blur-[160px]" />
        <div className="absolute inset-0 backdrop-blur-[2px] bg-gradient-to-b from-[#04060f]/60 to-[#04060f]" />
      </div>
      <div className="relative z-10 max-w-[1440px] mx-auto flex flex-col gap-8">{children}</div>
    </div>
  );
}
