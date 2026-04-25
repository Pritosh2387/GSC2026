"use client";

import { FormEvent, useState, useEffect } from "react";
import {
  analyzeAres,
  getAresHistory,
  type AresInput,
  type AresResult,
} from "@/lib/api";
import { Shield, Zap, History, Layout, Info } from "lucide-react";

const DEFAULT_INPUT: AresInput = {
  match_id: "M_001",
  content_id: "PREMIER_LEAGUE_2024",
  match_confidence: 0.92,
  transformation_index: 0.85,
  view_velocity: 3000,
  platform: "youtube",
  uploader_id: "pirate_channel_99",
  uploader_reputation: 0.2,
  jurisdiction: "US",
  is_commercial: true,
};

const PLATFORMS = ["youtube", "meta", "tiktok", "x"];

export default function AresPage() {
  const [input, setInput] = useState<AresInput>(DEFAULT_INPUT);
  const [result, setResult] = useState<AresResult | null>(null);
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getAresHistory()
      .then((h) => setHistory(h as Record<string, unknown>[]))
      .catch(() => {});
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const r = await analyzeAres(input);
      setResult(r);
      const h = await getAresHistory();
      setHistory(h as Record<string, unknown>[]);
    } catch { /* ignore */ }
    setLoading(false);
  }

  function update<K extends keyof AresInput>(key: K, val: AresInput[K]) {
    setInput((prev) => ({ ...prev, [key]: val }));
  }

  function categoryBadge(cat: string) {
    return <span className={`badge badge-${cat.toLowerCase()}`} style={{ fontWeight: 800 }}>{cat.toUpperCase()}</span>;
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>ARES Enforcement Engine</h1>
        <p>Automated Revenue Enforcement & Shield — AI-powered decision simulation.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40, alignItems: "stretch" }}>
        {/* Input form */}
        <div className="glass-card" style={{ padding: 40 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 32 }}>
            <div style={{ color: "var(--sg-accent)" }}><Layout size={24} /></div>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--sg-text-primary)" }}>Simulation Parameters</h3>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
              {/* Group 1: Asset Details */}
              <section>
                <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--sg-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 16 }}>Asset Context</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                  <div className="form-group">
                    <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 600, color: "var(--sg-text-secondary)", marginBottom: 8 }}>Match ID</label>
                    <input
                      className="input-field"
                      value={input.match_id}
                      onChange={(e) => update("match_id", e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 600, color: "var(--sg-text-secondary)", marginBottom: 8 }}>Content Asset</label>
                    <input
                      className="input-field"
                      value={input.content_id}
                      onChange={(e) => update("content_id", e.target.value)}
                    />
                  </div>
                </div>
              </section>

              {/* Group 2: Detection Analytics */}
              <section>
                <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--sg-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 16 }}>Detection Analytics</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                  <div className="form-group">
                    <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 600, color: "var(--sg-text-secondary)", marginBottom: 8 }}>Confidence (0-1)</label>
                    <input
                      className="input-field"
                      type="number" step={0.01}
                      value={input.match_confidence}
                      onChange={(e) => update("match_confidence", +e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 600, color: "var(--sg-text-secondary)", marginBottom: 8 }}>View Velocity</label>
                    <input
                      className="input-field"
                      type="number"
                      value={input.view_velocity}
                      onChange={(e) => update("view_velocity", +e.target.value)}
                    />
                  </div>
                </div>
              </section>

              {/* Group 3: Distribution & Legal */}
              <section>
                <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--sg-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 16 }}>Distribution & Metadata</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                  <div className="form-group">
                    <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 600, color: "var(--sg-text-secondary)", marginBottom: 8 }}>Platform</label>
                    <select
                      className="input-field"
                      style={{ background: "#fff" }}
                      value={input.platform}
                      onChange={(e) => update("platform", e.target.value)}
                    >
                      {PLATFORMS.map((p) => (
                        <option key={p} value={p}>{p.toUpperCase()}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 600, color: "var(--sg-text-secondary)", marginBottom: 8 }}>Jurisdiction</label>
                    <input
                      className="input-field"
                      value={input.jurisdiction}
                      onChange={(e) => update("jurisdiction", e.target.value)}
                    />
                  </div>
                </div>
              </section>
            </div>

            <div style={{ marginTop: 32, padding: 24, borderRadius: 16, background: "var(--sg-bg-secondary)", border: "1px solid var(--sg-border)" }}>
              <label style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer", fontSize: 14, fontWeight: 600, color: "var(--sg-text-primary)" }}>
                <input
                  type="checkbox"
                  checked={input.is_commercial}
                  onChange={(e) => update("is_commercial", e.target.checked)}
                  style={{ width: 20, height: 20, accentColor: "var(--sg-accent)" }}
                />
                Commercial Intent Detected
              </label>
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
              style={{ width: "100%", marginTop: 40, height: 54, fontSize: "1.0625rem" }}
            >
              <Zap size={20} />
              {loading ? "Decrypting Enforcement Logic..." : "Execute ARES Simulation"}
            </button>
          </form>
        </div>

        {/* Result */}
        <div className="glass-card" style={{ padding: 40, background: "#ffffff", display: "flex", flexDirection: "column", minHeight: "100%" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 32 }}>
            <div style={{ color: "var(--sg-accent)" }}><Shield size={24} /></div>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--sg-text-primary)" }}>AI Intelligence Output</h3>
          </div>

          {!result ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "var(--sg-text-muted)", textAlign: "center" }}>
              <Shield size={80} style={{ opacity: 0.05, marginBottom: 24 }} />
              <p style={{ maxWidth: 280, fontSize: "1rem" }}>Awaiting high-confidence match data to generate automated enforcement decisioning.</p>
            </div>
          ) : (
            <div className="animate-fade-in" style={{ flex: 1 }}>
              <div style={{ background: "var(--sg-bg-secondary)", border: "1px solid var(--sg-border)", borderRadius: 20, padding: 32, marginBottom: 40, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "var(--sg-text-muted)", textTransform: "uppercase", marginBottom: 12, letterSpacing: "0.05em" }}>Decision Category</div>
                  {categoryBadge(result.category)}
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "var(--sg-text-muted)", textTransform: "uppercase", marginBottom: 12, letterSpacing: "0.05em" }}>Severity Score</div>
                  <div style={{ fontSize: "2.5rem", fontWeight: 800, color: "var(--sg-text-primary)", letterSpacing: "-0.04em", lineHeight: 1 }}>
                    {(result.severity_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="glass-card" style={{ marginBottom: 40, padding: 24, border: "1px solid var(--sg-border)", background: "#fff" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.75rem", fontWeight: 700, color: "var(--sg-text-muted)", textTransform: "uppercase", marginBottom: 16, letterSpacing: "0.05em" }}>
                   <Info size={16} style={{ color: "var(--sg-accent)" }} /> AI Forensic Reasoning
                </div>
                <p style={{ color: "var(--sg-text-primary)", fontSize: "1rem", lineHeight: 1.7 }}>
                  {result.ai_analysis.reasoning}
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                <div style={{ padding: 20, borderRadius: 16, border: "1px solid var(--sg-border)", background: "var(--sg-bg-secondary)" }}>
                  <div style={{ fontSize: 11, color: "var(--sg-text-muted)", fontWeight: 700, textTransform: "uppercase", marginBottom: 4 }}>Uploader Risk</div>
                  <div style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--sg-success)" }}>Low Frequency</div>
                </div>
                <div style={{ padding: 20, borderRadius: 16, border: "1px solid var(--sg-border)", background: "var(--sg-bg-secondary)" }}>
                  <div style={{ fontSize: 11, color: "var(--sg-text-muted)", fontWeight: 700, textTransform: "uppercase", marginBottom: 4 }}>Primary Action</div>
                  <div style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--sg-accent)" }}>{result.ai_analysis.suggested_action}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div style={{ marginTop: 60 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
            <History size={24} style={{ color: "var(--sg-accent)" }} />
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--sg-text-primary)" }}>Recent Simulations</h3>
          </div>
          <div className="sg-table-container">
            <table className="sg-table">
              <thead>
                <tr>
                  <th>Match ID</th>
                  <th>Asset</th>
                  <th>Verdict</th>
                  <th>Severity</th>
                  <th>Platform</th>
                  <th>Timestamps</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 700, color: "var(--sg-text-primary)" }}>{h.match_id as string}</td>
                    <td>{h.content_id as string}</td>
                    <td>{categoryBadge(h.category as string)}</td>
                    <td style={{ fontWeight: 700 }}>{((h.severity_score as number) * 100).toFixed(0)}%</td>
                    <td><span className="badge badge-medium">{h.platform as string}</span></td>
                    <td style={{ fontSize: 13, color: "var(--sg-text-muted)" }}>
                      {h.analyzed_at ? new Date(h.analyzed_at as string).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
