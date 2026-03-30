"use client";

// app/cart/page.tsx — Cart view with quantity edit and remove

import { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/components/LanguageProvider";
import {
  CartItem,
  cartTotal,
  getCart,
  hasMultipleCartSellers,
  removeFromCart,
  updateQuantity,
} from "@/lib/cart";

export default function CartPage() {
  const { messages } = useLanguage();
  const [cart, setCart] = useState<CartItem[]>(() => {
    if (typeof window === "undefined") {
      return [];
    }
    return getCart();
  });
  const hasMultipleSellers = hasMultipleCartSellers(cart);

  function refresh() {
    const updated = getCart();
    setCart(updated);
    window.dispatchEvent(new Event("cartUpdated"));
  }

  function handleQtyChange(product_id: number, value: number) {
    if (value < 1) return;
    updateQuantity(product_id, value);
    refresh();
  }

  function handleRemove(product_id: number) {
    removeFromCart(product_id);
    refresh();
  }

  if (cart.length === 0) {
    return (
      <div className="text-center mt-16">
        <p className="text-gray-500 text-lg mb-4">{messages.cartEmpty}</p>
        <Link href="/" className="text-orange-600 hover:underline">
          {messages.browseProductsLink}
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.cartTitle}</h1>
      {hasMultipleSellers && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {messages.singleSellerCheckoutMessage}
        </div>
      )}
      <div className="space-y-4">
        {cart.map((item) => (
          <div key={item.product_id} className="flex items-center gap-4 bg-white border border-gray-200 rounded-lg p-4">
            <div className="w-16 h-16 bg-gray-100 rounded flex items-center justify-center text-2xl shrink-0">
              📦
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">{item.title}</p>
              <p className="text-orange-600 text-sm">
                ${item.price.toFixed(2)} {messages.each}
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <input
                type="number"
                min={1}
                value={item.quantity}
                onChange={(e) => handleQtyChange(item.product_id, Number(e.target.value))}
                className="w-14 border border-gray-300 rounded px-2 py-1 text-sm text-center"
              />
              <button
                onClick={() => handleRemove(item.product_id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                {messages.remove}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 bg-white border border-gray-200 rounded-lg p-4 flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{messages.total}</p>
          <p className="text-xl font-bold text-orange-600">${cartTotal(cart).toFixed(2)}</p>
        </div>
        <Link
          href="/checkout"
          onClick={(event) => {
            if (hasMultipleSellers) {
              event.preventDefault();
            }
          }}
          aria-disabled={hasMultipleSellers}
          className={`px-6 py-2 rounded font-medium text-white ${
            hasMultipleSellers
              ? "cursor-not-allowed bg-gray-400"
              : "bg-orange-600 hover:bg-orange-700"
          }`}
        >
          {messages.checkout}
        </Link>
      </div>
    </div>
  );
}
