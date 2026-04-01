"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Category, OfferType, Platform, PlatformDetail, Product } from "@/lib/types";
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

export default function EditProductPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { language, messages } = useLanguage();
  const [categories, setCategories] = useState<Category[]>([]);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [offerTypes, setOfferTypes] = useState<OfferType[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newImages, setNewImages] = useState<FileList | null>(null);
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

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }

    Promise.all([
      apiFetch<Product>(`/products/${id}`),
      apiFetch<Category[]>("/categories"),
      apiFetch<Platform[]>("/platforms"),
    ])
      .then(async ([product, categoriesData, platformsData]) => {
        let detail: PlatformDetail | null = null;
        if (product.platform?.slug) {
          detail = await apiFetch<PlatformDetail>(
            `/platforms/${encodeURIComponent(product.platform.slug)}`
          );
        }

        setForm({
          title: product.title,
          description: product.description,
          price: String(product.price),
          stock: String(product.stock),
          category_id: String(product.category_id),
          platform_id: product.platform_id ? String(product.platform_id) : "",
          offer_type_id: product.offer_type_id ? String(product.offer_type_id) : "",
        });
        setCategories(categoriesData);
        setPlatforms(platformsData);
        setOfferTypes(detail?.offer_types ?? []);
        setPlatformUsesOfferTypes(detail?.has_offer_types ?? false);
      })
      .catch((error: Error) => showToast(error.message, "error"))
      .finally(() => setLoading(false));
  }, [id, router]);

  const selectedCategoryId = Number(form.category_id);
  const availablePlatforms = form.category_id
    ? platforms.filter((platform) => platform.category_id === selectedCategoryId)
    : platforms;
  const categoryHasPlatforms = availablePlatforms.length > 0;
  const categoryIsLocked = Boolean(form.platform_id);

  useEffect(() => {
    const platformId = Number(form.platform_id);
    const platform = platforms.find((item) => item.id === platformId);
    if (!platform) {
      setOfferTypes([]);
      setPlatformUsesOfferTypes(false);
      if (form.offer_type_id) {
        setForm((current) => ({ ...current, offer_type_id: "" }));
      }
      return;
    }

    const category =
      categories.find((item) => item.id === platform.category_id) ?? null;
    if (category && form.category_id !== String(category.id)) {
      setForm((current) => ({ ...current, category_id: String(category.id) }));
    }

    let isCancelled = false;
    apiFetch<PlatformDetail>(`/platforms/${encodeURIComponent(platform.slug)}`)
      .then((detail) => {
        if (isCancelled) {
          return;
        }
        setOfferTypes(detail.offer_types);
        setPlatformUsesOfferTypes(detail.has_offer_types);
        if (
          detail.has_offer_types &&
          !detail.offer_types.some(
            (offerType) => offerType.id === Number(form.offer_type_id)
          )
        ) {
          setForm((current) => ({ ...current, offer_type_id: "" }));
        }
        if (!detail.has_offer_types && form.offer_type_id) {
          setForm((current) => ({ ...current, offer_type_id: "" }));
        }
      })
      .catch(() => {
        if (isCancelled) {
          return;
        }
        setOfferTypes([]);
        setPlatformUsesOfferTypes(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [categories, form.offer_type_id, form.platform_id, platforms]);

  function set(field: string, value: string) {
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      await apiFetch(`/products/${id}`, {
        method: "PUT",
        body: JSON.stringify({
          title: form.title,
          description: form.description,
          price: parseFloat(form.price),
          stock: parseInt(form.stock),
          category_id: parseInt(form.category_id),
          platform_id: form.platform_id ? parseInt(form.platform_id) : null,
          offer_type_id: form.offer_type_id ? parseInt(form.offer_type_id) : null,
        }),
      });

      if (newImages && newImages.length > 0) {
        const fd = new FormData();
        Array.from(newImages).forEach((file) => fd.append("images", file));
        await apiFetch(`/products/${id}/images`, { method: "POST", body: fd });
      }

      showToast(messages.productUpdated, "success");
      router.push("/seller/dashboard");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : messages.updateFailed, "error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-gray-500">{messages.loading}</p>;
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.editProductTitle}</h1>
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
          <select
            required
            value={form.category_id}
            onChange={(event) => {
              setForm((current) => ({
                ...current,
                category_id: event.target.value,
                platform_id: "",
                offer_type_id: "",
              }));
            }}
            className={input}
            disabled={categoryIsLocked}
          >
            <option value="">{messages.selectCategory}</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          {categoryIsLocked && (
            <p className="mt-1 text-xs text-gray-500">{messages.categoryAutoAssigned}</p>
          )}
        </Field>
        <Field label={messages.selectedGameLabel}>
          <select
            required={categoryHasPlatforms}
            value={form.platform_id}
            onChange={(event) => {
              const nextPlatformId = event.target.value;
              if (!nextPlatformId) {
                setForm((current) => ({
                  ...current,
                  platform_id: "",
                  offer_type_id: "",
                }));
                return;
              }

              const nextPlatform = availablePlatforms.find(
                (platform) => String(platform.id) === nextPlatformId
              );
              setForm((current) => ({
                ...current,
                category_id: nextPlatform
                  ? String(nextPlatform.category_id)
                  : current.category_id,
                platform_id: nextPlatformId,
                offer_type_id: "",
              }));
            }}
            className={input}
          >
            <option value="">{messages.chooseGame}</option>
            {availablePlatforms.map((platform) => (
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
        <Field label={messages.replaceImagesLabel}>
          <input
            type="file"
            accept="image/jpeg,image/png"
            multiple
            onChange={(event) => setNewImages(event.target.files)}
            className="text-sm text-gray-600"
          />
          <p className="text-xs text-gray-400 mt-1">{messages.replaceImagesHelp}</p>
        </Field>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 bg-orange-600 text-white py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50"
          >
            {saving ? messages.saving : messages.saveChanges}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
          >
            {messages.cancel}
          </button>
        </div>
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
