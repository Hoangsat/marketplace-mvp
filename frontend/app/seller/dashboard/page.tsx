"use client";

// app/seller/dashboard/page.tsx — Seller product list

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Product } from "@/lib/types";
import { showToast } from "@/components/Toast";

export default function SellerDashboardPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProducts = () => {
    if (!getToken()) { router.push("/login"); return; }
    apiFetch<Product[]>("/seller/products")
      .then(setProducts)
      .catch((e) => showToast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(loadProducts, [router]);

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

  if (loading) return <p className="text-gray-500">Loading...</p>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Products</h1>
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
    </div>
  );
}
