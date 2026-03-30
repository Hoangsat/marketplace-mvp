"use client";

// app/seller/orders/page.tsx - Order items for seller's own products

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { getMoneyStatusLabel, getOrderStatusLabel } from "@/lib/i18n";
import { SellerOrderItem } from "@/lib/types";

export default function SellerOrdersPage() {
  const router = useRouter();
  const { messages } = useLanguage();
  const [items, setItems] = useState<SellerOrderItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }

    apiFetch<SellerOrderItem[]>("/orders/seller")
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return <p className="text-gray-500">{messages.loading}</p>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{messages.salesOrderItems}</h1>
      {items.length === 0 ? (
        <p className="text-gray-500">{messages.noSellerOrders}</p>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
          {items.map((item) => (
            <div
              key={item.id}
              className="px-4 py-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between text-sm"
            >
              <div>
                <p className="font-medium">
                  {item.product?.title ??
                    `${messages.productFallback} #${item.product_id}`}
                </p>
                <p className="text-gray-400 text-xs">
                  {messages.orderPrefix} #{item.order_id} - {messages.quantityShort}{" "}
                  {item.quantity}
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <span className="inline-block text-xs px-2 py-0.5 rounded-full font-medium bg-blue-100 text-blue-700">
                    {messages.orderStatusLabel}:{" "}
                    {getOrderStatusLabel(messages, item.order_status)}
                  </span>
                  <span
                    className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium ${getMoneyStatusClasses(
                      item.payout_status
                    )}`}
                  >
                    {messages.payoutStatusLabel}:{" "}
                    {getMoneyStatusLabel(messages, item.payout_status)}
                  </span>
                </div>
              </div>
              <div className="sm:text-right">
                <p className="text-xs text-gray-500">
                  {messages.sellerAmountLabel}
                </p>
                <p className="font-semibold text-orange-600">
                  ${item.seller_amount.toFixed(2)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getMoneyStatusClasses(status: string) {
  if (status === "available") return "bg-green-100 text-green-700";
  if (status === "paid_out") return "bg-slate-200 text-slate-700";
  if (status === "on_hold") return "bg-yellow-100 text-yellow-700";
  if (status === "cancelled") return "bg-gray-100 text-gray-700";
  return "bg-slate-100 text-slate-700";
}
