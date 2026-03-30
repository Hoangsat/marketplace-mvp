"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import { Game, OfferType, Product } from "@/lib/types";

function getGameName(game: Game) {
  return game.display_name_vi || game.name;
}

function getOfferTypeName(offerType: OfferType) {
  return offerType.display_name_vi || offerType.name;
}

export default function CatalogOfferTypePage() {
  const { gameSlug, offerTypeSlug } = useParams<{
    gameSlug: string;
    offerTypeSlug: string;
  }>();
  const [game, setGame] = useState<Game | null>(null);
  const [offerType, setOfferType] = useState<OfferType | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
          setError(null);
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
        setError(null);
      })
      .catch((e: unknown) => {
        setGame(null);
        setOfferType(null);
        setProducts([]);
        setError(e instanceof Error ? e.message : "Unable to load products.");
      })
      .finally(() => setLoading(false));
  }, [gameSlug, offerTypeSlug]);

  const missingMessage = !game
    ? "Game not found."
    : !offerType
      ? "Offer type not found."
      : null;

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Link
          href={game ? `/catalog/${game.slug}` : "/catalog"}
          className="text-sm text-orange-600 hover:underline"
        >
          Back to offer types
        </Link>
        <div>
          <h1 className="text-2xl font-bold">
            {game && offerType
              ? `${getGameName(game)} / ${getOfferTypeName(offerType)}`
              : "Catalog"}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Browse products for this catalog selection.
          </p>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading products...</p>
      ) : error ? (
        <p className="text-red-600 text-sm">{error}</p>
      ) : missingMessage ? (
        <p className="text-gray-500 text-sm">{missingMessage}</p>
      ) : products.length === 0 ? (
        <p className="text-gray-500 text-sm">No products found.</p>
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
