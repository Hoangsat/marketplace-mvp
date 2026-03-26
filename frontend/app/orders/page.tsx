"use client";

// app/orders/page.tsx — Buyer order history

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Order } from "@/lib/types";

export default function OrdersPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) { router.push("/login"); return; }
    apiFetch<Order[]>("/orders/buyer")
      .then(setOrders)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <p className="text-gray-500">Loading orders...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">My Orders</h1>
      {orders.length === 0 ? (
        <p className="text-gray-500">You haven&apos;t placed any orders yet.</p>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <div key={order.id} className="bg-white border border-gray-200 rounded-lg p-5">
              <div className="flex justify-between items-center mb-3">
                <div>
                  <p className="font-semibold">Order #{order.id}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(order.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  <span className="inline-block bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full font-medium">
                    {order.status}
                  </span>
                  <p className="text-orange-600 font-semibold mt-1">${order.total.toFixed(2)}</p>
                </div>
              </div>
              <div className="divide-y divide-gray-100">
                {order.items.map((item) => (
                  <div key={item.id} className="py-2 flex justify-between text-sm">
                    <span className="text-gray-700">{item.product?.title ?? `Product #${item.product_id}`} × {item.quantity}</span>
                    <span className="text-gray-500">${(item.price_at_purchase * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
