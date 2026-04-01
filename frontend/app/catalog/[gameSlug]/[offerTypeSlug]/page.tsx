"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { apiFetch } from "@/lib/api";
import CatalogCategoryStrip from "@/components/CatalogCategoryStrip";
import CatalogBreadcrumbs from "@/components/CatalogBreadcrumbs";
import { useLanguage } from "@/components/LanguageProvider";
import ProductCard from "@/components/ProductCard";
import { Category, OfferType, Platform, Product } from "@/lib/types";
import { Language } from "@/lib/i18n";

function getPlatformName(platform: Platform, language: Language) {
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

export default function CatalogOfferTypePage() {
  const { gameSlug, offerTypeSlug } = useParams<{
    gameSlug: string;
    offerTypeSlug: string;
  }>();
  const { language, messages } = useLanguage();
  const [category, setCategory] = useState<Category | null>(null);
  const [platform, setPlatform] = useState<Platform | null>(null);
  const [offerType, setOfferType] = useState<OfferType | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([
      apiFetch<Platform>(`/platforms/${encodeURIComponent(gameSlug)}`),
      apiFetch<OfferType[]>(
        `/offer-types?platform=${encodeURIComponent(gameSlug)}`
      ),
      apiFetch<Category[]>("/categories"),
    ])
      .then(async ([platformData, offerTypes, categories]) => {
        const selectedOfferType =
          offerTypes.find((item) => item.slug === offerTypeSlug) ?? null;

        setCategory(
          categories.find((item) => item.id === platformData.category_id) ?? null
        );

        if (!selectedOfferType) {
          setPlatform(platformData);
          setOfferType(null);
          setProducts([]);
          setError(false);
          return;
        }

        const params = new URLSearchParams({
          platform: platformData.slug,
          offer_type: selectedOfferType.slug,
        });
        const productData = await apiFetch<Product[]>(
          `/products?${params.toString()}`
        );

        setPlatform(platformData);
        setOfferType(selectedOfferType);
        setProducts(productData);
        setError(false);
      })
      .catch(() => {
        setCategory(null);
        setPlatform(null);
        setOfferType(null);
        setProducts([]);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, [gameSlug, offerTypeSlug]);

  const missingMessage = !platform
    ? messages.gameNotFound
    : !offerType
      ? messages.offerTypeNotFound
      : null;

  return (
    <div className="space-y-5">
      <CatalogCategoryStrip activeCategorySlug={category?.slug ?? null} />

      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <Link
          href={platform ? `/catalog/${platform.slug}` : "/catalog"}
          className="text-sm font-medium text-orange-600 hover:underline"
        >
          {messages.backToOfferTypes}
        </Link>
        <div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <CatalogBreadcrumbs
              items={[
                { label: messages.catalog, href: "/catalog" },
                ...(category
                  ? [{ label: category.name, href: `/categories/${category.slug}` }]
                  : []),
                ...(platform
                  ? [{ label: getPlatformName(platform, language), href: `/catalog/${platform.slug}` }]
                  : []),
                {
                  label: offerType
                    ? getOfferTypeName(offerType, language)
                    : offerTypeSlug,
                },
              ]}
              className="text-gray-500"
            />
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">
              {platform && offerType
                ? `${getPlatformName(platform, language)} / ${getOfferTypeName(
                    offerType,
                    language
                  )}`
                : messages.catalog}
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-gray-600">
              {messages.browseProductsForSelection}
            </p>
          </div>
          {platform && offerType && (
            <Link
              href={`/seller/products/new?platform=${platform.slug}&offerType=${offerType.slug}`}
              className="inline-flex items-center justify-center rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-orange-700"
            >
              {messages.sellInThisCategory}
            </Link>
          )}
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">{messages.loadingProducts}</p>
      ) : error ? (
        <p className="text-red-600 text-sm">{messages.loadProductsError}</p>
      ) : missingMessage ? (
        <p className="text-gray-500 text-sm">{missingMessage}</p>
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
