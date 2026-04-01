"use client";

// app/products/[id]/page.tsx - Product detail with images + add to cart

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { addToCart } from "@/lib/cart";
import { resolveMediaUrl } from "@/lib/media";
import { Product } from "@/lib/types";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { messages } = useLanguage();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [qty, setQty] = useState(1);
  const [activeImg, setActiveImg] = useState(0);

  useEffect(() => {
    apiFetch<Product>(`/products/${id}`)
      .then((response) => {
        setProduct(response);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [id]);

  function handleAddToCart() {
    if (!product) return;

    addToCart(
      {
        product_id: product.id,
        title: product.title,
        price: product.price,
        image: product.images?.[0] ?? null,
        seller_id: product.seller_id,
      },
      qty
    );
    window.dispatchEvent(new Event("cartUpdated"));
    showToast(messages.addedToCart, "success");
  }

  if (loading) {
    return <p className="text-gray-500">{messages.loading}</p>;
  }

  if (!product) {
    return <p className="text-gray-500">{messages.productNotFound}</p>;
  }

  const activeImageUrl = resolveMediaUrl(product.images?.[activeImg]);
  const hasSellerProfile =
    !!product.seller_nickname && product.seller_nickname !== "Seller";
  const sellerHref = hasSellerProfile
    ? `/sellers/${encodeURIComponent(product.seller_nickname ?? "")}`
    : null;

  return (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => router.back()}
        className="text-sm text-gray-500 hover:underline mb-4 block"
      >
        {messages.back}
      </button>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden relative">
            {activeImageUrl ? (
              <Image
                src={activeImageUrl}
                alt={product.title}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, 50vw"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-6xl text-gray-300">
                []
              </div>
            )}
          </div>
          {product.images?.length > 1 && (
            <div className="flex gap-2 mt-2">
              {product.images.map((img, index) => (
                <button
                  key={index}
                  onClick={() => setActiveImg(index)}
                  className={`w-14 h-14 rounded border-2 overflow-hidden relative ${
                    index === activeImg ? "border-orange-500" : "border-gray-200"
                  }`}
                >
                  <Image
                    src={resolveMediaUrl(img) ?? ""}
                    alt={`Image ${index + 1}`}
                    fill
                    className="object-cover"
                    sizes="56px"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-4">
          <h1 className="text-2xl font-bold">{product.title}</h1>
          <p className="text-2xl text-orange-600 font-semibold">
            ${product.price.toFixed(2)}
          </p>
          <p className="text-sm text-gray-600 leading-relaxed">
            {product.description}
          </p>
          <p className="text-sm text-gray-500">
            {messages.categoryLabel}:{" "}
            <span className="font-medium">{product.category?.name}</span>
          </p>
          <p className="text-sm text-gray-500">
            {messages.seller}:{" "}
            {sellerHref ? (
              <Link
                href={sellerHref}
                className="font-medium hover:text-orange-600 hover:underline"
              >
                {product.seller_nickname}
              </Link>
            ) : (
              <span className="font-medium">
                {product.seller_nickname || "Seller"}
              </span>
            )}
          </p>
          <p className="text-sm text-gray-500">
            {messages.stockLabel}:{" "}
            <span
              className={
                product.stock > 0
                  ? "text-green-600 font-medium"
                  : "text-red-500 font-medium"
              }
            >
              {product.stock > 0
                ? messages.inStock(product.stock)
                : messages.outOfStock}
            </span>
          </p>

          {product.stock > 0 && (
            <div className="flex items-center gap-3 mt-2">
              <label className="text-sm font-medium">{messages.quantity}:</label>
              <input
                type="number"
                min={1}
                max={product.stock}
                value={qty}
                onChange={(event) =>
                  setQty(
                    Math.max(
                      1,
                      Math.min(product.stock, Number(event.target.value))
                    )
                  )
                }
                className="w-16 border border-gray-300 rounded px-2 py-1 text-sm"
              />
              <button
                onClick={handleAddToCart}
                className="bg-orange-600 text-white px-5 py-2 rounded font-medium hover:bg-orange-700"
              >
                {messages.addToCart}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
