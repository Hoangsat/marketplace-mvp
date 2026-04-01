"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import ProductCard from "@/components/ProductCard";
import { useLanguage } from "@/components/LanguageProvider";
import { apiFetch } from "@/lib/api";
import { PublicSellerProfile } from "@/lib/types";

export default function SellerProfilePage() {
  const { nickname } = useParams<{ nickname: string }>();
  const { messages } = useLanguage();
  const [profile, setProfile] = useState<PublicSellerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    apiFetch<PublicSellerProfile>(`/api/sellers/${encodeURIComponent(nickname)}/`)
      .then((response) => {
        if (isCancelled) return;
        setProfile(response);
        setNotFound(false);
        setError(false);
      })
      .catch((err: unknown) => {
        if (isCancelled) return;
        if (err instanceof Error && err.message === "Seller not found") {
          setNotFound(true);
          setError(false);
          setProfile(null);
          return;
        }

        setError(true);
        setNotFound(false);
        setProfile(null);
      })
      .finally(() => {
        if (!isCancelled) {
          setLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [nickname]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <Link
          href="/catalog"
          className="text-sm font-medium text-orange-600 hover:underline"
        >
          {messages.backToCatalog}
        </Link>
        <div className="mt-4">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            {profile?.nickname || nickname}
          </h1>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">{messages.loadingProducts}</p>
      ) : notFound ? (
        <p className="text-gray-500 text-sm">{messages.sellerProfileNotFound}</p>
      ) : error ? (
        <p className="text-red-600 text-sm">{messages.loadSellerProfileError}</p>
      ) : !profile || profile.products.length === 0 ? (
        <p className="text-gray-500 text-sm">{messages.noProducts}</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {profile.products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
