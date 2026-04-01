"use client";

// components/Navbar.tsx
import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import HeaderSearch from "@/components/HeaderSearch";
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
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center gap-3">
        <div className="flex min-w-0 flex-1 items-center gap-3 sm:gap-4 shrink-0">
          <Link
            href="/"
            className="shrink-0 whitespace-nowrap text-base font-bold text-orange-600 sm:text-lg"
          >
            MarketPy
          </Link>

          <div className="flex items-center gap-3 text-xs sm:text-sm">
            <Link
              href="/catalog"
              className="whitespace-nowrap text-gray-600 hover:text-gray-900"
            >
              {messages.catalog}
            </Link>
          </div>
        </div>

        <div className="order-last w-full lg:order-none lg:flex-1 lg:max-w-xl">
          <Suspense
            fallback={
              <div
                aria-hidden="true"
                className="h-11 rounded-2xl border border-gray-200 bg-gray-50"
              />
            }
          >
            <HeaderSearch />
          </Suspense>
        </div>

        <div className="ml-auto flex max-w-full flex-wrap items-center justify-end gap-x-3 gap-y-2 text-xs sm:flex-nowrap sm:text-sm shrink-0">
          {!mounted ? (
            <div
              aria-hidden="true"
              className="flex flex-wrap items-center justify-end gap-x-3 gap-y-2 text-xs text-transparent sm:flex-nowrap sm:text-sm"
            >
              <span className="select-none">Orders</span>
              <span className="select-none">Seller</span>
              <span className="select-none">Logout</span>
            </div>
          ) : loggedIn ? (
            <>
              <Link
                href="/orders"
                className="whitespace-nowrap text-gray-600 hover:text-gray-900"
              >
                {messages.orders}
              </Link>
              <Link
                href="/seller/dashboard"
                className="whitespace-nowrap text-gray-600 hover:text-gray-900"
              >
                {messages.seller}
              </Link>
              <button
                onClick={handleLogout}
                className="whitespace-nowrap text-gray-600 hover:text-gray-900"
              >
                {messages.logout}
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="whitespace-nowrap text-gray-600 hover:text-gray-900"
              >
                {messages.login}
              </Link>
              <Link
                href="/register"
                className="whitespace-nowrap rounded bg-orange-600 px-3 py-1.5 text-white hover:bg-orange-700"
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
