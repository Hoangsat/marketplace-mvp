"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import ProductCard from "@/components/ProductCard";
import { getToken } from "@/lib/auth";
import { Game, OfferType, Product } from "@/lib/types";
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

export default function CatalogOfferTypePage() {
  const { gameSlug, offerTypeSlug } = useParams<{
    gameSlug: string;
    offerTypeSlug: string;
  }>();
  const { language, messages } = useLanguage();
  const [game, setGame] = useState<Game | null>(null);
  const [offerType, setOfferType] = useState<OfferType | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [canSell, setCanSell] = useState(false);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setCanSell(!!getToken());
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, []);

  useEffect(() => {
    Promise.all([apiFetch<Game[]>("/games"), apiFetch<OfferType[]>("/offer-types")])
      .then(async ([games, offerTypes]) => {
        const selectedGame = games.find((item) => item.slug === gameSlug) ?? null;
        const selectedOfferType =
          offerTypes.find((item) => item.slug === offerTypeSlug) ?? null;

        if (!selectedGame || !selectedOfferType) {
          setGame(selectedGame);
          setOfferType(selectedOfferType);
          setProducts([]);
          setError(false);
          return;
        }

        const params = new URLSearchParams({
          game: selectedGame.slug,
          offer_type: selectedOfferType.slug,
        });
        const productData = await apiFetch<Product[]>(`/products?${params.toString()}`);

        setGame(selectedGame);
        setOfferType(selectedOfferType);
        setProducts(productData);
        setError(false);
      })
      .catch(() => {
        setGame(null);
        setOfferType(null);
        setProducts([]);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, [gameSlug, offerTypeSlug]);

  const missingMessage = !game
    ? messages.gameNotFound
    : !offerType
      ? messages.offerTypeNotFound
      : null;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <Link
          href={game ? `/catalog/${game.slug}` : "/catalog"}
          className="text-sm font-medium text-orange-600 hover:underline"
        >
          {messages.backToOfferTypes}
        </Link>
        <div className="mt-4 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">
              {game && offerType
                ? `${getGameName(game, language)} / ${getOfferTypeName(
                    offerType,
                    language
                  )}`
                : messages.catalog}
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-gray-600">
              {messages.browseProductsForSelection}
            </p>
          </div>
          {canSell && game && offerType && (
            <Link
              href={`/seller/products/new?game=${game.slug}&offerType=${offerType.slug}`}
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
        <p className="text-gray-500 text-sm">{messages.noProducts}</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
