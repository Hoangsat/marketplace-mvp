"use client";

// app/orders/page.tsx — Buyer order history

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { showToast } from "@/components/Toast";
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

  async function handleMarkCompleted(orderId: number) {
    try {
      const updatedOrder = await apiFetch<Order>(`/orders/${orderId}/mark-completed`, {
        method: "POST",
      });
      setOrders((currentOrders) =>
        currentOrders.map((order) => (order.id === orderId ? updatedOrder : order))
      );
    } catch (err: unknown) {
      showToast(
        err instanceof Error ? err.message : "Unable to update order",
        "error"
      );
    }
  }

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
                <div className="text-right flex flex-col items-end">
                  <span
                    className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium ${
                      order.status === "paid" || order.status === "delivered"
                        ? "bg-green-100 text-green-700"
                        : order.status === "pending"
                        ? "bg-yellow-100 text-yellow-700"
                        : order.status === "cancelled"
                        ? "bg-gray-100 text-gray-700"
                        : "bg-blue-100 text-blue-700"
                    }`}
                  >
                    {formatOrderStatus(order.status)}
                  </span>
                  {order.status === "pending" && !order.buyer_marked_paid_at && (
                    <button
                      onClick={() => router.push(`/orders/${order.id}/payment`)}
                      className="mt-2 text-xs bg-orange-600 text-white px-3 py-1 rounded hover:bg-orange-700 transition"
                    >
                      Complete Payment
                    </button>
                  )}
                  {order.status === "pending" && order.buyer_marked_paid_at && (
                    <p className="mt-2 text-xs text-orange-600 font-medium">Payment evaluating...</p>
                  )}
                  {order.status === "delivered" && (
                    <button
                      onClick={() => handleMarkCompleted(order.id)}
                      className="mt-2 text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition"
                    >
                      Mark as Completed
                    </button>
                  )}
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

function formatOrderStatus(status: string) {
  return status.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
