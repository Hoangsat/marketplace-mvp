from decimal import Decimal

from django.db.models import Prefetch
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAuthenticatedSeller
from .models import Order, OrderItem, SellerTransaction
from .serializers import (
    CheckoutSerializer,
    OrderItemSerializer,
    OrderSerializer,
    SellerDashboardSerializer,
)
from .services import (
    OrderFlowError,
    auto_complete_delivered_orders,
    cancel_order,
    confirm_order_payment,
    create_checkout_order,
    get_order_for_user,
    mark_order_completed,
    mark_order_delivered,
    mark_payment_submitted,
)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            detail = next(iter(serializer.errors.values()))[0]
            if isinstance(detail, dict):
                detail = next(iter(detail.values()))[0]
            return Response({"detail": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = create_checkout_order(
                buyer=request.user,
                items=serializer.validated_data["items"],
            )
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class BuyerOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = auto_complete_delivered_orders(
            Order.objects.filter(buyer_id=request.user.id)
            .prefetch_related("items__product__category")
            .select_related("buyer")
            .order_by("-created_at")
        )
        return Response(OrderSerializer(orders, many=True).data)


class SellerOrderItemListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedSeller]

    def get(self, request):
        items = (
            OrderItem.objects.filter(product__seller_id=request.user.id)
            .exclude(order__status=Order.Status.PENDING)
            .select_related("product__category", "order")
        )
        return Response(OrderItemSerializer(items, many=True).data)


class SellerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedSeller]

    def get(self, request):
        current_user = request.user.__class__.objects.get(pk=request.user.pk)
        orders = auto_complete_delivered_orders(
            Order.objects.filter(items__product__seller_id=request.user.id)
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.filter(product__seller_id=request.user.id),
                ),
                Prefetch(
                    "seller_transactions",
                    queryset=SellerTransaction.objects.filter(seller_id=request.user.id),
                ),
            )
            .distinct()
            .order_by("-created_at")
        )

        order_data = []
        for order in orders:
            seller_total = Decimal("0.00")
            for item in order.items.all():
                seller_total += Decimal(str(item.price_at_purchase)) * Decimal(
                    item.quantity
                )

            seller_transaction = next(iter(order.seller_transactions.all()), None)
            if seller_transaction and seller_transaction.status == SellerTransaction.Status.AVAILABLE:
                money_status = "available"
            elif seller_transaction and seller_transaction.status == SellerTransaction.Status.HOLD:
                money_status = "on_hold"
            elif order.status == Order.Status.CANCELLED:
                money_status = "cancelled"
            else:
                money_status = "pending"

            order_data.append(
                {
                    "id": order.id,
                    "created_at": order.created_at,
                    "total": seller_total,
                    "status": order.status,
                    "money_status": money_status,
                }
            )

        serializer = SellerDashboardSerializer(
            {
                "balance_pending": current_user.balance_pending,
                "balance_available": current_user.balance_available,
                "orders": order_data,
            }
        )
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = get_order_for_user(order_id=order_id, current_user=request.user)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)


class MarkPaymentSubmittedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = mark_payment_submitted(order_id=order_id, current_user=request.user)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)


class AdminConfirmPaymentView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, order_id):
        try:
            order = confirm_order_payment(order_id=order_id)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)


class ConfirmPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = mark_payment_submitted(order_id=order_id, current_user=request.user)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)


class MarkDeliveredView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedSeller]

    def post(self, request, order_id):
        try:
            order = mark_order_delivered(order_id=order_id, current_user=request.user)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)


class MarkCompletedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = mark_order_completed(order_id=order_id, current_user=request.user)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)


class AdminCancelOrderView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, order_id):
        try:
            order = cancel_order(order_id=order_id)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)
