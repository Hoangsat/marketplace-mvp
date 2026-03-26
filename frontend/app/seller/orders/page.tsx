"use client";

// app/seller/orders/page.tsx — Order items for seller's own products

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { OrderItem } from "@/lib/types";

export default function SellerOrdersPage() {
  const router = useRouter();
  const [items, setItems] = useState<OrderItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) { router.push("/login"); return; }
    apiFetch<OrderItem[]>("/orders/seller")
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <p className="text-gray-500">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Sales (Order Items)</h1>
      {items.length === 0 ? (
        <p className="text-gray-500">No orders yet for your products.</p>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
          {items.map((item) => (
            <div key={item.id} className="px-4 py-3 flex justify-between items-center text-sm">
              <div>
                <p className="font-medium">{item.product?.title ?? `Product #${item.product_id}`}</p>
                <p className="text-gray-400 text-xs">Order #{item.order_id} · qty {item.quantity}</p>
              </div>
              <p className="font-semibold text-orange-600">
                ${(item.price_at_purchase * item.quantity).toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
