"use client";

import { FormEvent, useState, useRef } from "react";
import { registerContent } from "@/lib/api";
import { Upload, CheckCircle, FilePlus, Info, ShieldCheck, Shield } from "lucide-react";

export default function RegisterContentPage() {
  const [file, setFile] = useState<File | null>(null);
  const [contentName, setContentName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState<{
    content_name: string;
    media_type: string;
    fingerprint_dim: number;
  } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file || !contentName) return;
    setLoading(true);
    setError("");
    setSuccess(null);
    try {
      const r = await registerContent(file, contentName);
      if ("error" in r) {
        setError(r.error as unknown as string);
      } else {
        setSuccess(r);
        setFile(null);
        setContentName("");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
    setLoading(false);
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Add Protected Content</h1>
        <p>Upload your original media to start monitoring and protecting it online.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 40 }}>
        <div className="glass-card" style={{ padding: 48 }}>
          {success ? (
            <div className="animate-fade-in" style={{ textAlign: "center" }}>
              <div
                style={{
                  width: 100,
                  height: 100,
                  borderRadius: "50%",
                  background: "var(--sg-bg-secondary)",
                  border: "6px solid var(--sg-success)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 32px",
                  boxShadow: "0 0 20px rgba(16, 185, 129, 0.15)"
                }}
              >
                <CheckCircle size={56} style={{ color: "var(--sg-success)" }} />
              </div>
              <h2 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--lp-text-main)", marginBottom: 12, letterSpacing: "-0.03em" }}>Content Added Successfully</h2>
              <p style={{ color: "var(--lp-text-sec)", marginBottom: 48, maxWidth: 440, margin: "0 auto 48px", fontSize: "1.125rem", lineHeight: 1.6 }}>
                Your content is now being monitored. We will alert you if any matches are found on supported channels and networks.
              </p>

               <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 20, marginBottom: 48 }}>
                <div style={{ padding: 20, background: "var(--lp-alt)", borderRadius: 16, border: "1px solid var(--lp-border)" }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Name</div>
                  <div style={{ fontWeight: 700, color: "var(--lp-text-main)" }}>{success.content_name}</div>
                </div>
                <div style={{ padding: 20, background: "var(--lp-alt)", borderRadius: 16, border: "1px solid var(--lp-border)" }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Type</div>
                  <div style={{ fontWeight: 700, color: "var(--lp-text-main)", textTransform: "capitalize" }}>{success.media_type}</div>
                </div>
                <div style={{ padding: 20, background: "var(--lp-alt)", borderRadius: 16, border: "1px solid var(--lp-border)" }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "var(--lp-text-sec)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>Fingerprint</div>
                  <div style={{ fontWeight: 700, color: "var(--lp-accent)" }}>{success.fingerprint_dim} bit</div>
                </div>
              </div>

              <button className="btn-secondary" onClick={() => setSuccess(null)} style={{ border: "none", fontSize: "1rem" }}>
                Register Another Asset
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 32 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 700, color: "var(--lp-text-sec)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>Title</label>
                <input
                  className="input-field"
                  placeholder="e.g. Football Match Highlights"
                  style={{ height: 52 }}
                  value={contentName}
                  onChange={(e) => setContentName(e.target.value)}
                  required
                />
              </div>

              <div style={{ marginBottom: 40 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 700, color: "var(--lp-text-sec)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>Media File</label>
                <div
                  onClick={() => inputRef.current?.click()}
                  style={{
                    border: "2px dashed var(--lp-border)",
                    borderRadius: 20,
                    padding: "80px 48px",
                    textAlign: "center",
                    cursor: "pointer",
                    background: file ? "var(--lp-alt)" : "transparent",
                    transition: "all 0.2s ease"
                  }}
                  onDragOver={(e) => { e.preventDefault(); e.currentTarget.style.borderColor = "var(--lp-accent)"; }}
                  onDragLeave={(e) => { e.currentTarget.style.borderColor = "var(--lp-border)"; }}
                  onDrop={(e) => { e.preventDefault(); e.currentTarget.style.borderColor = "var(--lp-border)"; const f = e.dataTransfer.files[0]; if (f) setFile(f); }}
                >
                  <div style={{ width: 64, height: 64, borderRadius: "50%", background: "var(--lp-accent-glow)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px", color: "var(--lp-accent)" }}>
                    <Upload size={28} />
                  </div>
                  {file ? (
                    <div>
                      <p style={{ fontWeight: 700, color: "var(--lp-text-main)", fontSize: "1.125rem" }}>{file.name}</p>
                      <p style={{ fontSize: 14, color: "var(--lp-text-sec)", marginTop: 8 }}>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  ) : (
                    <div>
                      <p style={{ fontWeight: 600, color: "var(--lp-text-main)", fontSize: "1.125rem" }}>Upload master file</p>
                      <p style={{ fontSize: 14, color: "var(--lp-text-sec)", marginTop: 8 }}>Detection is most accurate with high resolution files.</p>
                    </div>
                  )}
                  <input
                    ref={inputRef}
                    type="file"
                    accept="image/*,video/*"
                    style={{ display: "none" }}
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </div>
              </div>

              {error && <div style={{ marginBottom: 32, padding: 16, borderRadius: 12, background: "#fef2f2", color: "#b91c1c", border: "1px solid #fee2e2", fontSize: 14, fontWeight: 500 }}>{error}</div>}

              <button
                type="submit"
                className="btn-primary"
                disabled={!file || !contentName || loading}
                style={{ width: "100%", height: 56, fontSize: "1.0625rem" }}
              >
                {loading ? "Decrypting Artifacts..." : "Register & Protect Asset"}
              </button>
            </form>
          )}
        </div>

        {/* Info Sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
          <div className="glass-card" style={{ padding: 32 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
              <ShieldCheck size={24} style={{ color: "var(--lp-accent)" }} />
              <h3 style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--lp-text-main)" }}>Smart Protection</h3>
            </div>
            <p style={{ fontSize: 14, color: "var(--lp-text-sec)", lineHeight: 1.7 }}>
              Advanced matching identifies your content even after cropping, color changes, or watermarking.
            </p>
          </div>

          <div className="glass-card" style={{ padding: 32 }}>
             <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
               <Info size={24} style={{ color: "var(--lp-accent)" }} />
               <h3 style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--lp-text-main)" }}>Guidelines</h3>
             </div>
             <ul style={{ padding: 0, margin: 0, listStyle: "none", fontSize: 14, color: "var(--lp-text-sec)", display: "flex", flexDirection: "column", gap: 16 }}>
                <li style={{ display: "flex", gap: 10 }}><span>•</span> <span>Target minimum 720p resolution.</span></li>
                <li style={{ display: "flex", gap: 10 }}><span>•</span> <span>Provide a file with at least 5s of content.</span></li>
                <li style={{ display: "flex", gap: 10 }}><span>•</span> <span>Avoid files with long intro sequences.</span></li>
             </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
