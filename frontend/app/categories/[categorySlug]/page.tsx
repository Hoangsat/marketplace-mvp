"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import ProductCard from "@/components/ProductCard";
import { useLanguage } from "@/components/LanguageProvider";
import { apiFetch } from "@/lib/api";
import { CategoryDetail, Platform, Product } from "@/lib/types";

export default function CategoryPage() {
  const { categorySlug } = useParams<{ categorySlug: string }>();
  const { messages } = useLanguage();
  const [category, setCategory] = useState<CategoryDetail | null>(null);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    Promise.all([
      apiFetch<CategoryDetail>(
        `/api/catalog/categories/${encodeURIComponent(categorySlug)}`
      ),
      apiFetch<Platform[]>(
        `/api/catalog/categories/${encodeURIComponent(categorySlug)}/platforms`
      ),
      apiFetch<Product[]>(
        `/api/catalog/categories/${encodeURIComponent(categorySlug)}/products`
      ),
    ])
      .then(([categoryData, platformData, productData]) => {
        if (isCancelled) {
          return;
        }

        setCategory(categoryData);
        setPlatforms(platformData);
        setProducts(productData);
        setNotFound(false);
        setError(false);
      })
      .catch((err: unknown) => {
        if (isCancelled) {
          return;
        }

        if (err instanceof Error && err.message === "Category not found") {
          setNotFound(true);
          setError(false);
          setCategory(null);
          setPlatforms([]);
          setProducts([]);
          return;
        }

        setNotFound(false);
        setError(true);
        setCategory(null);
        setPlatforms([]);
        setProducts([]);
      })
      .finally(() => {
        if (!isCancelled) {
          setLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [categorySlug]);

  const isTerminalCategory = !platforms || platforms.length === 0;

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-slate-800 bg-slate-950 p-6 text-slate-100 shadow-xl">
        <Link
          href="/catalog"
          className="text-sm font-medium text-orange-300 hover:underline"
        >
          {messages.backToCatalog}
        </Link>

        <div className="mt-4 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-slate-400">
              {messages.categoryLabel}
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight">
              {category?.name ?? categorySlug}
            </h1>
          </div>
          {!loading && !notFound && !error && category && isTerminalCategory && (
            <Link
              href={`/seller/products/new?category=${category.slug}`}
              className="inline-flex items-center justify-center rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-orange-700"
            >
              {messages.sellInThisCategory}
            </Link>
          )}
        </div>
      </section>

      {loading ? (
        <p className="text-sm text-gray-500">{messages.loadingProducts}</p>
      ) : notFound ? (
        <p className="text-sm text-gray-500">Category not found.</p>
      ) : error ? (
        <p className="text-sm text-red-600">{messages.loadCatalogError}</p>
      ) : (
        <>
          <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">
              {messages.browseProducts}
            </h2>
            {platforms.length > 0 ? (
              <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {platforms.map((platform) => (
                  <Link
                    key={platform.id}
                    href={`/catalog/${platform.slug}`}
                    className="rounded-2xl border border-gray-200 bg-gray-50 p-4 text-sm font-medium text-gray-700 transition-colors hover:border-orange-300 hover:text-orange-700"
                  >
                    <p className="text-base font-semibold">{platform.name}</p>
                    <p className="mt-1 text-xs text-gray-500">{platform.slug}</p>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-gray-500">{messages.noOfferTypes}</p>
            )}
          </section>

          {products.length === 0 ? (
            <p className="text-sm text-gray-500">{messages.noProducts}</p>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
