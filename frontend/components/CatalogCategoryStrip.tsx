"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { Category } from "@/lib/types";

const CATEGORY_ICONS: Record<string, string> = {
  games: "🎮",
  software: "💻",
  "mobile-software": "📱",
  boost: "🚀",
  "social-media": "📣",
  accounts: "🔐",
};

function getCategoryIcon(category: Category) {
  return CATEGORY_ICONS[category.slug] ?? "🛍️";
}

export default function CatalogCategoryStrip({
  activeCategorySlug,
}: {
  activeCategorySlug?: string | null;
}) {
  const [categories, setCategories] = useState<Category[]>([]);

  useEffect(() => {
    apiFetch<Category[]>("/api/catalog/categories/top")
      .then((categoryData) => setCategories(categoryData))
      .catch(() => setCategories([]));
  }, []);

  if (categories.length === 0) {
    return null;
  }

  return (
    <section className="overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
      <div className="flex min-w-max gap-3">
        {categories.map((category) => {
          const isActive = activeCategorySlug === category.slug;

          return (
            <Link
              key={category.id}
              href={`/categories/${category.slug}`}
              aria-current={isActive ? "page" : undefined}
              className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "border-orange-300 bg-orange-100 text-orange-700 shadow-sm"
                  : "border-gray-200 bg-white text-gray-700 hover:border-orange-200 hover:bg-orange-50"
              }`}
            >
              <span aria-hidden="true" className="text-base">
                {getCategoryIcon(category)}
              </span>
              <span className="whitespace-nowrap">{category.name}</span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
