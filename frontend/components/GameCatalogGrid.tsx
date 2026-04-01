"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import CatalogCategoryStrip from "@/components/CatalogCategoryStrip";
import CatalogPopularStrip from "@/components/CatalogPopularStrip";
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
    <div className="space-y-6">
      <CatalogCategoryStrip />

      <CatalogPopularStrip />

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
                className="group block cursor-pointer rounded-2xl border border-gray-200 bg-gray-50 p-4 text-sm font-medium text-gray-700 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-orange-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-400/70"
              >
                <p className="text-base font-semibold text-gray-900 transition-colors group-hover:text-orange-700">
                  {category.name}
                </p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
