"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Category, OfferType, Platform, PlatformDetail } from "@/lib/types";
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

export default function NewProductPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { language, messages } = useLanguage();
  const [categories, setCategories] = useState<Category[]>([]);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [offerTypes, setOfferTypes] = useState<OfferType[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null);
  const [selectedOfferType, setSelectedOfferType] = useState<OfferType | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [platformUsesOfferTypes, setPlatformUsesOfferTypes] = useState(false);

  const [form, setForm] = useState({
    title: "",
    description: "",
    price: "",
    stock: "",
    category_id: "",
    platform_id: "",
    offer_type_id: "",
  });
  const [images, setImages] = useState<FileList | null>(null);

  const platformSlug = searchParams.get("platform") || searchParams.get("game");
  const offerTypeSlug = searchParams.get("offerType");
  const hasCatalogQuery = Boolean(platformSlug || offerTypeSlug);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }

    let isCancelled = false;

    Promise.all([apiFetch<Category[]>("/categories"), apiFetch<Platform[]>("/platforms")])
      .then(async ([categoriesData, platformData]) => {
        const resolvedPlatform =
          platformData.find((platform) => platform.slug === platformSlug) ?? null;

        let platformDetail: PlatformDetail | null = null;
        if (resolvedPlatform) {
          platformDetail = await apiFetch<PlatformDetail>(
            `/platforms/${encodeURIComponent(resolvedPlatform.slug)}`
          );
        }

        const resolvedCategory =
          resolvedPlatform
            ? categoriesData.find(
                (category) => category.id === resolvedPlatform.category_id
              ) ?? null
            : null;
        const resolvedOfferTypes = platformDetail?.offer_types ?? [];
        const resolvedOfferType =
          resolvedOfferTypes.find((offerType) => offerType.slug === offerTypeSlug) ??
          null;

        if (isCancelled) {
          return;
        }

        setCategories(categoriesData);
        setPlatforms(platformData);
        setSelectedPlatform(resolvedPlatform);
        setSelectedOfferType(resolvedOfferType);
        setSelectedCategory(resolvedCategory);
        setOfferTypes(resolvedOfferTypes);
        setPlatformUsesOfferTypes(platformDetail?.has_offer_types ?? false);
        setForm((currentForm) => ({
          ...currentForm,
          category_id: resolvedCategory ? String(resolvedCategory.id) : currentForm.category_id,
          platform_id: resolvedPlatform ? String(resolvedPlatform.id) : currentForm.platform_id,
          offer_type_id: resolvedOfferType ? String(resolvedOfferType.id) : "",
        }));
      })
      .catch(() => {
        if (isCancelled) {
          return;
        }
        setCategories([]);
        setPlatforms([]);
        setOfferTypes([]);
        setSelectedPlatform(null);
        setSelectedOfferType(null);
        setSelectedCategory(null);
        setPlatformUsesOfferTypes(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [offerTypeSlug, platformSlug, router]);

  useEffect(() => {
    const platformId = Number(form.platform_id);
    const nextPlatform =
      platforms.find((platform) => platform.id === platformId) ?? null;

    if (!nextPlatform) {
      setSelectedPlatform(null);
      setSelectedCategory(null);
      setSelectedOfferType(null);
      setOfferTypes([]);
      setPlatformUsesOfferTypes(false);
      return;
    }

    if (selectedPlatform?.id === nextPlatform.id && offerTypes.length > 0) {
      return;
    }

    const nextCategory =
      categories.find((category) => category.id === nextPlatform.category_id) ?? null;
    setSelectedPlatform(nextPlatform);
    setSelectedCategory(nextCategory);
    setForm((current) => ({
      ...current,
      category_id: nextCategory ? String(nextCategory.id) : current.category_id,
    }));

    let isCancelled = false;
    apiFetch<PlatformDetail>(`/platforms/${encodeURIComponent(nextPlatform.slug)}`)
      .then((platformDetail) => {
        if (isCancelled) {
          return;
        }
        setOfferTypes(platformDetail.offer_types);
        setPlatformUsesOfferTypes(platformDetail.has_offer_types);

        if (!platformDetail.has_offer_types) {
          setSelectedOfferType(null);
          setForm((current) => ({ ...current, offer_type_id: "" }));
          return;
        }

        const nextOfferType =
          platformDetail.offer_types.find(
            (offerType) => offerType.id === Number(form.offer_type_id)
          ) ?? null;
        setSelectedOfferType(nextOfferType);
        if (!nextOfferType) {
          setForm((current) => ({ ...current, offer_type_id: "" }));
        }
      })
      .catch(() => {
        if (isCancelled) {
          return;
        }
        setOfferTypes([]);
        setPlatformUsesOfferTypes(false);
        setSelectedOfferType(null);
        setForm((current) => ({ ...current, offer_type_id: "" }));
      });

    return () => {
      isCancelled = true;
    };
  }, [categories, form.offer_type_id, form.platform_id, offerTypes.length, platforms, selectedPlatform?.id]);

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
      if (form.platform_id) {
        fd.append("platform_id", form.platform_id);
      }
      if (form.offer_type_id) {
        fd.append("offer_type_id", form.offer_type_id);
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

  const showCatalogContext = Boolean(
    selectedPlatform || selectedOfferType || selectedCategory || hasCatalogQuery
  );

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.createProductTitle}</h1>
      {showCatalogContext && (
        <div className="mb-6 rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm">
          <p className="font-medium text-gray-900">
            {messages.catalogContextPrefilled}
          </p>
          {selectedCategory && (
            <p className="mt-2 text-gray-700">
              {messages.selectedCategoryLabel}: {selectedCategory.name}
            </p>
          )}
          {selectedPlatform && (
            <p className="mt-2 text-gray-700">
              {messages.selectedGameLabel}:{" "}
              {getPlatformName(selectedPlatform, language)}
            </p>
          )}
          {selectedOfferType && (
            <p className="mt-1 text-gray-700">
              {messages.selectedOfferTypeLabel}:{" "}
              {getOfferTypeName(selectedOfferType, language)}
            </p>
          )}
          {selectedPlatform && (
            <p className="mt-2 text-gray-600">{messages.categoryAutoAssigned}</p>
          )}
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
        <Field label={messages.categoryLabel}>
          <select required value={form.category_id} className={input} disabled>
            <option value="">{messages.selectCategory}</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label={messages.selectedGameLabel}>
          <select
            required
            value={form.platform_id}
            onChange={(event) => set("platform_id", event.target.value)}
            className={input}
          >
            <option value="">{messages.chooseGame}</option>
            {platforms.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {getPlatformName(platform, language)}
              </option>
            ))}
          </select>
        </Field>
        {(platformUsesOfferTypes || offerTypes.length > 0) && (
          <Field label={messages.selectedOfferTypeLabel}>
            <select
              required={platformUsesOfferTypes}
              value={form.offer_type_id}
              onChange={(event) => set("offer_type_id", event.target.value)}
              className={input}
            >
              <option value="">{messages.chooseOfferType}</option>
              {offerTypes.map((offerType) => (
                <option key={offerType.id} value={offerType.id}>
                  {getOfferTypeName(offerType, language)}
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
