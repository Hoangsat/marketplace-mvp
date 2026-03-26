"use client";

// app/seller/products/new/page.tsx — Create a new product

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Category } from "@/lib/types";
import { showToast } from "@/components/Toast";

export default function NewProductPage() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    title: "",
    description: "",
    price: "",
    stock: "",
    category_id: "",
  });
  const [images, setImages] = useState<FileList | null>(null);

  useEffect(() => {
    if (!getToken()) { router.push("/login"); return; }
    apiFetch<Category[]>("/categories").then(setCategories).catch(() => {});
  }, [router]);

  function set(field: string, value: string) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("title", form.title);
      fd.append("description", form.description);
      fd.append("price", form.price);
      fd.append("stock", form.stock);
      fd.append("category_id", form.category_id);
      if (images) {
        Array.from(images).forEach((f) => fd.append("images", f));
      }

      await apiFetch("/products", { method: "POST", body: fd });
      showToast("Product created!", "success");
      router.push("/seller/dashboard");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Failed to create product", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">Create Product</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Title">
          <input required value={form.title} onChange={(e) => set("title", e.target.value)}
            className={input} />
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
          <select required value={form.category_id} onChange={(e) => set("category_id", e.target.value)}
            className={input}>
            <option value="">Select category</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </Field>
        <Field label="Images (up to 5, jpg/png, max 5MB each)">
          <input type="file" accept="image/jpeg,image/png" multiple
            onChange={(e) => setImages(e.target.files)}
            className="text-sm text-gray-600" />
        </Field>

        <button type="submit" disabled={loading}
          className="w-full bg-orange-600 text-white py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50">
          {loading ? "Creating..." : "Create Product"}
        </button>
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
