import type { NextConfig } from "next";
import type { RemotePattern } from "next/dist/shared/lib/image-config";

function toRemotePattern(url: string | undefined): RemotePattern | null {
  if (!url) {
    return null;
  }

  try {
    const parsed = new URL(url);
    const protocol =
      parsed.protocol === "https:"
        ? "https"
        : parsed.protocol === "http:"
          ? "http"
          : null;
    if (!protocol) {
      return null;
    }
    return {
      protocol,
      hostname: parsed.hostname,
      port: parsed.port,
      pathname: "/**",
    };
  } catch {
    return null;
  }
}

const remotePatterns = [
  toRemotePattern(process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"),
  toRemotePattern(process.env.NEXT_PUBLIC_MEDIA_URL),
  toRemotePattern("http://localhost:8000"),
  toRemotePattern("http://127.0.0.1:8000"),
].filter((pattern): pattern is RemotePattern => Boolean(pattern));

const nextConfig: NextConfig = {
  images: {
    remotePatterns,
  },
};

export default nextConfig;
