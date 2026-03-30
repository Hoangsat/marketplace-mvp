"use client";

// app/seller/products/new/page.tsx - Create a new product

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Category } from "@/lib/types";

export default function NewProductPage() {
  const router = useRouter();
  const { messages } = useLanguage();
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
    if (!getToken()) {
      router.push("/login");
      return;
    }
    apiFetch<Category[]>("/categories").then(setCategories).catch(() => {});
  }, [router]);

  function set(field: string, value: string) {
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("title", form.title);
      fd.append("description", form.description);
      fd.append("price", form.price);
      fd.append("stock", form.stock);
      fd.append("category_id", form.category_id);
      if (images) {
        Array.from(images).forEach((file) => fd.append("images", file));
      }

      await apiFetch("/products", { method: "POST", body: fd });
      showToast(messages.productCreated, "success");
      router.push("/seller/dashboard");
    } catch (err: unknown) {
      showToast(
        err instanceof Error ? err.message : messages.createProductFailed,
        "error"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.createProductTitle}</h1>
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
        <Field label={messages.imagesLabel}>
          <input
            type="file"
            accept="image/jpeg,image/png"
            multiple
            onChange={(event) => setImages(event.target.files)}
            className="text-sm text-gray-600"
          />
        </Field>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-orange-600 text-white py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50"
        >
          {loading ? messages.creating : messages.createProductTitle}
        </button>
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
