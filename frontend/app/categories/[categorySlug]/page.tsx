"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import CatalogCategoryStrip from "@/components/CatalogCategoryStrip";
import CatalogBreadcrumbs from "@/components/CatalogBreadcrumbs";
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
    <div className="space-y-4">
      <CatalogCategoryStrip activeCategorySlug={categorySlug} />

      <section className="space-y-2">
        <CatalogBreadcrumbs
          items={[
            { label: messages.home, href: "/" },
            { label: messages.catalog, href: "/catalog" },
            { label: category?.name ?? categorySlug },
          ]}
          className="text-gray-400"
        />

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">
            {category?.name ?? categorySlug}
          </h1>
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
          <section className="space-y-3">
            {platforms.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {platforms.map((platform) => (
                  <Link
                    key={platform.id}
                    href={`/catalog/${platform.slug}`}
                    className="inline-flex items-center rounded-full border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-all duration-200 hover:border-orange-300 hover:bg-orange-50 hover:text-orange-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-400/70"
                  >
                    {platform.name}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                {messages.noPlatformsAvailableYet}
              </p>
            )}
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-900">
              {messages.productsLabel}
            </h2>
            {products.length === 0 ? (
              <p className="text-sm text-gray-500">{messages.noProductsFoundYet}</p>
            ) : (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
