"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import { SearchSuggestResponse } from "@/lib/types";

const EMPTY_SUGGESTIONS: SearchSuggestResponse = {
  query: "",
  categories: [],
  search_terms: [],
};

export default function HeaderSearch() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { messages } = useLanguage();
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [suggestions, setSuggestions] = useState<SearchSuggestResponse>(EMPTY_SUGGESTIONS);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setQuery(searchParams.get("q") ?? "");
  }, [pathname, searchParams]);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
    };
  }, []);

  useEffect(() => {
    const trimmedQuery = query.trim();
    if (trimmedQuery.length < 2) {
      setSuggestions(EMPTY_SUGGESTIONS);
      setLoading(false);
      return;
    }

    let isCancelled = false;
    setLoading(true);

    const timeoutId = window.setTimeout(() => {
      apiFetch<SearchSuggestResponse>(
        `/api/search/suggest?q=${encodeURIComponent(trimmedQuery)}`
      )
        .then((response) => {
          if (isCancelled) {
            return;
          }
          setSuggestions(response);
          setOpen(true);
        })
        .catch(() => {
          if (isCancelled) {
            return;
          }
          setSuggestions(EMPTY_SUGGESTIONS);
        })
        .finally(() => {
          if (!isCancelled) {
            setLoading(false);
          }
        });
    }, 250);

    return () => {
      isCancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [query]);

  const trimmedQuery = query.trim();
  const categorySuggestions = suggestions.categories;
  const searchTermSuggestions = suggestions.search_terms;
  const hasSuggestions =
    categorySuggestions.length > 0 || searchTermSuggestions.length > 0;
  const showEmptyState = !loading && !hasSuggestions;
  const shouldShowDropdown = open && trimmedQuery.length >= 2;

  function submitSearch(nextQuery = query) {
    const trimmed = nextQuery.trim();
    if (!trimmed) {
      setOpen(false);
      return;
    }
    setOpen(false);
    router.push(`/search?q=${encodeURIComponent(trimmed)}`);
  }

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="relative">
        <input
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            if (!open) {
              setOpen(true);
            }
          }}
          onFocus={() => {
            if (trimmedQuery.length >= 2) {
              setOpen(true);
            }
          }}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              submitSearch();
            }
            if (event.key === "Escape") {
              setOpen(false);
            }
          }}
          placeholder={messages.searchProducts}
          className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm outline-none transition focus:border-orange-300 focus:ring-2 focus:ring-orange-200"
        />
      </div>

      {shouldShowDropdown && (
        <div className="absolute left-0 right-0 top-[calc(100%+0.5rem)] z-50 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl">
          <div className="max-h-[28rem] overflow-y-auto p-3">
            {loading ? (
              <p className="px-2 py-3 text-sm text-gray-500">{messages.loading}</p>
            ) : (
              <div className="space-y-4">
                {categorySuggestions.length > 0 && (
                  <section>
                    <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-[0.18em] text-gray-400">
                      {messages.searchCategoriesGroupLabel}
                    </p>
                    <div className="space-y-1">
                      {categorySuggestions.map((item) => (
                        <Link
                          key={`${item.type}-${item.id}`}
                          href={item.url}
                          onClick={() => setOpen(false)}
                          className="block rounded-xl px-3 py-2 transition hover:bg-orange-50"
                        >
                          <p className="text-sm font-medium text-gray-900">{item.label}</p>
                          {item.subtitle && (
                            <p className="mt-0.5 text-xs text-gray-500">{item.subtitle}</p>
                          )}
                        </Link>
                      ))}
                    </div>
                  </section>
                )}

                {searchTermSuggestions.length > 0 && (
                  <section>
                    <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-[0.18em] text-gray-400">
                      {messages.searchTermsGroupLabel}
                    </p>
                    <div className="space-y-1">
                      {searchTermSuggestions.map((item) => (
                        <Link
                          key={item.query}
                          href={item.url}
                          onClick={() => setOpen(false)}
                          className="block rounded-xl px-3 py-2 transition hover:bg-orange-50"
                        >
                          <p className="text-sm font-medium text-gray-900">{item.label}</p>
                        </Link>
                      ))}
                    </div>
                  </section>
                )}

                {showEmptyState && (
                  <p className="px-2 py-1 text-sm text-gray-500">
                    {messages.noSuggestResults}
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="border-t border-gray-100 bg-gray-50 p-3">
            <button
              type="button"
              onClick={() => submitSearch()}
              className="w-full rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-orange-700"
            >
              {messages.showAllResults}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
