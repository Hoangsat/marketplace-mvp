"use client";

// app/login/page.tsx

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import { setToken } from "@/lib/auth";
import { showToast } from "@/components/Toast";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export default function LoginPage() {
  const router = useRouter();
  const { messages } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      // OAuth2PasswordRequestForm requires form-encoded body
      const body = new URLSearchParams();
      body.set("username", email);
      body.set("password", password);

      const res = await fetch(
        `${API_BASE_URL}/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body.toString(),
        }
      );

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data?.detail ?? messages.loginFailed);
      }

      const data: TokenResponse = await res.json();
      setToken(data.access_token);
      showToast(messages.loggedIn, "success");
      router.refresh();
      router.push("/");
    } catch (err: unknown) {
      showToast(
        err instanceof Error ? err.message : messages.loginFailed,
        "error"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-12">
      <h1 className="text-2xl font-bold mb-6">{messages.loginTitle}</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">{messages.email}</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">
            {messages.password}
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-orange-600 text-white py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50"
        >
          {loading ? messages.loggingIn : messages.login}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-500 text-center">
        {messages.dontHaveAccount}{" "}
        <Link href="/register" className="text-orange-600 hover:underline">
          {messages.register}
        </Link>
      </p>
    </div>
  );
}
