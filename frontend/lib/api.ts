// lib/api.ts
// Typed fetch wrapper that prepends API base URL and attaches JWT automatically.

import { getToken } from "@/lib/auth";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

function normalizePath(path: string): string {
  const pathWithoutQuery = path.split("?")[0] ?? path;
  const trimmedPath = pathWithoutQuery.replace(/\/+$/, "");
  return trimmedPath || "/";
}

function shouldAttachAuth(path: string, method?: string): boolean {
  const normalizedPath = normalizePath(path);
  const normalizedMethod = (method ?? "GET").toUpperCase();

  if (normalizedMethod === "GET") {
    if (
      normalizedPath === "/categories" ||
      normalizedPath === "/games" ||
      normalizedPath === "/platforms" ||
      /^\/platforms\/[^/]+$/.test(normalizedPath) ||
        normalizedPath === "/offer-types" ||
        normalizedPath === "/products" ||
        /^\/products\/\d+$/.test(normalizedPath) ||
        normalizedPath === "/api/search" ||
        normalizedPath === "/api/search/suggest" ||
        /^\/api\/catalog\/.+$/.test(normalizedPath) ||
        /^\/api\/sellers\/[^/]+$/.test(normalizedPath)
    ) {
      return false;
    }
  }

  if (normalizedMethod === "POST" && normalizedPath === "/auth/register") {
    return false;
  }

  return true;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token && shouldAttachAuth(path, options.method)) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Only set Content-Type to JSON if we're NOT sending FormData
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let message = `API error ${res.status}`;
    try {
      const data = await res.json();
      message = data?.detail ?? message;
    } catch {
      // ignore parse errors
    }
    throw new Error(message);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}
