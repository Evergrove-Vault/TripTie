import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  // Используем API routes вместо rewrites для более надежного проксирования
};

export default nextConfig;
