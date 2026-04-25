"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register, setToken } from "@/lib/api";
import { ShieldCheck } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await register(name, email, password);
      setToken(res.access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page bg-dots">
      <div className="glass-card auth-card animate-fade-in">
        {/* Logo */}
        <div style={{ display: "flex", justifyContent: "center", marginBottom: 48 }}>
          <Link href="/" className="logo-icon" style={{ width: 64, height: 64, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center", textDecoration: "none" }}>
            <ShieldCheck size={36} />
          </Link>
        </div>

        <h1 style={{ fontSize: "2rem", fontWeight: 800, textAlign: "center", color: "var(--lp-text-main)", marginBottom: 12, letterSpacing: "-0.03em" }}>
          Create an account
        </h1>
        <p style={{ textAlign: "center", color: "var(--lp-text-sec)", marginBottom: 40, fontSize: "1.125rem" }}>
          Get started with content protection today.
        </p>

        {error && <div style={{ background: "#fef2f2", border: "1px solid #fee2e2", padding: "16px", borderRadius: 12, color: "#b91c1c", fontSize: 14, marginBottom: 32, fontWeight: 500 }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: "var(--sg-text-muted)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>Full Operations Name</label>
            <input
              type="text"
              className="input-field"
              placeholder="Commander Shepard"
              style={{ height: 50 }}
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: "var(--sg-text-muted)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>Official Email</label>
            <input
              type="email"
              className="input-field"
              placeholder="ops@nexus.com"
              style={{ height: 50 }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: 32 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: "var(--sg-text-muted)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>Security Passphrase</label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              style={{ height: 50 }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: "100%", height: 54, fontSize: "1rem" }}
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <div style={{ textAlign: "center", marginTop: 40, fontSize: 14, color: "var(--lp-text-sec)" }}>
          Already have an account?{" "}
          <Link href="/login" style={{ color: "var(--lp-accent)", fontWeight: 700, textDecoration: "none" }}>Sign in</Link>
        </div>
      </div>
    </div>
  );
}
