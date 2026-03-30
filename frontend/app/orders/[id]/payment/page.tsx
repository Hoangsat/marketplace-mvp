"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { showToast } from "@/components/Toast";
import { Order } from "@/lib/types";
import Link from "next/link";

export default function OrderPaymentPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;
  
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!getToken()) { router.push("/login"); return; }
    if (!id) return;
    
    apiFetch<Order>(`/orders/${id}`)
      .then(setOrder)
      .catch((err) => {
        showToast(err instanceof Error ? err.message : "Failed to load order", "error");
        router.push("/orders");
      })
      .finally(() => setLoading(false));
  }, [id, router]);

  async function handleMarkPaid() {
    setSubmitting(true);
    try {
      const updatedOrder = await apiFetch<Order>(`/orders/${id}/confirm-payment`, {
        method: "POST"
      });
      setOrder(updatedOrder);
      showToast("Payment confirmed!", "success");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Failed to submit", "error");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p className="text-gray-500">Loading payment details...</p>;
  if (!order) return <p className="text-red-500">Order not found.</p>;

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Complete Payment</h1>
      
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold border-b pb-3 mb-4">Bank Transfer Instructions</h2>
        
        <div className="space-y-4 text-gray-700">
          <p>Please transfer exactly <span className="text-orange-600 font-bold">${order.total.toFixed(2)}</span> to the following bank account:</p>
          
          <div className="bg-gray-50 p-4 rounded-md font-mono text-sm border">
            <div><strong>Bank:</strong> Techcombank</div>
            <div><strong>Account Name:</strong> NGUYEN THI MAI LAN</div>
            <div><strong>Account Number:</strong> 19072620168019</div>
            <div className="mt-2 text-indigo-700 font-bold bg-indigo-50 p-2 inline-block rounded">
              MEMO / NỘI DUNG: {order.payment_reference || `ORD-${order.id}`}
            </div>
          </div>
          
          <p className="text-sm text-gray-500 italic mb-2">
            * Warning: You must include the EXACT MEMO above so we can identify your payment.
          </p>
        </div>
      </div>

      {order.status === "paid" || order.status === "delivered" ? (
        <div className="bg-green-50 border border-green-200 rounded p-4 text-green-800 text-center font-medium">
          ✅ Payment has been confirmed! We are preparing your order.
          <div className="mt-3">
            <Link href="/orders" className="text-sm border border-green-300 px-4 py-2 rounded bg-white hover:bg-green-100">
              View My Orders
            </Link>
          </div>
        </div>
      ) : order.buyer_marked_paid_at ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4 text-yellow-800 text-center">
          ⏳ You marked this as paid on {new Date(order.buyer_marked_paid_at).toLocaleString()}.<br/>
          <span className="text-sm mt-1 block">Order will be marked paid only after manual confirmation from our admins.</span>
          <div className="mt-4">
            <Link href="/orders" className="text-sm border border-yellow-300 px-4 py-2 rounded bg-white hover:bg-yellow-100 transition">
              Return to Orders
            </Link>
          </div>
        </div>
      ) : (
        <button
          onClick={handleMarkPaid}
          disabled={submitting}
          className="w-full bg-orange-600 text-white py-3 rounded font-semibold hover:bg-orange-700 disabled:opacity-50"
        >
          {submitting ? "Submitting..." : "I have paid"}
        </button>
      )}

    </div>
  );
}
