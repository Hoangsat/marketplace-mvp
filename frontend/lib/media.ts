import { API_BASE_URL } from "@/lib/api";

export function resolveMediaUrl(path: string | null | undefined): string | null {
  if (!path) {
    return null;
  }

  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  const baseUrl = API_BASE_URL.replace(/\/+$/, "");
  const relativePath = path.startsWith("/") ? path : `/${path}`;
  return `${baseUrl}${relativePath}`;
}
