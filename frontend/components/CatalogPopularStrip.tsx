"use client";

type PopularItem = {
  name: string;
  emoji: string;
  background: string;
};

const POPULAR_ITEMS: PopularItem[] = [
  { name: "Steam", emoji: "🎮", background: "#0f172a" },
  { name: "PlayStation", emoji: "🎯", background: "#1d4ed8" },
  { name: "Telegram Premium", emoji: "✈️", background: "#0ea5e9" },
  { name: "ChatGPT Plus", emoji: "✨", background: "#10b981" },
  { name: "Netflix", emoji: "🎬", background: "#b91c1c" },
  { name: "Spotify", emoji: "🎵", background: "#15803d" },
  { name: "Canva Pro", emoji: "🎨", background: "#7c3aed" },
  { name: "Discord Nitro", emoji: "💬", background: "#4f46e5" },
  { name: "FC Online", emoji: "⚽", background: "#ea580c" },
  { name: "Valorant", emoji: "🔺", background: "#be123c" },
  { name: "Mobile Legends", emoji: "📱", background: "#0369a1" },
  { name: "YouTube Premium", emoji: "▶️", background: "#dc2626" },
];

function buildMockImage(name: string, emoji: string, background: string) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240">
      <rect width="320" height="240" rx="28" fill="${background}" />
      <circle cx="250" cy="70" r="56" fill="rgba(255,255,255,0.14)" />
      <circle cx="80" cy="190" r="72" fill="rgba(255,255,255,0.10)" />
      <text x="32" y="116" font-size="54">${emoji}</text>
      <text x="32" y="190" font-size="28" font-family="Arial, sans-serif" fill="#ffffff">${name}</text>
    </svg>
  `;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

export default function CatalogPopularStrip() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Popular</h2>
      </div>

      <div className="overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        <div className="flex min-w-max gap-4">
          {POPULAR_ITEMS.map((item) => (
            <article
              key={item.name}
              className="group w-52 shrink-0 overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="aspect-[1.08/1] overflow-hidden bg-gray-100">
                <img
                  src={buildMockImage(item.name, item.emoji, item.background)}
                  alt={item.name}
                  className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              </div>
              <div className="p-4">
                <p className="text-base font-semibold text-gray-900">{item.name}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
