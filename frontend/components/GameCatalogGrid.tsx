"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import { Category } from "@/lib/types";

export default function GameCatalogGrid() {
  const { messages } = useLanguage();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiFetch<Category[]>("/api/catalog/categories/top")
      .then((categoryData) => {
        setCategories(categoryData);
        setError(false);
      })
      .catch(() => {
        setCategories([]);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-orange-100 bg-gradient-to-br from-white to-orange-50 p-6 shadow-sm">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          {messages.catalog}
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-gray-600">
          {messages.chooseGame}
        </p>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            {messages.categoryLabel}
          </h2>
        </div>
        {loading ? (
          <p className="text-sm text-gray-500">{messages.loadingGames}</p>
        ) : error ? (
          <p className="text-sm text-red-600">{messages.loadCatalogError}</p>
        ) : categories.length === 0 ? (
          <p className="text-sm text-gray-500">{messages.noGames}</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {categories.map((category) => (
              <Link
                key={category.id}
                href={`/categories/${category.slug}`}
                className="group block rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-md"
              >
                <p className="text-lg font-semibold text-gray-900 transition-colors group-hover:text-orange-700">
                  {category.name}
                </p>
                <p className="mt-2 text-sm text-gray-500">
                  {category.slug.replace(/-/g, " ")}
                </p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
