"use client";

// components/Toast.tsx
// Simple toast/alert — call showToast(message, type) globally.

import { useEffect, useState } from "react";

type ToastType = "success" | "error" | "info";

interface ToastState {
  message: string;
  type: ToastType;
  id: number;
}

let toastId = 0;
const listeners: Set<(t: ToastState | null) => void> = new Set();

export function showToast(message: string, type: ToastType = "info") {
  const t = { message, type, id: ++toastId };
  listeners.forEach((fn) => fn(t));
}

export default function Toast() {
  const [toast, setToast] = useState<ToastState | null>(null);

  useEffect(() => {
    const fn = (t: ToastState | null) => {
      setToast(t);
      if (t) setTimeout(() => setToast(null), 3000);
    };
    listeners.add(fn);
    return () => { listeners.delete(fn); };
  }, []);

  if (!toast) return null;

  const colors: Record<ToastType, string> = {
    success: "bg-green-600",
    error: "bg-red-600",
    info: "bg-gray-800",
  };

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 text-white px-4 py-3 rounded-lg shadow-lg text-sm max-w-xs ${colors[toast.type]}`}
    >
      {toast.message}
    </div>
  );
}
