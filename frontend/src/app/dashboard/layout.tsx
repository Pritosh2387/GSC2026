"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/api";
import Sidebar from "@/components/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
    }
  }, [router]);

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "var(--lp-alt)" }}>
      <Sidebar />
      <main className="page-wrapper" style={{ flex: 1, minWidth: 0 }}>{children}</main>
    </div>
  );
}
