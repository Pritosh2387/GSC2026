import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Export a fully static site suitable for Firebase Hosting
  output: "export",
  trailingSlash: true,
};

export default nextConfig;
