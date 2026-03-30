"use client";

// app/seller/products/new/page.tsx - Create a new product

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Category, Game, OfferType } from "@/lib/types";
import { Language } from "@/lib/i18n";

function getGameName(game: Game, language: Language) {
  if (language === "vi") {
    return game.display_name_vi || game.name;
  }
  return game.name;
}

function getOfferTypeName(offerType: OfferType, language: Language) {
  if (language === "vi") {
    return offerType.display_name_vi || offerType.name;
  }
  return offerType.name;
}

export default function NewProductPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { language, messages } = useLanguage();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [selectedOfferType, setSelectedOfferType] = useState<OfferType | null>(
    null
  );
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);

  const [form, setForm] = useState({
    title: "",
    description: "",
    price: "",
    stock: "",
    category_id: "",
  });
  const [images, setImages] = useState<FileList | null>(null);

  const gameSlug = searchParams.get("game");
  const offerTypeSlug = searchParams.get("offerType");
  const hasCatalogQuery = Boolean(gameSlug || offerTypeSlug);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    Promise.all([
      apiFetch<Category[]>("/categories"),
      apiFetch<Game[]>("/games"),
      apiFetch<OfferType[]>("/offer-types"),
    ])
      .then(([categoriesData, gamesData, offerTypesData]) => {
        const resolvedGame =
          gamesData.find((game) => game.slug === gameSlug) ?? null;
        const resolvedOfferType =
          offerTypesData.find((offerType) => offerType.slug === offerTypeSlug) ??
          null;
        const resolvedCategory =
          resolvedGame && resolvedOfferType
            ? categoriesData.find(
                (category) => category.name.toLowerCase() === "games"
              ) ?? null
            : null;

        setCategories(categoriesData);
        setSelectedGame(resolvedGame);
        setSelectedOfferType(resolvedOfferType);
        setSelectedCategory(resolvedCategory);
        setForm((currentForm) => ({
          ...currentForm,
          category_id: resolvedCategory
            ? String(resolvedCategory.id)
            : resolvedGame && resolvedOfferType
              ? ""
              : currentForm.category_id,
        }));
      })
      .catch(() => {
        setCategories([]);
        setSelectedGame(null);
        setSelectedOfferType(null);
        setSelectedCategory(null);
      });
  }, [gameSlug, offerTypeSlug, router]);

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
      if (form.category_id) {
        fd.append("category_id", form.category_id);
      }
      if (selectedGame) {
        fd.append("game_id", String(selectedGame.id));
      }
      if (selectedOfferType) {
        fd.append("offer_type_id", String(selectedOfferType.id));
      }
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

  const hasResolvedCatalogCategory = Boolean(
    selectedGame && selectedOfferType && selectedCategory
  );
  const showCatalogContext = Boolean(
    selectedGame || selectedOfferType || hasResolvedCatalogCategory || hasCatalogQuery
  );
  const showManualCategoryFallback = hasCatalogQuery && !hasResolvedCatalogCategory;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.createProductTitle}</h1>
      {showCatalogContext && (
        <div className="mb-6 rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm">
          <p className="font-medium text-gray-900">
            {messages.catalogContextPrefilled}
          </p>
          {hasResolvedCatalogCategory && (
            <p className="mt-2 text-gray-700">
              {messages.selectedCategoryLabel}: {messages.gamesCategoryName}
            </p>
          )}
          {selectedGame && (
            <p className="mt-2 text-gray-700">
              {messages.selectedGameLabel}:{" "}
              {getGameName(selectedGame, language)}
            </p>
          )}
          {selectedOfferType && (
            <p className="mt-1 text-gray-700">
              {messages.selectedOfferTypeLabel}:{" "}
              {getOfferTypeName(selectedOfferType, language)}
            </p>
          )}
          {hasResolvedCatalogCategory ? (
            <p className="mt-2 text-gray-600">{messages.categoryAutoAssigned}</p>
          ) : showManualCategoryFallback ? (
            <p className="mt-2 text-gray-600">{messages.categoryFallbackManual}</p>
          ) : null}
        </div>
      )}
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
        {!hasResolvedCatalogCategory && (
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
        )}
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
