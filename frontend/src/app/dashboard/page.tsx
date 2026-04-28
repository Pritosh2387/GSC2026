"use client";

import { useEffect, useState } from "react";
import { getDashboardStats, getAlerts, type DashboardStats, type Alert } from "@/lib/api";
import StatsCard from "@/components/StatsCard";
import { Bell, Search, Shield, FileUp, AlertCircle, Clock, RefreshCcw, Zap, Layout, Plus, Send, Video } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const s = await getDashboardStats();
        setStats(s);
        const a = await getAlerts({ limit: 8 });
        setAlerts(a);
      } catch (err) {
        console.error("Dashboard data fetch failed", err);
      }
    }
    fetchData();
    const interval = setInterval(fetchData, 10000); // Polling every 10s
    return () => clearInterval(interval);
  }, []);

  function severityBadge(sev?: string) {
    const s = sev?.toLowerCase() || "medium";
    return <span className={`badge badge-${s}`}>{s}</span>;
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Dashboard Overview</h1>
        <p>Monitor your content protection status and system health.</p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 32,
          marginBottom: 60,
        }}
      >
        <StatsCard label="Alerts" value={stats?.overview.total_alerts ?? "—"} icon={Bell} delay={1} />
        <StatsCard
          label="Matches"
          value={stats?.overview.total_detections ?? "—"}
          icon={Shield}
          delay={2}
        />
        <StatsCard
          label="Monitoring"
          value={stats?.overview.registered_media ?? "—"}
          icon={FileUp}
          delay={3}
        />
        <StatsCard
          label="Status"
          value={stats?.telegram_running ? "Active" : "Paused"}
          icon={Send}
          delay={4}
        />
      </div>

      {/* Analytics Summary */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 32,
          marginBottom: 60,
        }}
      >
        {/* Severity Breakdown */}
        <div className="glass-card" style={{ padding: 32 }}>
          <h3 style={{ fontSize: "1.125rem", fontWeight: 700, marginBottom: 24 }}>Severity Distribution</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {["critical", "high", "medium", "low"].map((sev) => {
              const count = stats?.severity?.[sev] ?? 0;
              const total = stats?.overview?.total_alerts || 1;
              const percent = Math.round((count / total) * 100);
              return (
                <div key={sev}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, fontWeight: 700, textTransform: "uppercase", marginBottom: 8 }}>
                    <span style={{ color: `var(--sg-${sev === "critical" ? "danger" : sev})` }}>{sev}</span>
                    <span style={{ color: "var(--lp-text-sec)" }}>{count} ({percent}%)</span>
                  </div>
                  <div style={{ height: 6, background: "var(--lp-alt)", borderRadius: 3, overflow: "hidden" }}>
                    <div 
                      style={{ 
                        height: "100%", 
                        width: `${percent}%`, 
                        background: `var(--sg-${sev === "critical" ? "danger" : sev})`,
                        transition: "width 1s ease-out"
                      }} 
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Channels */}
        <div className="glass-card" style={{ padding: 32 }}>
          <h3 style={{ fontSize: "1.125rem", fontWeight: 700, marginBottom: 24 }}>Top Infringing Channels</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {stats?.top_channels && stats.top_channels.length > 0 ? (
              stats.top_channels.map((chan, idx) => (
                <div key={idx} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", background: "var(--lp-alt)", borderRadius: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 24, height: 24, borderRadius: "50%", background: "var(--lp-accent-glow)", color: "var(--lp-accent)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 800 }}>
                      {idx + 1}
                    </div>
                    <span style={{ fontSize: 14, fontWeight: 600, color: "var(--lp-text-main)" }}>{chan.channel}</span>
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: "var(--lp-accent)" }}>{chan.violations} violations</span>
                </div>
              ))
            ) : (
              <div style={{ textAlign: "center", padding: 40, color: "var(--lp-text-sec)" }}>
                No channel data available yet.
              </div>
            )}
          </div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 380px",
          gap: 40,
        }}
      >
        {/* Alerts Feed */}
        <div>
          <div
            style={{
              padding: "0 0 24px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--lp-text-main)" }}>Recent Alerts</h3>
            <Link href="/dashboard/alerts" className="btn-secondary" style={{ fontSize: 13, padding: "8px 16px" }}>
              View all
            </Link>
          </div>

          <div className="sg-table-container">
            {alerts.length === 0 ? (
              <div style={{ padding: 80, textAlign: "center", color: "var(--sg-text-muted)" }}>
                <Search size={48} style={{ marginBottom: 20, opacity: 0.1 }} />
                <p style={{ fontSize: "1rem" }}>Neural network is scanning. No threats detected.</p>
              </div>
            ) : (
              <table className="sg-table">
                <thead>
                  <tr>
                    <th>Content Name</th>
                    <th>Source</th>
                    <th>Match Score</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((a) => (
                    <tr key={a._id}>
                      <td style={{ fontWeight: 700, color: "var(--sg-text-primary)" }}>
                        {a.matched_content || "Unknown Media"}
                      </td>
                      <td>{a.channel_name || "Encrypted Source"}</td>
                      <td style={{ fontWeight: 600 }}>
                        {a.similarity_score
                          ? `${(a.similarity_score * 100).toFixed(1)}%`
                          : "—"}
                      </td>
                      <td>{severityBadge(a.severity)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Sidebar Actions */}
        <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
          <div className="glass-card" style={{ padding: 32 }}>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 700, marginBottom: 24 }}>Quick Actions</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <Link href="/dashboard/register-content" className="lp-btn-secondary" style={{ justifyContent: "center" }}>
                <Plus size={18} /> Add Media
              </Link>
              <button className="lp-btn-secondary" style={{ justifyContent: "center" }} onClick={() => window.location.reload()}>
                <RefreshCcw size={18} /> Sync Assets
              </button>
            </div>
          </div>

          <div className="glass-card" style={{ padding: 32, flex: 1 }}>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 700, marginBottom: 24 }}>System Health</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {[
                { n: "Recognition Engine", s: "ONLINE" },
                { n: "Telegram Integration", s: stats?.telegram_running ? "ONLINE" : "OFFLINE" },
                { n: "Deepfake Detection", s: "ONLINE" },
                { n: "Database Service", s: "ONLINE" }
              ].map(item => (
                <div key={item.n} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "0.875rem", color: "var(--lp-text-sec)" }}>{item.n}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.75rem", fontWeight: 800, color: item.s === "ONLINE" ? "var(--lp-success)" : "var(--lp-text-muted)" }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: item.s === "ONLINE" ? "var(--lp-success)" : "var(--lp-text-muted)" }} />
                    {item.s}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
