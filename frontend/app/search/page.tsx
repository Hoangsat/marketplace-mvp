"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import ProductCard from "@/components/ProductCard";
import { useLanguage } from "@/components/LanguageProvider";
import { apiFetch } from "@/lib/api";
import { SearchResultsResponse } from "@/lib/types";

const EMPTY_RESULTS: SearchResultsResponse = {
  query: "",
  count: 0,
  page: 1,
  page_size: 24,
  has_more: false,
  results: [],
};

function SearchPageContent() {
  const searchParams = useSearchParams();
  const { messages } = useLanguage();
  const [data, setData] = useState<SearchResultsResponse>(EMPTY_RESULTS);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(false);

  const query = (searchParams.get("q") ?? "").trim();

  useEffect(() => {
    if (!query) {
      setData(EMPTY_RESULTS);
      setError(false);
      setLoading(false);
      return;
    }

    let isCancelled = false;
    setLoading(true);
    setError(false);

    apiFetch<SearchResultsResponse>(`/api/search?q=${encodeURIComponent(query)}&page=1`)
      .then((response) => {
        if (isCancelled) {
          return;
        }
        setData(response);
      })
      .catch(() => {
        if (isCancelled) {
          return;
        }
        setData(EMPTY_RESULTS);
        setError(true);
      })
      .finally(() => {
        if (!isCancelled) {
          setLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [query]);

  async function handleLoadMore() {
    if (!data.has_more || loadingMore || !query) {
      return;
    }

    setLoadingMore(true);
    try {
      const nextPage = data.page + 1;
      const response = await apiFetch<SearchResultsResponse>(
        `/api/search?q=${encodeURIComponent(query)}&page=${nextPage}`
      );
      setData((current) => ({
        ...response,
        results: [...current.results, ...response.results],
      }));
    } catch {
      setError(true);
    } finally {
      setLoadingMore(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900">{messages.searchResultsLabel}</h1>
        {query ? (
          <p className="mt-2 text-sm text-gray-600">
            "{query}" ({data.count})
          </p>
        ) : (
          <p className="mt-2 text-sm text-gray-600">{messages.noSearchQuery}</p>
        )}
      </section>

      {loading ? (
        <p className="text-sm text-gray-500">{messages.loadingProducts}</p>
      ) : error ? (
        <p className="text-sm text-red-600">{messages.loadProductsError}</p>
      ) : !query ? (
        <p className="text-sm text-gray-500">{messages.noSearchQuery}</p>
      ) : data.results.length === 0 ? (
        <p className="text-sm text-gray-500">{messages.noSearchResults}</p>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {data.results.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>

          {data.has_more && (
            <div className="flex justify-center">
              <button
                type="button"
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="rounded-xl bg-orange-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-orange-700 disabled:opacity-50"
              >
                {loadingMore ? messages.loadingProducts : messages.loadMoreResults}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<p className="text-sm text-gray-500">Loading...</p>}>
      <SearchPageContent />
    </Suspense>
  );
}
