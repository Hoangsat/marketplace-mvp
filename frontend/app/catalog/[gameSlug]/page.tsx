"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { apiFetch } from "@/lib/api";
import CatalogBreadcrumbs from "@/components/CatalogBreadcrumbs";
import { useLanguage } from "@/components/LanguageProvider";
import ProductCard from "@/components/ProductCard";
import { Category, OfferType, PlatformDetail, Product } from "@/lib/types";
import { Language } from "@/lib/i18n";

function getPlatformName(platform: PlatformDetail, language: Language) {
  if (language === "vi") {
    return platform.display_name_vi || platform.name;
  }
  return platform.name;
}

function getOfferTypeName(offerType: OfferType, language: Language) {
  if (language === "vi") {
    return offerType.display_name_vi || offerType.name;
  }
  return offerType.name;
}

export default function CatalogPlatformPage() {
  const { gameSlug } = useParams<{ gameSlug: string }>();
  const { language, messages } = useLanguage();
  const [category, setCategory] = useState<Category | null>(null);
  const [platform, setPlatform] = useState<PlatformDetail | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([
      apiFetch<PlatformDetail>(`/platforms/${encodeURIComponent(gameSlug)}`),
      apiFetch<Category[]>("/categories"),
    ])
      .then(async ([platformData, categories]) => {
        if (!platformData.has_offer_types) {
          const productData = await apiFetch<Product[]>(
            `/products?platform=${encodeURIComponent(platformData.slug)}`
          );
          setProducts(productData);
        } else {
          setProducts([]);
        }
        setCategory(
          categories.find((item) => item.id === platformData.category_id) ?? null
        );
        setPlatform(platformData);
        setError(false);
      })
      .catch(() => {
        setCategory(null);
        setPlatform(null);
        setProducts([]);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, [gameSlug]);

  const offerTypes = platform?.offer_types ?? [];

  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <Link
          href="/catalog"
          className="text-sm font-medium text-orange-600 hover:underline"
        >
          {messages.backToCatalog}
        </Link>
        <div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <CatalogBreadcrumbs
              items={[
                { label: messages.catalog, href: "/catalog" },
                ...(category
                  ? [{ label: category.name, href: `/categories/${category.slug}` }]
                  : []),
                {
                  label: platform ? getPlatformName(platform, language) : gameSlug,
                },
              ]}
              className="text-gray-500"
            />
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">
              {platform ? getPlatformName(platform, language) : messages.catalog}
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-gray-600">
              {platform?.has_offer_types
                ? messages.chooseOfferType
                : messages.browseProductsForSelection}
            </p>
          </div>
          {platform && !platform.has_offer_types && (
            <Link
              href={`/seller/products/new?platform=${platform.slug}`}
              className="inline-flex items-center justify-center rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-orange-700"
            >
              {messages.sellInThisCategory}
            </Link>
          )}
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">
          {platform?.has_offer_types
            ? messages.loadingOfferTypes
            : messages.loadingProducts}
        </p>
      ) : error && !platform ? (
        <p className="text-red-600 text-sm">{messages.loadCatalogError}</p>
      ) : !platform ? (
        <p className="text-gray-500 text-sm">{messages.gameNotFound}</p>
      ) : platform.has_offer_types ? (
        offerTypes.length === 0 ? (
          <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">
              {messages.offerTypesLabel}
            </h2>
            <p className="mt-3 text-gray-500 text-sm">
              {messages.noOfferTypesAvailableYet}
            </p>
          </section>
        ) : (
          <section className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-900">
              {messages.offerTypesLabel}
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {offerTypes.map((offerType) => (
              <Link
                key={offerType.id}
                href={`/catalog/${platform.slug}/${offerType.slug}`}
                className="group block cursor-pointer rounded-2xl border border-gray-200 bg-gray-50 p-4 text-sm font-medium text-gray-700 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-orange-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-400/70"
              >
                <p className="text-base font-semibold text-gray-900 transition-colors group-hover:text-orange-700">
                  {getOfferTypeName(offerType, language)}
                </p>
              </Link>
            ))}
            </div>
          </section>
        )
      ) : products.length === 0 ? (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-900">
            {messages.productsLabel}
          </h2>
          <p className="text-gray-500 text-sm">{messages.noProductsFoundYet}</p>
        </section>
      ) : (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-900">
            {messages.productsLabel}
          </h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
