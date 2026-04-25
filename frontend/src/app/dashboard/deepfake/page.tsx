"use client";

import { FormEvent, useState, useRef } from "react";
import { predictVideo, type DeepfakeResult } from "@/lib/api";
import { Upload, Video, AlertTriangle, CheckCircle, FileVideo, ShieldCheck } from "lucide-react";

export default function DeepfakePage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<DeepfakeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await predictVideo(file);
      setResult(r);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    }
    setLoading(false);
  }

  const isFake = result ? result.prediction === 1 : null;
  const confidence = result ? result.probability * 100 : 0;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Deepfake Detector</h1>
        <p>AI-powered video forensic analysis to detect synthetic manipulation.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40, alignItems: "stretch" }}>
        {/* Upload */}
        <div className="glass-card" style={{ padding: 40, display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 32 }}>
            <div style={{ color: "var(--sg-accent)" }}><FileVideo size={24} /></div>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--sg-text-primary)" }}>Upload Media</h3>
          </div>

          <form onSubmit={handleSubmit} style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            <div
              onClick={() => inputRef.current?.click()}
              style={{
                border: "2px dashed var(--sg-border)",
                borderRadius: 20,
                padding: "80px 32px",
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.2s ease",
                background: file ? "var(--sg-accent-glow)" : "transparent",
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center"
              }}
              onDragOver={(e) => {
                e.preventDefault();
                e.currentTarget.style.borderColor = "var(--sg-accent)";
              }}
              onDragLeave={(e) => {
                e.currentTarget.style.borderColor = "var(--sg-border)";
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.currentTarget.style.borderColor = "var(--sg-border)";
                const f = e.dataTransfer.files[0];
                if (f) setFile(f);
              }}
            >
              <div style={{ 
                width: 80, height: 80, borderRadius: "50%", 
                background: file ? "rgba(99, 91, 255, 0.15)" : "#f8fafc",
                display: "flex", alignItems: "center", justifyContent: "center",
                margin: "0 auto 24px", color: file ? "var(--sg-accent)" : "var(--sg-text-muted)"
              }}>
                <Upload size={32} />
              </div>

              {file ? (
                <div>
                  <p style={{ color: "var(--sg-text-primary)", fontWeight: 700, fontSize: "1.125rem" }}>{file.name}</p>
                  <p style={{ fontSize: 14, color: "var(--sg-text-secondary)", marginTop: 8 }}>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <div>
                  <p style={{ color: "var(--sg-text-primary)", fontWeight: 600, fontSize: "1.125rem" }}>Drag and drop forensic sample</p>
                  <p style={{ fontSize: 14, color: "var(--sg-text-secondary)", marginTop: 8 }}>Supports MP4, AVI, MOV (Max 50MB)</p>
                </div>
              )}
              <input
                ref={inputRef}
                type="file"
                accept="video/*"
                style={{ display: "none" }}
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>

            {error && (
              <div style={{ marginTop: 24, padding: 16, borderRadius: 12, background: "#fef2f2", color: "#991b1b", fontSize: 14, border: "1px solid #fee2e2", fontWeight: 500 }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              className="lp-btn-primary"
              disabled={!file || loading}
              style={{ width: "100%", marginTop: 32, padding: "16px", fontSize: "1.0625rem" }}
            >
              {loading ? "Decrypting Artifacts..." : "Execute Forensic Scan"}
            </button>
          </form>
        </div>

        {/* Result */}
        <div className="glass-card" style={{ padding: 40, background: "#ffffff", display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 32 }}>
            <div style={{ color: "var(--sg-accent)" }}><ShieldCheck size={24} /></div>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--sg-text-primary)" }}>Detection Report</h3>
          </div>

          {result === null ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "var(--sg-text-muted)", textAlign: "center" }}>
              <Video size={80} style={{ opacity: 0.05, marginBottom: 24 }} />
              <p style={{ maxWidth: 280, fontSize: "1rem" }}>Await ingestion of media to generate deep learning forensic analysis.</p>
            </div>
          ) : (
            <div className="animate-fade-in" style={{ textAlign: "center", flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <div
                style={{
                  width: 160,
                  height: 160,
                  borderRadius: "50%",
                  margin: "0 auto 32px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: isFake ? "#fef2f2" : "#f0fdf4",
                  border: `6px solid ${isFake ? "var(--sg-danger)" : "var(--sg-success)"}`,
                  boxShadow: `0 0 30px ${isFake ? "rgba(239,68,68,0.15)" : "rgba(16,185,129,0.15)"}`
                }}
              >
                {isFake ? (
                  <AlertTriangle size={80} style={{ color: "var(--sg-danger)" }} />
                ) : (
                  <CheckCircle size={80} style={{ color: "var(--sg-success)" }} />
                )}
              </div>

              <h2 style={{ fontSize: "2rem", fontWeight: 800, color: isFake ? "var(--sg-danger)" : "var(--sg-success)", marginBottom: 12, letterSpacing: "-0.03em" }}>
                {isFake ? "Synthetic Fraud Detected" : "Media Verified Authentic"}
              </h2>

              <p style={{ color: "var(--sg-text-secondary)", fontSize: "1.125rem", marginBottom: 48, maxWidth: 380, margin: "0 auto 48px" }}>
                {isFake
                  ? "Analysis confirms presence of high-confidence AI-generated facial artifacts."
                  : "Scanning complete. No evidence of malicious generative manipulation found."}
              </p>

              <div style={{ padding: 32, borderRadius: 20, background: "var(--sg-bg-secondary)", border: "1px solid var(--sg-border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <span style={{ fontSize: 13, fontWeight: 700, color: "var(--sg-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Forensic Confidence</span>
                  <span style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--sg-text-primary)" }}>{confidence.toFixed(1)}%</span>
                </div>
                <div style={{ height: 12, background: "rgba(0,0,0,0.05)", borderRadius: 6, overflow: "hidden" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${confidence}%`,
                      background: isFake ? "var(--sg-danger)" : "var(--sg-success)",
                      transition: "width 2s cubic-bezier(0.34, 1.56, 0.64, 1)",
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
