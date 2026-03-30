"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import { Game, OfferType } from "@/lib/types";
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

export default function CatalogGamePage() {
  const { gameSlug } = useParams<{ gameSlug: string }>();
  const { language, messages } = useLanguage();
  const [game, setGame] = useState<Game | null>(null);
  const [offerTypes, setOfferTypes] = useState<OfferType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([apiFetch<Game[]>("/games"), apiFetch<OfferType[]>("/offer-types")])
      .then(([games, offerTypeData]) => {
        const selectedGame = games.find((item) => item.slug === gameSlug) ?? null;
        if (!selectedGame) {
          setGame(null);
          setOfferTypes([]);
          setError(false);
          return;
        }

        setGame(selectedGame);
        setOfferTypes(offerTypeData);
        setError(false);
      })
      .catch(() => {
        setGame(null);
        setOfferTypes([]);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, [gameSlug]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <Link href="/catalog" className="text-sm font-medium text-orange-600 hover:underline">
          {messages.backToCatalog}
        </Link>
        <div className="mt-3">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            {game ? getGameName(game, language) : messages.catalog}
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-gray-600">
            {messages.chooseOfferType}
          </p>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">{messages.loadingOfferTypes}</p>
      ) : error ? (
        <p className="text-red-600 text-sm">{messages.loadCatalogError}</p>
      ) : !game ? (
        <p className="text-gray-500 text-sm">{messages.gameNotFound}</p>
      ) : offerTypes.length === 0 ? (
        <p className="text-gray-500 text-sm">{messages.noOfferTypes}</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {offerTypes.map((offerType) => (
            <Link
              key={offerType.id}
              href={`/catalog/${game.slug}/${offerType.slug}`}
              className="group block rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-md"
            >
              <p className="text-lg font-semibold text-gray-900 transition-colors group-hover:text-orange-700">
                {getOfferTypeName(offerType, language)}
              </p>
              <p className="mt-2 text-sm text-gray-500">{offerType.name}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
