"use client";

import Link from "next/link";
import { ShieldCheck, Zap, ArrowRight, Check, Lock, Globe } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="stripe-theme">
      {/* Navbar */}
      <nav className="lp-navbar">
        <div
          className="lp-container"
          style={{
            width: "100%",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Link href="/" className="lp-logo">
            <div
              style={{
                padding: 6,
                background: "var(--lp-accent)",
                borderRadius: 8,
                color: "white",
              }}
            >
              <ShieldCheck size={20} />
            </div>
            Piraksha
          </Link>

          <div className="lp-nav-links">
            <Link href="#features" className="lp-nav-link">
              Features
            </Link>
            <Link href="#showcase" className="lp-nav-link">
              Product
            </Link>
            <Link href="#pricing" className="lp-nav-link">
              Pricing
            </Link>
          </div>

          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <Link href="/login" className="lp-nav-link">
              Sign in
            </Link>
            <Link href="/register" className="lp-btn-primary">
              Sign up
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="lp-hero" style={{ padding: "100px 0" }}>
        <div
          className="lp-container"
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 80,
            alignItems: "center",
          }}
        >
          {/* Left Column - Text & CTA */}
          <div style={{ textAlign: "left" }}>
            <h1
              style={{
                fontSize: "3.5rem",
                fontWeight: 800,
                lineHeight: 1.2,
                marginBottom: 24,
                color: "var(--lp-text-main)",
              }}
            >
              Complete{" "}
              <span style={{ color: "var(--lp-accent)" }}>protection</span> for
              your{" "}
              <span style={{ color: "var(--lp-accent)" }}>digital content</span>
              .
            </h1>
            <p
              style={{
                fontSize: "1.125rem",
                color: "var(--lp-text-sec)",
                marginBottom: 40,
                lineHeight: 1.7,
              }}
            >
              Identify and stop unauthorized distribution of your media assets
              across all social and chat networks instantly.
            </p>
            <Link
              href="/register"
              className="lp-btn-primary"
              style={{
                padding: "14px 32px",
                fontSize: "1rem",
                display: "inline-block",
              }}
            >
              Get Started
            </Link>
          </div>

          {/* Right Column - Image with Badge */}
          <div
            style={{
              position: "relative",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            {/* Image */}
            <img
              src="/home.png"
              alt="Hero visual"
              style={{
                width: 500,
                height: 500,
                objectFit: "cover",
                borderRadius: "16px",
                position: "relative",
                zIndex: 1,
                boxShadow: "0 20px 60px rgba(0,0,0,0.12)",
              }}
            />
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section id="features" className="lp-section-alt">
        <div className="lp-container">
          <div className="lp-grid">
            <div className="lp-card">
              <div style={{ color: "var(--lp-accent)", marginBottom: 24 }}>
                <Zap size={32} />
              </div>
              <h3>Instant Alerts</h3>
              <p style={{ marginTop: 12 }}>
                Receive notifications the moment your content appears on
                unauthorized channels.
              </p>
            </div>

            <div className="lp-card">
              <div style={{ color: "var(--lp-accent)", marginBottom: 24 }}>
                <Lock size={32} />
              </div>
              <h3>Smart Enforcement</h3>
              <p style={{ marginTop: 12 }}>
                Automatically resolve content matches with our powerful decision
                engine.
              </p>
            </div>

            <div className="lp-card">
              <div style={{ color: "var(--lp-accent)", marginBottom: 24 }}>
                <Globe size={32} />
              </div>
              <h3>Global Monitoring</h3>
              <p style={{ marginTop: 12 }}>
                Continuous surveillance across Telegram, social platforms, and
                the open web.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Showcase Section */}
      <section id="showcase" className="lp-section">
        <div className="lp-container">
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 80,
              alignItems: "center",
            }}
          >
            <div>
              <h2 style={{ fontSize: "2.5rem", marginBottom: 24 }}>
                Everything you need to <br />
                protect your assets.
              </h2>
              <p style={{ marginBottom: 32, fontSize: "1.125rem" }}>
                Our simple dashboard gives you a clear view of your content
                across the internet. Manage alerts, verify matches, and enforce
                your rights with one click.
              </p>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: 16,
                }}
              >
                {[
                  "Live Channel Monitoring",
                  "Content Image Identification",
                  "Automated Takedowns",
                  "Detailed Analytics",
                ].map((f) => (
                  <li
                    key={f}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      fontWeight: 600,
                      color: "var(--lp-text-main)",
                    }}
                  >
                    <Check size={20} color="var(--lp-accent)" /> {f}
                  </li>
                ))}
              </ul>
            </div>
            <div
              style={{
                padding: 12,
                background: "var(--lp-alt)",
                borderRadius: 16,
              }}
            >
              <img
                src="/SportsVidProd.jpg"
                alt="Landing hero"
                style={{
                  width: "100%",
                  borderRadius: 12,
                  display: "block",
                  boxShadow: "var(--lp-shadow-sm)",
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="lp-section-alt">
        <div className="lp-container">
          <div className="lp-grid">
            {[
              {
                q: "Piraksha has simplified our rights management completely. It just works.",
                n: "Alex Thompson",
                r: "Digital Director",
                avatar: "/avatar-alex.svg",
              },
              {
                q: "The accuracy of the matching system is incredible. Highly recommended.",
                n: "Sarah Chen",
                r: "IP Legal Head",
                avatar: "/avatar-sarah.svg",
              },
            ].map((t, i) => (
              <div key={i} className="lp-card" style={{ textAlign: "left" }}>
                <p
                  style={{
                    fontSize: "1.125rem",
                    fontStyle: "italic",
                    marginBottom: 24,
                  }}
                >
                  &ldquo;{t.q}&rdquo;
                </p>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <img
                    src={t.avatar}
                    alt={`${t.n} avatar`}
                    style={{
                      width: 48,
                      height: 48,
                      borderRadius: "50%",
                      objectFit: "cover",
                      border: "2px solid var(--lp-accent)",
                    }}
                  />
                  <div>
                    <div
                      style={{ fontWeight: 700, color: "var(--lp-text-main)" }}
                    >
                      {t.n}
                    </div>
                    <div
                      style={{
                        fontSize: "0.875rem",
                        color: "var(--lp-text-sec)",
                      }}
                    >
                      {t.r}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="lp-section">
        <div className="lp-container">
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <h2 style={{ fontSize: "2.5rem" }}>Simple Pricing</h2>
            <p style={{ fontSize: "1.125rem", marginTop: 12 }}>
              Choose the plan that fits your needs.
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: 32,
              maxWidth: 900,
              margin: "0 auto",
            }}
          >
            <div
              className="lp-card"
              style={{
                textAlign: "center",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                minHeight: "100%",
              }}
            >
              <div>
                <div
                  style={{
                    fontWeight: 600,
                    textTransform: "uppercase",
                    fontSize: "0.875rem",
                    marginBottom: 16,
                  }}
                >
                  Starter
                </div>
                <div
                  style={{
                    fontSize: "3rem",
                    fontWeight: 800,
                    color: "var(--lp-text-main)",
                  }}
                >
                  $499
                  <span
                    style={{
                      fontSize: "1.125rem",
                      color: "var(--lp-text-sec)",
                      fontWeight: 500,
                    }}
                  >
                    /mo
                  </span>
                </div>
                <ul
                  style={{
                    listStyle: "none",
                    padding: 0,
                    margin: "32px 0",
                    textAlign: "left",
                    display: "flex",
                    flexDirection: "column",
                    gap: 12,
                  }}
                >
                  {["10 Media Assets", "Daily Monitoring", "Email Support"].map(
                    (f) => (
                      <li
                        key={f}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                        }}
                      >
                        <Check size={18} color="var(--lp-accent)" /> {f}
                      </li>
                    ),
                  )}
                </ul>
              </div>
              <Link
                href="/register"
                className="lp-btn-secondary"
                style={{ width: "100%", justifyContent: "center" }}
              >
                Get Started
              </Link>
            </div>

            <div
              className="lp-card"
              style={{
                textAlign: "center",
                borderColor: "var(--lp-accent)",
                borderWidth: 2,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                minHeight: "100%",
              }}
            >
              <div
                style={{
                  fontWeight: 600,
                  textTransform: "uppercase",
                  fontSize: "0.875rem",
                  marginBottom: 16,
                  color: "var(--lp-accent)",
                }}
              >
                Professional
              </div>
              <div
                style={{
                  fontSize: "3rem",
                  fontWeight: 800,
                  color: "var(--lp-text-main)",
                }}
              >
                $1,299
                <span
                  style={{
                    fontSize: "1.125rem",
                    color: "var(--lp-text-sec)",
                    fontWeight: 500,
                  }}
                >
                  /mo
                </span>
              </div>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  margin: "32px 0",
                  textAlign: "left",
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                }}
              >
                {[
                  "Unlimited Assets",
                  "Real-time Monitoring",
                  "24/7 Support",
                  "API Access",
                ].map((f) => (
                  <li
                    key={f}
                    style={{ display: "flex", alignItems: "center", gap: 8 }}
                  >
                    <Check size={18} color="var(--lp-accent)" /> {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/register"
                className="lp-btn-primary"
                style={{ width: "100%", justifyContent: "center" }}
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="lp-footer">
        <div className="lp-container">
          <div className="lp-footer-grid">
            <div>
              <Link href="/" className="lp-logo" style={{ marginBottom: 24 }}>
                <div
                  style={{
                    padding: 6,
                    background: "var(--lp-accent)",
                    borderRadius: 8,
                    color: "white",
                  }}
                >
                  <ShieldCheck size={20} />
                </div>
                Piraksha
              </Link>
              <p style={{ maxWidth: 300 }}>
                Leading digital rights management platform for sports media and
                content creators.
              </p>
            </div>
            <div>
              <h4 style={{ marginBottom: 16, fontSize: "1rem" }}>Product</h4>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                }}
              >
                <li>
                  <Link href="#features" className="lp-nav-link">
                    Monitoring
                  </Link>
                </li>
                <li>
                  <Link href="#showcase" className="lp-nav-link">
                    Enforcement
                  </Link>
                </li>
                <li>
                  <Link href="#pricing" className="lp-nav-link">
                    Pricing
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 style={{ marginBottom: 16, fontSize: "1rem" }}>Company</h4>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                }}
              >
                <li>
                  <Link href="#" className="lp-nav-link">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="#" className="lp-nav-link">
                    Legal
                  </Link>
                </li>
                <li>
                  <Link href="#" className="lp-nav-link">
                    Privacy
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 style={{ marginBottom: 16, fontSize: "1rem" }}>Social</h4>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                }}
              >
                <li>
                  <Link href="#" className="lp-nav-link">
                    Twitter
                  </Link>
                </li>
                <li>
                  <Link href="#" className="lp-nav-link">
                    LinkedIn
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div
            style={{ marginTop: 64, textAlign: "center", fontSize: "0.875rem" }}
          >
            © {new Date().getFullYear()} Piraksha. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
