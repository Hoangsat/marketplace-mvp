"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { showToast } from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Order } from "@/lib/types";

export default function OrderPaymentPage() {
  const router = useRouter();
  const params = useParams();
  const { messages } = useLanguage();
  const id = params.id as string;

  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    if (!id) return;

    apiFetch<Order>(`/orders/${id}`)
      .then(setOrder)
      .catch((err) => {
        showToast(
          err instanceof Error ? err.message : messages.failedToLoadOrder,
          "error"
        );
        router.push("/orders");
      })
      .finally(() => setLoading(false));
  }, [id, messages.failedToLoadOrder, router]);

  async function handleMarkPaid() {
    setSubmitting(true);
    try {
      const updatedOrder = await apiFetch<Order>(
        `/orders/${id}/mark-payment-submitted`,
        {
          method: "POST",
        }
      );
      setOrder(updatedOrder);
      showToast(messages.paymentSubmitted, "success");
    } catch (err: unknown) {
      showToast(
        err instanceof Error ? err.message : messages.failedToSubmit,
        "error"
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <p className="text-gray-500">{messages.loadingPaymentDetails}</p>;
  }

  if (!order) {
    return <p className="text-red-500">{messages.orderNotFound}</p>;
  }

  const paymentInstructions = order.payment_instructions;

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{messages.completePaymentTitle}</h1>

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold border-b pb-3 mb-4">
          {messages.bankTransferInstructions}
        </h2>

        <div className="space-y-4 text-gray-700">
          <p>
            {messages.transferExactAmount}{" "}
            <span className="text-orange-600 font-bold">
              ${order.total.toFixed(2)}
            </span>{" "}
            {messages.toFollowingBankAccount}
          </p>

          {paymentInstructions ? (
            <div className="bg-gray-50 p-4 rounded-md font-mono text-sm border">
              <div>
                <strong>{messages.bankLabel}:</strong> {paymentInstructions.bank_name}
              </div>
              <div>
                <strong>{messages.accountNameLabel}:</strong>{" "}
                {paymentInstructions.account_name}
              </div>
              <div>
                <strong>{messages.accountNumberLabel}:</strong>{" "}
                {paymentInstructions.account_number}
              </div>
              <div className="mt-2 text-indigo-700 font-bold bg-indigo-50 p-2 inline-block rounded">
                {messages.memoLabel}: {order.payment_reference || `ORD-${order.id}`}
              </div>
              {paymentInstructions.note && (
                <p className="mt-3 font-sans text-sm text-gray-600">
                  {paymentInstructions.note}
                </p>
              )}
            </div>
          ) : (
            <div className="rounded-md border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
              {messages.paymentInstructionsUnavailable}
            </div>
          )}

          <p className="text-sm text-gray-500 italic mb-2">
            {messages.exactMemoWarning}
          </p>
        </div>
      </div>

      {order.status === "paid" || order.status === "delivered" ? (
        <div className="bg-green-50 border border-green-200 rounded p-4 text-green-800 text-center font-medium">
          {messages.paymentConfirmedPreparingOrder}
          <div className="mt-3">
            <Link
              href="/orders"
              className="text-sm border border-green-300 px-4 py-2 rounded bg-white hover:bg-green-100"
            >
              {messages.viewMyOrders}
            </Link>
          </div>
        </div>
      ) : order.buyer_marked_paid_at ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4 text-yellow-800 text-center">
          {messages.markedPaidOn}{" "}
          {new Date(order.buyer_marked_paid_at).toLocaleString()}.
          <br />
          <span className="text-sm mt-1 block">
            {messages.awaitingManualConfirmation}
          </span>
          <div className="mt-4">
            <Link
              href="/orders"
              className="text-sm border border-yellow-300 px-4 py-2 rounded bg-white hover:bg-yellow-100 transition"
            >
              {messages.returnToOrders}
            </Link>
          </div>
        </div>
      ) : (
        <button
          onClick={handleMarkPaid}
          disabled={submitting}
          className="w-full bg-orange-600 text-white py-3 rounded font-semibold hover:bg-orange-700 disabled:opacity-50"
        >
          {submitting ? messages.submitting : messages.iHavePaid}
        </button>
      )}
    </div>
  );
}
