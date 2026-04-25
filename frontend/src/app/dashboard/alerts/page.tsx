"use client";

import { useEffect, useState } from "react";
import { getAlerts, resolveAlert, type Alert } from "@/lib/api";
import { CheckCircle, Filter, Search } from "lucide-react";

const SEVERITIES = ["all", "critical", "high", "medium", "low"];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, [filter]);

  async function fetchAlerts() {
    setLoading(true);
    try {
      const params: Record<string, string | boolean | number> = { limit: 100 };
      if (filter !== "all") params.severity = filter;
      const data = await getAlerts(params as Parameters<typeof getAlerts>[0]);
      setAlerts(data);
    } catch {
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleResolve(id: string) {
    try {
      await resolveAlert(id);
      setAlerts((prev) =>
        prev.map((a) => (a._id === id ? { ...a, resolved: true } : a))
      );
    } catch { /* ignore */ }
  }

  function severityBadge(sev?: string) {
    const s = sev?.toLowerCase() || "medium";
    return <span className={`badge badge-${s}`}>{s}</span>;
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Piracy Alerts</h1>
        <p>Monitor and manage detected piracy incidents across platforms.</p>
      </div>

      {/* Filters */}
      <div
        style={{
          display: "flex",
          gap: 16,
          marginBottom: 40,
          alignItems: "center",
          flexWrap: "wrap"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 16px", background: "#fff", border: "1px solid var(--sg-border)", borderRadius: 12, color: "var(--sg-text-muted)", fontSize: 13, fontWeight: 600 }}>
          <Filter size={16} />
          <span>Filter Sensitivity:</span>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {SEVERITIES.map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={filter === s ? "btn-primary" : "btn-secondary"}
              style={{ 
                height: 42,
                padding: "0 20px", 
                fontSize: 13, 
                textTransform: "capitalize",
                border: filter === s ? "none" : "1px solid var(--sg-border)"
              }}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="sg-table-container">
        {loading ? (
          <div style={{ padding: 100, textAlign: "center", color: "var(--sg-text-muted)" }}>
            <div className="skeleton" style={{ width: 120, height: 24, margin: "0 auto 16px" }} />
            <p>Accessing neural archives…</p>
          </div>
        ) : alerts.length === 0 ? (
          <div style={{ padding: 120, textAlign: "center", color: "var(--sg-text-muted)" }}>
            <Search size={64} style={{ marginBottom: 24, opacity: 0.1 }} />
            <p style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--sg-text-primary)", marginBottom: 8, letterSpacing: "-0.02em" }}>Forensic Clearance</p>
            <p style={{ maxWidth: 320, margin: "0 auto" }}>The matching engine has not detected any active policy violations in this sector.</p>
          </div>
        ) : (
          <table className="sg-table">
            <thead>
              <tr>
                <th>Target Asset</th>
                <th>Forensic Source</th>
                <th>Confidence</th>
                <th>Severity</th>
                <th>Operational Status</th>
                <th>Detection Time</th>
                <th>Command</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a._id}>
                  <td style={{ color: "var(--sg-text-primary)", fontWeight: 700 }}>
                    {a.matched_content || "Unknown Media"}
                  </td>
                  <td style={{ fontSize: 13 }}>{a.channel_name || "—"}</td>
                  <td style={{ fontWeight: 700 }}>
                    {a.similarity_score
                      ? `${(a.similarity_score * 100).toFixed(1)}%`
                      : "—"}
                  </td>
                  <td>{severityBadge(a.severity)}</td>
                  <td>
                    {a.resolved ? (
                      <span style={{ color: "var(--sg-success)", fontSize: 13, fontWeight: 700, display: "flex", alignItems: "center", gap: 6 }}>
                         <CheckCircle size={16} /> Resolved
                      </span>
                    ) : (
                      <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--sg-danger)", fontSize: 13, fontWeight: 700 }}>
                         <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--sg-danger)", boxShadow: "0 0 10px var(--sg-danger)" }} />
                         Violation Active
                      </div>
                    )}
                  </td>
                  <td style={{ fontSize: 13, color: "var(--sg-text-muted)" }}>
                    {a.created_at ? new Date(a.created_at).toLocaleString() : "—"}
                  </td>
                  <td>
                    {!a.resolved ? (
                      <button
                        onClick={() => handleResolve(a._id)}
                        className="btn-secondary"
                        style={{ 
                          padding: "8px 16px", 
                          fontSize: 12, 
                          height: 34
                        }}
                      >
                        Resolve
                      </button>
                    ) : (
                      <span style={{ fontSize: 12, color: "var(--sg-text-muted)", fontWeight: 700 }}>VERIFIED</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
