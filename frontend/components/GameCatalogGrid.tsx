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
      <div>
        <h1 className="text-2xl font-bold">{messages.catalog}</h1>
        <p className="mt-1 text-sm text-gray-500">{messages.chooseGame}</p>
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
              className="block rounded-lg border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md"
            >
              <p className="font-semibold text-gray-900">
                {getDisplayName(game, language)}
              </p>
              <p className="mt-1 text-sm text-gray-500">{game.name}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
