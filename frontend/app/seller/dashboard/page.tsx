"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Product, SellerDashboardData } from "@/lib/types";
import { showToast } from "@/components/Toast";

export default function SellerDashboardPage() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<SellerDashboardData | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }

    Promise.all([
      apiFetch<SellerDashboardData>("/seller/dashboard"),
      apiFetch<Product[]>("/seller/products"),
    ])
      .then(([dashboardData, productData]) => {
        setDashboard(dashboardData);
        setProducts(productData);
      })
      .catch((e: unknown) =>
        showToast(e instanceof Error ? e.message : "Unable to load seller dashboard", "error")
      )
      .finally(() => setLoading(false));
  }, [router]);

  async function handleDelete(id: number) {
    if (!confirm("Delete this product?")) return;
    try {
      await apiFetch(`/products/${id}`, { method: "DELETE" });
      showToast("Product deleted", "success");
      setProducts((p) => p.filter((x) => x.id !== id));
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Delete failed", "error");
    }
  }

  async function handleMarkDelivered(orderId: number) {
    try {
      await apiFetch(`/orders/${orderId}/mark-delivered`, { method: "POST" });
      showToast("Order marked as delivered", "success");
      const updatedDashboard = await apiFetch<SellerDashboardData>("/seller/dashboard");
      setDashboard(updatedDashboard);
    } catch (e: unknown) {
      showToast(
        e instanceof Error ? e.message : "Unable to update order status",
        "error"
      );
    }
  }

  if (loading) return <p className="text-gray-500">Loading...</p>;
  if (!dashboard) return <p className="text-gray-500">Unable to load seller dashboard.</p>;

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-bold mb-6">Seller Dashboard</h1>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <p className="text-sm text-gray-500 mb-2">Pending Balance (On Hold)</p>
            <p className="text-2xl font-semibold text-orange-600">
              ${Number(dashboard.balance_pending).toFixed(2)}
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <p className="text-sm text-gray-500 mb-2">Available Balance</p>
            <p className="text-2xl font-semibold text-green-600">
              ${Number(dashboard.balance_available).toFixed(2)}
            </p>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-6">My Orders</h2>
        {dashboard.orders.length === 0 ? (
          <p className="text-gray-500">No orders yet for your products.</p>
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
            {dashboard.orders.map((order) => (
              <div
                key={order.id}
                className="px-4 py-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="font-medium text-sm">Order #{order.id}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(order.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex flex-col gap-2 text-sm sm:items-end">
                  <p className="font-semibold text-orange-600">
                    ${Number(order.total).toFixed(2)}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <span className="inline-block text-xs px-2 py-0.5 rounded-full font-medium bg-blue-100 text-blue-700">
                      Order Status: {formatLabel(order.status)}
                    </span>
                    <span
                      className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium ${getMoneyStatusClasses(
                        order.money_status
                      )}`}
                    >
                      Money Status: {formatMoneyStatus(order.money_status)}
                    </span>
                  </div>
                  {order.status === "paid" && (
                    <button
                      onClick={() => handleMarkDelivered(order.id)}
                      className="mt-1 text-xs bg-orange-600 text-white px-3 py-1 rounded hover:bg-orange-700 transition"
                    >
                      Mark as Delivered
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">My Products</h2>
          <Link
            href="/seller/products/new"
            className="bg-orange-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-orange-700"
          >
            + New Product
          </Link>
        </div>

        {products.length === 0 ? (
          <p className="text-gray-500">You haven&apos;t listed any products yet.</p>
        ) : (
          <div className="space-y-3">
            {products.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between bg-white border border-gray-200 rounded-lg px-4 py-3"
              >
                <div className="min-w-0">
                  <p className="font-medium text-sm truncate">{p.title}</p>
                  <p className="text-xs text-gray-400">
                    ${p.price.toFixed(2)} · {p.stock} in stock
                  </p>
                </div>
                <div className="flex gap-3 text-sm shrink-0 ml-4">
                  <Link
                    href={`/seller/products/${p.id}/edit`}
                    className="text-blue-600 hover:underline"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={() => handleDelete(p.id)}
                    className="text-red-500 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8">
          <Link
            href="/seller/orders"
            className="text-sm text-orange-600 hover:underline"
          >
            View order items for my products →
          </Link>
        </div>
      </section>
    </div>
  );
}

function formatLabel(value: string) {
  return value.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatMoneyStatus(status: string) {
  if (status === "on_hold") return "On Hold";
  if (status === "available") return "Available";
  if (status === "cancelled") return "Cancelled";
  return "Pending Payment";
}

function getMoneyStatusClasses(status: string) {
  if (status === "available") return "bg-green-100 text-green-700";
  if (status === "on_hold") return "bg-yellow-100 text-yellow-700";
  if (status === "cancelled") return "bg-gray-100 text-gray-700";
  return "bg-slate-100 text-slate-700";
}
