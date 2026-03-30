"use client";

// app/products/[id]/page.tsx — Product detail with images + add to cart

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { API_BASE_URL, apiFetch } from "@/lib/api";
import { Product } from "@/lib/types";
import { addToCart } from "@/lib/cart";
import { showToast } from "@/components/Toast";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [qty, setQty] = useState(1);
  const [activeImg, setActiveImg] = useState(0);

  useEffect(() => {
    apiFetch<Product>(`/products/${id}`)
      .then((p) => { setProduct(p); setLoading(false); })
      .catch(() => { setLoading(false); });
  }, [id]);

  function handleAddToCart() {
    if (!product) return;
    addToCart({
      product_id: product.id,
      title: product.title,
      price: product.price,
      image: product.images?.[0] ?? null,
    }, qty);
    window.dispatchEvent(new Event("cartUpdated"));
    showToast("Added to cart!", "success");
  }

  if (loading) return <p className="text-gray-500">Loading...</p>;
  if (!product) return <p className="text-gray-500">Product not found.</p>;

  return (
    <div className="max-w-4xl mx-auto">
      <button onClick={() => router.back()} className="text-sm text-gray-500 hover:underline mb-4 block">
        ← Back
      </button>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Images */}
        <div>
          <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden relative">
            {product.images?.[activeImg] ? (
              <Image
                src={`${API_BASE_URL}${product.images[activeImg]}`}
                alt={product.title}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, 50vw"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-6xl text-gray-300">📦</div>
            )}
          </div>
          {product.images?.length > 1 && (
            <div className="flex gap-2 mt-2">
              {product.images.map((img, i) => (
                <button
                  key={i}
                  onClick={() => setActiveImg(i)}
                  className={`w-14 h-14 rounded border-2 overflow-hidden relative ${i === activeImg ? "border-orange-500" : "border-gray-200"}`}
                >
                  <Image
                    src={`${API_BASE_URL}${img}`}
                    alt={`Image ${i + 1}`}
                    fill
                    className="object-cover"
                    sizes="56px"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex flex-col gap-4">
          <h1 className="text-2xl font-bold">{product.title}</h1>
          <p className="text-2xl text-orange-600 font-semibold">${product.price.toFixed(2)}</p>
          <p className="text-sm text-gray-600 leading-relaxed">{product.description}</p>
          <p className="text-sm text-gray-500">
            Category: <span className="font-medium">{product.category?.name}</span>
          </p>
          <p className="text-sm text-gray-500">
            Stock: <span className={product.stock > 0 ? "text-green-600 font-medium" : "text-red-500 font-medium"}>
              {product.stock > 0 ? `${product.stock} available` : "Out of stock"}
            </span>
          </p>

          {product.stock > 0 && (
            <div className="flex items-center gap-3 mt-2">
              <label className="text-sm font-medium">Qty:</label>
              <input
                type="number"
                min={1}
                max={product.stock}
                value={qty}
                onChange={(e) => setQty(Math.max(1, Math.min(product.stock, Number(e.target.value))))}
                className="w-16 border border-gray-300 rounded px-2 py-1 text-sm"
              />
              <button
                onClick={handleAddToCart}
                className="bg-orange-600 text-white px-5 py-2 rounded font-medium hover:bg-orange-700"
              >
                Add to Cart
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
