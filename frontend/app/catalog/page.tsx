"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Game } from "@/lib/types";

function getDisplayName(game: Game) {
  return game.display_name_vi || game.name;
}

export default function CatalogPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Game[]>("/games")
      .then((data) => {
        setGames(data);
        setError(null);
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "Unable to load catalog.");
        setGames([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Catalog</h1>
        <p className="text-sm text-gray-500 mt-1">Choose a game to continue.</p>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading games...</p>
      ) : error ? (
        <p className="text-red-600 text-sm">{error}</p>
      ) : games.length === 0 ? (
        <p className="text-gray-500 text-sm">No games available.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {games.map((game) => (
            <Link
              key={game.id}
              href={`/catalog/${game.slug}`}
              className="block rounded-lg border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow"
            >
              <p className="font-semibold text-gray-900">{getDisplayName(game)}</p>
              <p className="mt-1 text-sm text-gray-500">{game.name}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
