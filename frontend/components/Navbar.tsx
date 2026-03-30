"use client";

// components/Navbar.tsx
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, removeToken } from "@/lib/auth";
import { getCart } from "@/lib/cart";
import { useLanguage } from "@/components/LanguageProvider";

export default function Navbar() {
  const router = useRouter();
  const { language, setLanguage, messages } = useLanguage();
  const [mounted, setMounted] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [cartCount, setCartCount] = useState(0);

  useEffect(() => {
    // Update on storage changes (from other tabs or same-page mutations)
    const handler = () => {
      setLoggedIn(!!getToken());
      setCartCount(getCart().reduce((s, c) => s + c.quantity, 0));
    };

    const timeoutId = window.setTimeout(() => {
      setMounted(true);
      handler();
    }, 0);
    window.addEventListener("storage", handler);
    window.addEventListener("cartUpdated", handler);
    window.addEventListener("authUpdated", handler);
    return () => {
      window.clearTimeout(timeoutId);
      window.removeEventListener("storage", handler);
      window.removeEventListener("cartUpdated", handler);
      window.removeEventListener("authUpdated", handler);
    };
  }, []);

  function handleLogout() {
    removeToken();
    localStorage.removeItem("user");
    setLoggedIn(false);
    router.refresh();
    router.push("/login");
  }

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 shrink-0">
          <Link href="/" className="text-lg font-bold text-orange-600 shrink-0">
            MarketPy
          </Link>

          <div className="flex items-center gap-3 text-sm">
            <Link href="/catalog" className="text-gray-600 hover:text-gray-900">
              {messages.catalog}
            </Link>
          </div>
        </div>

        <div className="flex items-center gap-3 text-sm">
          {!mounted ? (
            <div
              aria-hidden="true"
              className="flex items-center gap-3 text-sm text-transparent"
            >
              <span className="select-none">Orders</span>
              <span className="select-none">Seller</span>
              <span className="select-none">Logout</span>
            </div>
          ) : loggedIn ? (
            <>
              <Link href="/orders" className="text-gray-600 hover:text-gray-900">
                {messages.orders}
              </Link>
              <Link
                href="/seller/dashboard"
                className="text-gray-600 hover:text-gray-900"
              >
                {messages.seller}
              </Link>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
              >
                {messages.logout}
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-gray-600 hover:text-gray-900">
                {messages.login}
              </Link>
              <Link
                href="/register"
                className="bg-orange-600 text-white px-3 py-1.5 rounded hover:bg-orange-700"
              >
                {messages.register}
              </Link>
            </>
          )}

          <Link
            href="/cart"
            className="relative flex items-center gap-1 text-gray-700 hover:text-gray-900"
          >
            <span>{messages.cart}</span>
            {mounted && cartCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-orange-600 text-white text-xs w-4 h-4 rounded-full flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </Link>

          <div className="flex items-center gap-1 rounded-full border border-gray-200 px-2 py-1 text-xs">
            <button
              type="button"
              onClick={() => setLanguage("vi")}
              className={
                language === "vi" ? "font-semibold text-orange-600" : "text-gray-500"
              }
            >
              VI
            </button>
            <span className="text-gray-300">|</span>
            <button
              type="button"
              onClick={() => setLanguage("en")}
              className={
                language === "en" ? "font-semibold text-orange-600" : "text-gray-500"
              }
            >
              EN
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
