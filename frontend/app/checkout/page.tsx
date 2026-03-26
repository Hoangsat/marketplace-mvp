"use client";

// app/checkout/page.tsx — Mock checkout, calls POST /orders/checkout

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CartItem, getCart, cartTotal, clearCart } from "@/lib/cart";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { showToast } from "@/components/Toast";
import { Order } from "@/lib/types";
import Link from "next/link";

export default function CheckoutPage() {
  const router = useRouter();
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setCart(getCart());
  }, []);

  async function handleCheckout() {
    if (!getToken()) {
      showToast("Please log in to checkout", "error");
      router.push("/login");
      return;
    }
    if (cart.length === 0) {
      showToast("Cart is empty", "error");
      return;
    }

    setLoading(true);
    try {
      await apiFetch<Order>("/orders/checkout", {
        method: "POST",
        body: JSON.stringify({
          items: cart.map((c) => ({
            product_id: c.product_id,
            quantity: c.quantity,
          })),
        }),
      });
      clearCart();
      window.dispatchEvent(new Event("cartUpdated"));
      showToast("Order placed! 🎉", "success");
      router.push("/orders");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Checkout failed", "error");
    } finally {
      setLoading(false);
    }
  }

  if (cart.length === 0) {
    return (
      <div className="text-center mt-16">
        <p className="text-gray-500 mb-4">Nothing to checkout.</p>
        <Link href="/" className="text-orange-600 hover:underline">Browse products</Link>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">Checkout</h1>

      <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100 mb-6">
        {cart.map((item) => (
          <div key={item.product_id} className="flex justify-between px-4 py-3 text-sm">
            <span className="text-gray-700">
              {item.title} <span className="text-gray-400">× {item.quantity}</span>
            </span>
            <span className="font-medium">${(item.price * item.quantity).toFixed(2)}</span>
          </div>
        ))}
        <div className="flex justify-between px-4 py-3 font-semibold">
          <span>Total</span>
          <span className="text-orange-600">${cartTotal(cart).toFixed(2)}</span>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800 mb-6">
        🔒 This is a <strong>mock checkout</strong> — no real payment will be charged.
      </div>

      <button
        onClick={handleCheckout}
        disabled={loading}
        className="w-full bg-orange-600 text-white py-3 rounded font-semibold hover:bg-orange-700 disabled:opacity-50"
      >
        {loading ? "Placing order..." : "Place Order (Mock)"}
      </button>
    </div>
  );
}
