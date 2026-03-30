from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAuthenticatedSeller
from .models import Order, OrderItem
from .serializers import CheckoutSerializer, OrderItemSerializer, OrderSerializer
from .services import (
    OrderFlowError,
    cancel_order,
    confirm_order_payment,
    create_checkout_order,
    get_order_for_user,
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
        orders = (
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
            .exclude(order__status=Order.Status.PAYMENT_PENDING)
            .select_related("product__category", "order")
        )
        return Response(OrderItemSerializer(items, many=True).data)


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
    permission_classes = [permissions.IsAuthenticated]

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
            order = confirm_order_payment(order_id=order_id, current_user=request.user)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)


class AdminCancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = cancel_order(order_id=order_id)
        except OrderFlowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)
        return Response(OrderSerializer(order).data)
