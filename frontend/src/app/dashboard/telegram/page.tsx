"use client";

import { useEffect, useState } from "react";
import { Send, Play, Square, Info, ShieldCheck } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function TelegramMonitorPage() {
  const [status, setStatus] = useState<{ 
    running: boolean; 
    api_id: string; 
    session_exists: boolean;
    stats?: {
      total_matches: number;
      unique_channels: number;
      media_captured: number;
      forensic_storage_mb: number;
      average_confidence: number;
      last_match_time: string;
    }
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  async function fetchStatus() {
    try {
      const data = await apiFetch("/api/telegram/status");
      setStatus(data as { running: boolean; api_id: string; session_exists: boolean });
    } catch (err) {
      console.error("Failed to fetch status", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  async function handleToggle() {
    setActionLoading(true);
    try {
      const endpoint = status?.running ? "/api/telegram/stop-monitor" : "/api/telegram/start-monitor";
      await apiFetch(endpoint, { method: "POST" });
      await fetchStatus();
    } catch (err) {
      alert("Action failed. Check console.");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) return <div>Loading monitor status...</div>;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Telegram Monitor</h1>
        <p>Manage real-time scanning across Telegram channels to protect your content.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 40, alignItems: "stretch" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 40 }}>
          {/* Status Card */}
          <div className="glass-card" style={{ padding: 60, textAlign: "center", position: "relative", overflow: "hidden" }}>
             {/* Background glow effect for active state */}
             {status?.running && (
               <div style={{ position: "absolute", top: "-50%", left: "-50%", width: "200%", height: "200%", background: "radial-gradient(circle, rgba(16, 185, 129, 0.03) 0%, transparent 60%)", pointerEvents: "none" }} />
             )}

            <div 
              style={{ 
                width: 100, height: 100, borderRadius: "50%", 
                background: status?.running ? "var(--sg-bg-secondary)" : "var(--sg-bg-secondary)",
                border: `6px solid ${status?.running ? "var(--sg-success)" : "var(--sg-border)"}`,
                color: status?.running ? "var(--sg-success)" : "var(--sg-text-muted)",
                display: "flex", alignItems: "center", justifyContent: "center",
                margin: "0 auto 32px",
                boxShadow: status?.running ? "0 0 30px rgba(16, 185, 129, 0.1)" : "none",
                transition: "all 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
              }}
            >
              <Send size={48} className={status?.running ? "animate-pulse" : ""} />
            </div>
            
            <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: 12, color: "var(--lp-text-main)", letterSpacing: "-0.03em" }}>
              Scanner {status?.running ? "Running" : "Paused"}
            </h2>
            <p style={{ color: "var(--lp-text-sec)", marginBottom: 48, fontSize: "1.125rem", maxWidth: 460, margin: "0 auto 48px", lineHeight: 1.6 }}>
              {status?.running 
                ? "The system is currently scanning channels for matches with your registered media." 
                : "The scanner is currently paused. No channels are being monitored."}
            </p>

            <button 
              className={status?.running ? "btn-secondary" : "btn-primary"}
              onClick={handleToggle}
              disabled={actionLoading}
              style={{ minWidth: 260, height: 60, fontSize: "1.0625rem" }}
            >
              {actionLoading ? "Processing..." : (
                status?.running ? (
                  <><Square size={20} /> Stop Scanner</>
                ) : (
                  <><Play size={20} /> Start Scanner</>
                )
              )}
            </button>
          </div>

          {/* Stats Cards Row 1 */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24 }}>
            <div className="glass-card" style={{ padding: 24, textAlign: "center" }}>
               <div style={{ fontSize: 11, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Monitored Channels</div>
               <div style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--lp-text-main)" }}>{status?.stats?.unique_channels ?? 0}</div>
            </div>
            <div className="glass-card" style={{ padding: 24, textAlign: "center" }}>
               <div style={{ fontSize: 11, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Media Captured</div>
               <div style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--lp-text-main)" }}>{status?.stats?.media_captured ?? 0}</div>
            </div>
            <div className="glass-card" style={{ padding: 24, textAlign: "center" }}>
               <div style={{ fontSize: 11, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Total Matches</div>
               <div style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--lp-accent)" }}>{status?.stats?.total_matches ?? 0}</div>
            </div>
          </div>

          {/* Stats Cards Row 2 */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24 }}>
            <div className="glass-card" style={{ padding: 24, textAlign: "center" }}>
               <div style={{ fontSize: 11, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Forensic Storage</div>
               <div style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--lp-text-main)" }}>{status?.stats?.forensic_storage_mb ?? 0} <span style={{ fontSize: 14 }}>MB</span></div>
            </div>
            <div className="glass-card" style={{ padding: 24, textAlign: "center" }}>
               <div style={{ fontSize: 11, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Avg. Confidence</div>
               <div style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--lp-text-main)" }}>{status?.stats?.average_confidence ?? 0}%</div>
            </div>
            <div className="glass-card" style={{ padding: 24, textAlign: "center" }}>
               <div style={{ fontSize: 11, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Last Detection</div>
               <div style={{ fontSize: "1rem", fontWeight: 800, color: "var(--lp-text-main)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                 {status?.stats?.last_match_time && status.stats.last_match_time !== "Never" 
                   ? new Date(status.stats.last_match_time).toLocaleTimeString() 
                   : "Never"}
               </div>
            </div>
          </div>

          {/* Service Details Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
            <div className="glass-card" style={{ padding: 32 }}>
              <div style={{ color: "var(--lp-accent)", marginBottom: 20 }}><ShieldCheck size={28} /></div>
              <h3 style={{ fontSize: "1.125rem", fontWeight: 700, marginBottom: 12, color: "var(--lp-text-main)" }}>Connection Status</h3>
              <p style={{ fontSize: 14, color: "var(--lp-text-sec)", lineHeight: 1.6 }}>
                {status?.session_exists 
                  ? "Secure connection to Telegram is active." 
                  : "Connection required. Please authorize via terminal."}
              </p>
            </div>
            <div className="glass-card" style={{ padding: 32 }}>
              <div style={{ color: "var(--lp-accent)", marginBottom: 20 }}><Info size={28} /></div>
              <h3 style={{ fontSize: "1.125rem", fontWeight: 700, marginBottom: 12, color: "var(--lp-text-main)" }}>System Info</h3>
              <p style={{ fontSize: 14, color: "var(--lp-text-sec)", lineHeight: 1.6 }}>
                API ID: <code style={{ color: "var(--lp-accent)", fontWeight: 700 }}>{status?.api_id}</code>. 
                Optimized for fast detection and content matching.
              </p>
            </div>
          </div>
        </div>

        {/* Operational Sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
          <div className="glass-card" style={{ padding: 32 }}>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 24, color: "var(--lp-text-main)" }}>Instructions</h3>
            <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 24, fontSize: 14 }}>
              <li style={{ display: "flex", gap: 12, lineHeight: 1.6 }}>
                <span style={{ color: "var(--lp-accent)", fontWeight: 800 }}>01</span>
                <div>
                  <span style={{ display: "block", color: "var(--lp-text-main)", fontWeight: 700, marginBottom: 4 }}>Channel Access</span>
                  <span style={{ color: "var(--lp-text-sec)" }}>Ensure you are a member of the channels you wish to monitor.</span>
                </div>
              </li>
              <li style={{ display: "flex", gap: 12, lineHeight: 1.6 }}>
                <span style={{ color: "var(--lp-accent)", fontWeight: 800 }}>02</span>
                <div>
                  <span style={{ display: "block", color: "var(--lp-text-main)", fontWeight: 700, marginBottom: 4 }}>Content Matching</span>
                  <span style={{ color: "var(--lp-text-sec)" }}>Matches are only triggered for media you have uploaded to the system.</span>
                </div>
              </li>
              <li style={{ display: "flex", gap: 12, lineHeight: 1.6 }}>
                <span style={{ color: "var(--lp-accent)", fontWeight: 800 }}>03</span>
                <div>
                  <span style={{ display: "block", color: "var(--lp-text-main)", fontWeight: 700, marginBottom: 4 }}>Alert Flow</span>
                  <span style={{ color: "var(--lp-text-sec)" }}>Detected matches appear in your alerts dashboard for review.</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
