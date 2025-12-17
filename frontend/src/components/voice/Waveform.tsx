import { useMemo, useEffect, useState } from "react";

interface WaveformProps {
  active?: boolean;
  bars?: number;
  height?: number;
}

export function Waveform({ active, bars = 32, height = 52 }: WaveformProps) {
  const barIndexes = useMemo(() => Array.from({ length: bars }, (_, index) => index), [bars]);
  const [heights, setHeights] = useState<number[]>([]);

  useEffect(() => {
    const generateHeights = () => {
      return barIndexes.map((_, i) => {
        const center = bars / 2;
        const distance = Math.abs(i - center) / center;
        const baseHeight = 6 + Math.random() * (height - 12);
        // Create wave pattern from center
        return baseHeight * (1 - distance * 0.3);
      });
    };

    setHeights(generateHeights());

    if (active) {
      const interval = setInterval(() => {
        setHeights(generateHeights());
      }, 200);

      return () => clearInterval(interval);
    }
  }, [active, barIndexes, height, bars]);

  return (
    <div className="flex items-end gap-1" style={{ height }}>
      {barIndexes.map((bar, index) => (
        <div
          key={bar}
          className="w-1 rounded-full transition-all duration-200"
          style={{
            height: `${active ? (heights[index] || 8) : 8}px`,
            opacity: active ? 0.6 + ((index % 8) * 0.05) : 0.3,
            background: active 
              ? 'linear-gradient(to bottom, #2368af, #1B5F8C)'
              : 'linear-gradient(to bottom, #666, #444)',
            animation: active
              ? `voiceBounce ${0.6 + (index % 7) * 0.12}s ease-in-out infinite`
              : "none"
          }}
        />
      ))}
    </div>
  );
}
