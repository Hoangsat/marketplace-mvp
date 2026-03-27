// lib/auth.ts
// JWT helpers — read/write from localStorage.

export interface AuthUser {
  id: number;
  email: string;
  is_seller: boolean;
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function setToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("token", token);
    window.dispatchEvent(new Event("authUpdated"));
  }
}

export function removeToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
    window.dispatchEvent(new Event("authUpdated"));
  }
}

export function isLoggedIn(): boolean {
  return !!getToken();
}
