"use client";

// app/register/page.tsx

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";

const NICKNAME_PATTERN = /^[A-Za-z0-9_.-]+$/;

export default function RegisterPage() {
  const router = useRouter();
  const { messages } = useLanguage();
  const [email, setEmail] = useState("");
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [formError, setFormError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError("");

    const trimmedNickname = nickname.trim();

    if (!trimmedNickname) {
      setFormError(messages.nicknameRequired);
      return;
    }

    if (trimmedNickname.length < 3 || trimmedNickname.length > 30) {
      setFormError(messages.nicknameLengthError);
      return;
    }

    if (!NICKNAME_PATTERN.test(trimmedNickname)) {
      setFormError(messages.nicknameInvalidError);
      return;
    }

    if (password !== confirmPassword) {
      setFormError(messages.passwordsDoNotMatch);
      return;
    }

    setLoading(true);
    try {
      await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, nickname: trimmedNickname, password }),
      });
      showToast(messages.accountCreated, "success");
      router.push("/login");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : messages.registrationFailed;
      setFormError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-12">
      <h1 className="text-2xl font-bold mb-6">{messages.createAccountTitle}</h1>
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
            {messages.nickname}
          </label>
          <input
            type="text"
            required
            minLength={3}
            maxLength={30}
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
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
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">
            {messages.confirmPassword}
          </label>
          <input
            type="password"
            required
            minLength={6}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
          {formError && (
            <p className="text-red-500 text-sm mt-1">{formError}</p>
          )}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-orange-600 text-white py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50"
        >
          {loading ? messages.creatingAccount : messages.createAccount}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-500 text-center">
        {messages.alreadyHaveAccount}{" "}
        <Link href="/login" className="text-orange-600 hover:underline">
          {messages.login}
        </Link>
      </p>
    </div>
  );
}
