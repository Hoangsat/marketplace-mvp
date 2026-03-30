import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8011",
        pathname: "/static/**",
      },
    ],
  },
};

export default nextConfig;
