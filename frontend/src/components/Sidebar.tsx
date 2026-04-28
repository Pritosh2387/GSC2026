"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bell,
  Shield,
  Video,
  FileUp,
  LogOut,
  Send, // Added for Telegram
} from "lucide-react";
import { clearToken } from "@/lib/api";
import { useRouter } from "next/navigation";

const NAV = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Alerts", href: "/dashboard/alerts", icon: Bell },
  { label: "Telegram Monitor", href: "/dashboard/telegram", icon: Send },
  { label: "ARES Engine", href: "/dashboard/ares", icon: Shield },
  { label: "Deepfake Detector", href: "/dashboard/deepfake", icon: Video },
  {
    label: "Register Content",
    href: "/dashboard/register-content",
    icon: FileUp,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon">PK</div>
        <div>
          <div className="logo-text">Piraksha</div>
          <div className="logo-sub">AI Platform</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section">Main</div>
        {NAV.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-link ${isActive ? "active" : ""}`}
            >
              <Icon size={18} className="sidebar-icon" />
              {item.label}
            </Link>
          );
        })}

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="sidebar-link"
          style={{
            border: "none",
            background: "none",
            cursor: "pointer",
            width: "100%",
            textAlign: "left",
          }}
        >
          <LogOut size={18} className="sidebar-icon" />
          Logout
        </button>
      </nav>
    </aside>
  );
}
