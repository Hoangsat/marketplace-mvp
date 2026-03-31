"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { getMoneyStatusLabel, getOrderStatusLabel } from "@/lib/i18n";
import { PayoutRequest, Product, SellerDashboardData } from "@/lib/types";

export default function SellerDashboardPage() {
  const router = useRouter();
  const { messages } = useLanguage();
  const [dashboard, setDashboard] = useState<SellerDashboardData | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [payoutAmount, setPayoutAmount] = useState("");
  const [submittingPayout, setSubmittingPayout] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }

    Promise.all([
      apiFetch<SellerDashboardData>("/seller/dashboard"),
      apiFetch<Product[]>("/seller/products"),
    ])
      .then(([dashboardData, productData]) => {
        setDashboard(dashboardData);
        setProducts(productData);
      })
      .catch((e: unknown) =>
        showToast(
          e instanceof Error ? e.message : messages.unableToLoadSellerDashboard,
          "error"
        )
      )
      .finally(() => setLoading(false));
  }, [messages.unableToLoadSellerDashboard, router]);

  async function handleDelete(id: number) {
    if (!confirm(messages.deleteProductConfirm)) return;
    try {
      await apiFetch(`/products/${id}`, { method: "DELETE" });
      showToast(messages.productDeleted, "success");
      setProducts((currentProducts) =>
        currentProducts.filter((product) => product.id !== id)
      );
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : messages.deleteFailed, "error");
    }
  }

  async function handleMarkDelivered(orderId: number) {
    try {
      await apiFetch(`/orders/${orderId}/mark-delivered`, { method: "POST" });
      showToast(messages.orderMarkedDelivered, "success");
      const updatedDashboard =
        await apiFetch<SellerDashboardData>("/seller/dashboard");
      setDashboard(updatedDashboard);
    } catch (e: unknown) {
      showToast(
        e instanceof Error ? e.message : messages.unableToUpdateOrderStatus,
        "error"
      );
    }
  }

  async function handleSubmitPayoutRequest(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!payoutAmount.trim()) {
      showToast(messages.payoutAmountRequired, "error");
      return;
    }

    if (Number(payoutAmount) <= 0) {
      showToast(messages.payoutAmountMustBePositive, "error");
      return;
    }

    try {
      setSubmittingPayout(true);
      await apiFetch<PayoutRequest>("/seller/payout-requests", {
        method: "POST",
        body: JSON.stringify({ amount: payoutAmount }),
      });
      showToast(messages.payoutRequestSubmitted, "success");
      setPayoutAmount("");
      const updatedDashboard =
        await apiFetch<SellerDashboardData>("/seller/dashboard");
      setDashboard(updatedDashboard);
    } catch (e: unknown) {
      showToast(
        e instanceof Error ? e.message : messages.payoutRequestFailed,
        "error"
      );
    } finally {
      setSubmittingPayout(false);
    }
  }

  if (loading) {
    return <p className="text-gray-500">{messages.loading}</p>;
  }

  if (!dashboard) {
    return (
      <p className="text-gray-500">{messages.unableToLoadSellerDashboard}.</p>
    );
  }

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-bold mb-6">
          {messages.sellerDashboardTitle}
        </h1>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <p className="text-sm text-gray-500 mb-2">
              {messages.pendingBalanceOnHold}
            </p>
            <p className="text-2xl font-semibold text-orange-600">
              ${Number(dashboard.balance_pending).toFixed(2)}
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <p className="text-sm text-gray-500 mb-2">
              {messages.availableBalance}
            </p>
            <p className="text-2xl font-semibold text-green-600">
              ${Number(dashboard.balance_available).toFixed(2)}
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <p className="text-sm text-gray-500 mb-2">
              {messages.paidOutBalance}
            </p>
            <p className="text-2xl font-semibold text-slate-700">
              ${Number(dashboard.balance_paid_out).toFixed(2)}
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <p className="text-sm text-gray-500 mb-2">
              {messages.totalEarnings}
            </p>
            <p className="text-2xl font-semibold text-blue-700">
              ${Number(dashboard.total_earned).toFixed(2)}
            </p>
          </div>
        </div>
        <div className="mt-4 bg-white border border-gray-200 rounded-lg p-5">
          <h2 className="text-lg font-semibold mb-4">
            {messages.payoutRequestTitle}
          </h2>
          <form
            onSubmit={handleSubmitPayoutRequest}
            className="flex flex-col gap-3 sm:flex-row sm:items-end"
          >
            <div className="flex-1">
              <label
                htmlFor="payout-amount"
                className="block text-sm text-gray-500 mb-2"
              >
                {messages.payoutAmountLabel}
              </label>
              <input
                id="payout-amount"
                type="number"
                min="0.01"
                step="0.01"
                value={payoutAmount}
                onChange={(event) => setPayoutAmount(event.target.value)}
                placeholder={messages.payoutAmountPlaceholder}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
              />
            </div>
            <button
              type="submit"
              disabled={submittingPayout}
              className="bg-orange-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {submittingPayout ? messages.submitting : messages.requestPayout}
            </button>
          </form>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-6">{messages.myOrders}</h2>
        {dashboard.orders.length === 0 ? (
          <p className="text-gray-500">{messages.noSellerOrders}</p>
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
            {dashboard.orders.map((order) => (
              <div
                key={order.id}
                className="px-4 py-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="font-medium text-sm">
                    {messages.orderPrefix} #{order.id}
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(order.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex flex-col gap-2 text-sm sm:items-end">
                  <p className="text-xs text-gray-500">
                    {messages.sellerAmountLabel}
                  </p>
                  <p className="font-semibold text-orange-600">
                    ${Number(order.seller_amount).toFixed(2)}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <span className="inline-block text-xs px-2 py-0.5 rounded-full font-medium bg-blue-100 text-blue-700">
                      {messages.orderStatusLabel}:{" "}
                      {getOrderStatusLabel(messages, order.status)}
                    </span>
                    <span
                      className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium ${getMoneyStatusClasses(
                        order.payout_status
                      )}`}
                    >
                      {messages.payoutStatusLabel}:{" "}
                      {getMoneyStatusLabel(messages, order.payout_status)}
                    </span>
                  </div>
                  {order.status === "paid" && (
                    <button
                      onClick={() => handleMarkDelivered(order.id)}
                      className="mt-1 text-xs bg-orange-600 text-white px-3 py-1 rounded hover:bg-orange-700 transition"
                    >
                      {messages.markAsDelivered}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">{messages.myProducts}</h2>
          <Link
            href="/seller/products/new"
            className="bg-orange-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-orange-700"
          >
            {messages.newProduct}
          </Link>
        </div>

        {products.length === 0 ? (
          <p className="text-gray-500">{messages.noSellerProducts}</p>
        ) : (
          <div className="space-y-3">
            {products.map((product) => (
              <div
                key={product.id}
                className="flex items-center justify-between bg-white border border-gray-200 rounded-lg px-4 py-3"
              >
                <div className="min-w-0">
                  <p className="font-medium text-sm truncate">{product.title}</p>
                  <p className="text-xs text-gray-400">
                    ${product.price.toFixed(2)} -{" "}
                    {product.stock > 0
                      ? messages.inStock(product.stock)
                      : messages.outOfStock}
                  </p>
                </div>
                <div className="flex gap-3 text-sm shrink-0 ml-4">
                  <Link
                    href={`/seller/products/${product.id}/edit`}
                    className="text-blue-600 hover:underline"
                  >
                    {messages.edit}
                  </Link>
                  <button
                    onClick={() => handleDelete(product.id)}
                    className="text-red-500 hover:underline"
                  >
                    {messages.delete}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8">
          <Link
            href="/seller/orders"
            className="text-sm text-orange-600 hover:underline"
          >
            {messages.viewOrderItems}
          </Link>
        </div>
      </section>
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
