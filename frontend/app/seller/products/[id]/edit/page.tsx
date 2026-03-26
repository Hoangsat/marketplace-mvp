"use client";

// app/seller/products/[id]/edit/page.tsx — Edit an existing product

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Category, Product } from "@/lib/types";
import { showToast } from "@/components/Toast";

export default function EditProductPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newImages, setNewImages] = useState<FileList | null>(null);

  const [form, setForm] = useState({
    title: "",
    description: "",
    price: "",
    stock: "",
    category_id: "",
  });

  useEffect(() => {
    if (!getToken()) { router.push("/login"); return; }
    Promise.all([
      apiFetch<Product>(`/products/${id}`),
      apiFetch<Category[]>("/categories"),
    ]).then(([product, cats]) => {
      setForm({
        title: product.title,
        description: product.description,
        price: String(product.price),
        stock: String(product.stock),
        category_id: String(product.category_id),
      });
      setCategories(cats);
    }).catch((e) => showToast(e.message, "error"))
      .finally(() => setLoading(false));
  }, [id, router]);

  function set(field: string, value: string) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await apiFetch(`/products/${id}`, {
        method: "PUT",
        body: JSON.stringify({
          title: form.title,
          description: form.description,
          price: parseFloat(form.price),
          stock: parseInt(form.stock),
          category_id: parseInt(form.category_id),
        }),
      });

      // Upload new images if provided
      if (newImages && newImages.length > 0) {
        const fd = new FormData();
        Array.from(newImages).forEach((f) => fd.append("images", f));
        await apiFetch(`/products/${id}/images`, { method: "POST", body: fd });
      }

      showToast("Product updated!", "success");
      router.push("/seller/dashboard");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Update failed", "error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-gray-500">Loading...</p>;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">Edit Product</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Title">
          <input required value={form.title} onChange={(e) => set("title", e.target.value)} className={input} />
        </Field>
        <Field label="Description">
          <textarea required value={form.description} onChange={(e) => set("description", e.target.value)}
            rows={3} className={`${input} resize-none`} />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Price ($)">
            <input required type="number" min="0.01" step="0.01" value={form.price}
              onChange={(e) => set("price", e.target.value)} className={input} />
          </Field>
          <Field label="Stock">
            <input required type="number" min="0" value={form.stock}
              onChange={(e) => set("stock", e.target.value)} className={input} />
          </Field>
        </div>
        <Field label="Category">
          <select required value={form.category_id} onChange={(e) => set("category_id", e.target.value)} className={input}>
            <option value="">Select category</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </Field>
        <Field label="Replace Images (optional)">
          <input type="file" accept="image/jpeg,image/png" multiple
            onChange={(e) => setNewImages(e.target.files)}
            className="text-sm text-gray-600" />
          <p className="text-xs text-gray-400 mt-1">Uploading new images will replace all existing ones.</p>
        </Field>

        <div className="flex gap-3">
          <button type="submit" disabled={saving}
            className="flex-1 bg-orange-600 text-white py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50">
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <button type="button" onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

const input = "w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      {children}
    </div>
  );
}
