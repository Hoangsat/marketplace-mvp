"use client";

// app/checkout/page.tsx - Mock checkout, calls POST /orders/checkout

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { CartItem, cartTotal, clearCart, getCart } from "@/lib/cart";
import { Order } from "@/lib/types";

export default function CheckoutPage() {
  const router = useRouter();
  const { messages } = useLanguage();
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setCart(getCart());
  }, []);

  async function handleCheckout() {
    if (!getToken()) {
      showToast(messages.pleaseLoginToCheckout, "error");
      router.push("/login");
      return;
    }

    if (cart.length === 0) {
      showToast(messages.cartIsEmpty, "error");
      return;
    }

    setLoading(true);
    try {
      const order = await apiFetch<Order>("/orders/checkout", {
        method: "POST",
        body: JSON.stringify({
          items: cart.map((item) => ({
            product_id: item.product_id,
            quantity: item.quantity,
          })),
        }),
      });

      clearCart();
      window.dispatchEvent(new Event("cartUpdated"));
      showToast(messages.orderPlacedContinuePayment, "success");
      router.push(`/orders/${order.id}/payment`);
    } catch (err: unknown) {
      showToast(
        err instanceof Error ? err.message : messages.checkoutFailed,
        "error"
      );
    } finally {
      setLoading(false);
    }
  }

  if (cart.length === 0) {
    return (
      <div className="text-center mt-16">
        <p className="text-gray-500 mb-4">{messages.nothingToCheckout}</p>
        <Link href="/" className="text-orange-600 hover:underline">
          {messages.browseProductsLink}
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.checkout}</h1>

      <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100 mb-6">
        {cart.map((item) => (
          <div
            key={item.product_id}
            className="flex justify-between px-4 py-3 text-sm"
          >
            <span className="text-gray-700">
              {item.title} <span className="text-gray-400">x {item.quantity}</span>
            </span>
            <span className="font-medium">
              ${(item.price * item.quantity).toFixed(2)}
            </span>
          </div>
        ))}
        <div className="flex justify-between px-4 py-3 font-semibold">
          <span>{messages.total}</span>
          <span className="text-orange-600">${cartTotal(cart).toFixed(2)}</span>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800 mb-6">
        {messages.manualBankTransferRedirect}
      </div>

      <button
        onClick={handleCheckout}
        disabled={loading}
        className="w-full bg-orange-600 text-white py-3 rounded font-semibold hover:bg-orange-700 disabled:opacity-50"
      >
        {loading ? messages.processing : messages.continueToPayment}
      </button>
    </div>
  );
}
