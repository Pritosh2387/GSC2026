import { type LucideIcon } from "lucide-react";

interface StatsCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  gradient?: string;
  delay?: number;
}

export default function StatsCard({
  label,
  value,
  icon: Icon,
  gradient,
  delay = 0,
}: StatsCardProps) {
  return (
    <div
      className={`stat-card animate-fade-in ${delay > 0 ? `animate-delay-${delay}` : ""}`}
      style={gradient ? { "--sg-gradient-1": gradient } as React.CSSProperties : {}}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div className="stat-value">{value}</div>
          <div className="stat-label">{label}</div>
        </div>
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: "rgba(108, 92, 231, 0.1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Icon size={22} style={{ color: "var(--sg-accent-light)" }} />
        </div>
      </div>
    </div>
  );
}
