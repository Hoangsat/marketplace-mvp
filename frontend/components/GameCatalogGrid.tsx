"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import { type Language } from "@/lib/i18n";
import { Game } from "@/lib/types";

function getDisplayName(game: Game, language: Language) {
  if (language === "vi") {
    return game.display_name_vi || game.name;
  }
  return game.name;
}

export default function GameCatalogGrid() {
  const { language, messages } = useLanguage();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiFetch<Game[]>("/games")
      .then((data) => {
        setGames(data);
        setError(false);
      })
      .catch(() => {
        setError(true);
        setGames([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-orange-100 bg-gradient-to-br from-white to-orange-50 p-6 shadow-sm">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          {messages.catalog}
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-gray-600">
          {messages.chooseGame}
        </p>
      </div>

      {loading ? (
        <p className="text-sm text-gray-500">{messages.loadingGames}</p>
      ) : error ? (
        <p className="text-sm text-red-600">{messages.loadCatalogError}</p>
      ) : games.length === 0 ? (
        <p className="text-sm text-gray-500">{messages.noGames}</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {games.map((game) => (
            <Link
              key={game.id}
              href={`/catalog/${game.slug}`}
              className="group block rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-md"
            >
              <p className="text-lg font-semibold text-gray-900 transition-colors group-hover:text-orange-700">
                {getDisplayName(game, language)}
              </p>
              <p className="mt-2 text-sm text-gray-500">{game.name}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
