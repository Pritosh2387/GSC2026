"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login, setToken } from "@/lib/api";
import { ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await login(email, password);
      setToken(res.access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page bg-dots">
      <div className="glass-card auth-card animate-fade-in">
        {/* Logo */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginBottom: 48,
          }}
        >
          <Link
            href="/"
            className="logo-icon"
            style={{
              width: 64,
              height: 64,
              borderRadius: 16,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              textDecoration: "none",
            }}
          >
            <ShieldCheck size={36} />
          </Link>
        </div>

        <h1
          style={{
            fontSize: "2rem",
            fontWeight: 800,
            textAlign: "center",
            color: "var(--lp-text-main)",
            marginBottom: 12,
            letterSpacing: "-0.03em",
          }}
        >
          Sign in
        </h1>
        <p
          style={{
            textAlign: "center",
            color: "var(--lp-text-sec)",
            marginBottom: 40,
            fontSize: "1.125rem",
          }}
        >
          Access your content protection dashboard.
        </p>

        {error && (
          <div
            style={{
              background: "#fef2f2",
              border: "1px solid #fee2e2",
              padding: "16px",
              borderRadius: 12,
              color: "#b91c1c",
              fontSize: 14,
              marginBottom: 32,
              fontWeight: 500,
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 24 }}>
            <label
              style={{
                display: "block",
                fontSize: 11,
                fontWeight: 700,
                color: "var(--sg-text-muted)",
                marginBottom: 10,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              Corporate Email
            </label>
            <input
              type="email"
              className="input-field"
              placeholder="operator@piraksha.ai"
              style={{ height: 50 }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: 32 }}>
            <label
              style={{
                display: "block",
                fontSize: 11,
                fontWeight: 700,
                color: "var(--sg-text-muted)",
                marginBottom: 10,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              Encrypted Password
            </label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              style={{ height: 50 }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: "100%", height: 54, fontSize: "1rem" }}
          >
            {loading ? "Decrypting Credentials…" : "Authenticate Access"}
          </button>
        </form>

        <div
          style={{
            textAlign: "center",
            marginTop: 40,
            fontSize: 14,
            color: "var(--lp-text-sec)",
          }}
        >
          New to Piraksha?{" "}
          <Link
            href="/register"
            style={{
              color: "var(--lp-accent)",
              fontWeight: 700,
              textDecoration: "none",
            }}
          >
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
}
