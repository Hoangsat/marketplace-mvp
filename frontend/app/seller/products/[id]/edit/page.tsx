"use client";

// app/seller/products/[id]/edit/page.tsx - Edit an existing product

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Category, Product } from "@/lib/types";

export default function EditProductPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { messages } = useLanguage();
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
    if (!getToken()) {
      router.push("/login");
      return;
    }

    Promise.all([
      apiFetch<Product>(`/products/${id}`),
      apiFetch<Category[]>("/categories"),
    ])
      .then(([product, categoriesData]) => {
        setForm({
          title: product.title,
          description: product.description,
          price: String(product.price),
          stock: String(product.stock),
          category_id: String(product.category_id),
        });
        setCategories(categoriesData);
      })
      .catch((error: Error) => showToast(error.message, "error"))
      .finally(() => setLoading(false));
  }, [id, router]);

  function set(field: string, value: string) {
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
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

      if (newImages && newImages.length > 0) {
        const fd = new FormData();
        Array.from(newImages).forEach((file) => fd.append("images", file));
        await apiFetch(`/products/${id}/images`, { method: "POST", body: fd });
      }

      showToast(messages.productUpdated, "success");
      router.push("/seller/dashboard");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : messages.updateFailed, "error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-gray-500">{messages.loading}</p>;
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.editProductTitle}</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label={messages.titleLabel}>
          <input
            required
            value={form.title}
            onChange={(event) => set("title", event.target.value)}
            className={input}
          />
        </Field>
        <Field label={messages.descriptionLabel}>
          <textarea
            required
            value={form.description}
            onChange={(event) => set("description", event.target.value)}
            rows={3}
            className={`${input} resize-none`}
          />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label={messages.priceLabel}>
            <input
              required
              type="number"
              min="0.01"
              step="0.01"
              value={form.price}
              onChange={(event) => set("price", event.target.value)}
              className={input}
            />
          </Field>
          <Field label={messages.stockFieldLabel}>
            <input
              required
              type="number"
              min="0"
              value={form.stock}
              onChange={(event) => set("stock", event.target.value)}
              className={input}
            />
          </Field>
        </div>
        <Field label={messages.categoryLabel}>
          <select
            required
            value={form.category_id}
            onChange={(event) => set("category_id", event.target.value)}
            className={input}
          >
            <option value="">{messages.selectCategory}</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label={messages.replaceImagesLabel}>
          <input
            type="file"
            accept="image/jpeg,image/png"
            multiple
            onChange={(event) => setNewImages(event.target.files)}
            className="text-sm text-gray-600"
          />
          <p className="text-xs text-gray-400 mt-1">{messages.replaceImagesHelp}</p>
        </Field>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 bg-orange-600 text-white py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50"
          >
            {saving ? messages.saving : messages.saveChanges}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
          >
            {messages.cancel}
          </button>
        </div>
      </form>
    </div>
  );
}

const input =
  "w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400";

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      {children}
    </div>
  );
}
