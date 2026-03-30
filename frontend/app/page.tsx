"use client";

// app/page.tsx — Product catalog: search, category filter, price filter

import { useEffect, useState, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import { Category, Product } from "@/lib/types";
import ProductCard from "@/components/ProductCard";

export default function HomePage() {
  const { messages } = useLanguage();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState<string>("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (categoryId) params.set("category_id", categoryId);
      if (minPrice) params.set("min_price", minPrice);
      if (maxPrice) params.set("max_price", maxPrice);

      const data = await apiFetch<Product[]>(`/products?${params.toString()}`);
      setProducts(data);
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [search, categoryId, minPrice, maxPrice]);

  useEffect(() => {
    apiFetch<Category[]>("/categories").then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    const delay = setTimeout(fetchProducts, 300);
    return () => clearTimeout(delay);
  }, [fetchProducts]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">{messages.browseProducts}</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <input
          type="text"
          placeholder={messages.searchProducts}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 text-sm flex-1 min-w-48 focus:outline-none focus:ring-2 focus:ring-orange-400"
        />
        <select
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
        >
          <option value="">{messages.allCategories}</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <input
          type="number"
          placeholder={messages.minPrice}
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 text-sm w-24 focus:outline-none focus:ring-2 focus:ring-orange-400"
        />
        <input
          type="number"
          placeholder={messages.maxPrice}
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 text-sm w-24 focus:outline-none focus:ring-2 focus:ring-orange-400"
        />
      </div>

      {/* Grid */}
      {loading ? (
        <p className="text-gray-500 text-sm">{messages.loadingProducts}</p>
      ) : products.length === 0 ? (
        <p className="text-gray-500 text-sm">{messages.noProducts}</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  );
}
