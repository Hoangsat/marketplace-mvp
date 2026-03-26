// components/ProductCard.tsx
import Link from "next/link";
import Image from "next/image";
import { Product } from "@/lib/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Props {
  product: Product;
}

export default function ProductCard({ product }: Props) {
  const imgSrc =
    product.images?.[0] ? `${BASE}${product.images[0]}` : null;

  return (
    <Link
      href={`/products/${product.id}`}
      className="group block bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
    >
      <div className="aspect-square bg-gray-100 relative overflow-hidden">
        {imgSrc ? (
          <Image
            src={imgSrc}
            alt={product.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-200"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400 text-4xl">
            📦
          </div>
        )}
      </div>
      <div className="p-3">
        <p className="text-sm font-medium text-gray-900 line-clamp-2 leading-snug">
          {product.title}
        </p>
        <p className="mt-1 text-orange-600 font-semibold text-sm">
          ${product.price.toFixed(2)}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">
          {product.stock > 0 ? `${product.stock} in stock` : "Out of stock"}
        </p>
      </div>
    </Link>
  );
}
