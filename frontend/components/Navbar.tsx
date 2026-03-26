"use client";

// components/Navbar.tsx
import Link from "next/link";
import { useEffect, useState } from "react";
import { getToken, removeToken } from "@/lib/auth";
import { getCart } from "@/lib/cart";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useState(false);
  const [cartCount, setCartCount] = useState(0);

  useEffect(() => {
    setLoggedIn(!!getToken());
    setCartCount(getCart().reduce((s, c) => s + c.quantity, 0));

    // Update on storage changes (from other tabs or same-page mutations)
    const handler = () => {
      setLoggedIn(!!getToken());
      setCartCount(getCart().reduce((s, c) => s + c.quantity, 0));
    };
    window.addEventListener("storage", handler);
    window.addEventListener("cartUpdated", handler);
    return () => {
      window.removeEventListener("storage", handler);
      window.removeEventListener("cartUpdated", handler);
    };
  }, []);

  function handleLogout() {
    removeToken();
    localStorage.removeItem("user");
    setLoggedIn(false);
    router.push("/login");
  }

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        <Link href="/" className="text-lg font-bold text-orange-600 shrink-0">
          MarketPy
        </Link>

        <div className="flex items-center gap-3 text-sm">
          {loggedIn ? (
            <>
              <Link href="/orders" className="text-gray-600 hover:text-gray-900">
                Orders
              </Link>
              <Link href="/seller/dashboard" className="text-gray-600 hover:text-gray-900">
                Seller
              </Link>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-gray-600 hover:text-gray-900">
                Login
              </Link>
              <Link
                href="/register"
                className="bg-orange-600 text-white px-3 py-1.5 rounded hover:bg-orange-700"
              >
                Register
              </Link>
            </>
          )}

          <Link
            href="/cart"
            className="relative flex items-center gap-1 text-gray-700 hover:text-gray-900"
          >
            🛒
            {cartCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-orange-600 text-white text-xs w-4 h-4 rounded-full flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </Link>
        </div>
      </div>
    </nav>
  );
}
