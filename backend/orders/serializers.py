from django.conf import settings
from rest_framework import serializers

from catalog.serializers import ProductSerializer
from common.media import normalize_media_url

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    price_at_purchase = serializers.FloatField(read_only=True)
    product = ProductSerializer(read_only=True)
    product_title = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "order_id",
            "product_id",
            "quantity",
            "price_at_purchase",
            "product_title",
            "product_image",
            "product",
        )

    def get_product_title(self, obj):
        return obj.product_title_snapshot or getattr(obj.product, "title", "")

    def get_product_image(self, obj):
        request = self.context.get("request")
        image_value = obj.product_image_snapshot
        if not image_value and getattr(obj.product, "images", None):
            image_value = obj.product.images[0]
        return normalize_media_url(image_value, request=request)


class OrderSerializer(serializers.ModelSerializer):
    buyer_id = serializers.IntegerField(read_only=True)
    total = serializers.FloatField(read_only=True)
    payment_method = serializers.CharField(allow_null=True, required=False)
    payment_provider = serializers.CharField(allow_null=True, required=False)
    payment_reference = serializers.CharField(allow_null=True, required=False)
    payment_confirmed_at = serializers.DateTimeField(allow_null=True, required=False)
    buyer_marked_paid_at = serializers.DateTimeField(allow_null=True, required=False)
    items = OrderItemSerializer(many=True, read_only=True)
    payment_instructions = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "buyer_id",
            "total",
            "status",
            "payment_method",
            "payment_provider",
            "payment_reference",
            "payment_confirmed_at",
            "buyer_marked_paid_at",
            "payment_instructions",
            "created_at",
            "items",
        )

    def get_payment_instructions(self, obj):
        if obj.payment_method != "manual_bank":
            return None

        bank_name = getattr(settings, "MANUAL_PAYMENT_BANK_NAME", "").strip()
        account_name = getattr(settings, "MANUAL_PAYMENT_ACCOUNT_NAME", "").strip()
        account_number = getattr(settings, "MANUAL_PAYMENT_ACCOUNT_NUMBER", "").strip()
        note = getattr(settings, "MANUAL_PAYMENT_NOTE", "").strip()

        if not bank_name and not account_name and not account_number and not note:
            return None

        return {
            "bank_name": bank_name,
            "account_name": account_name,
            "account_number": account_number,
            "note": note,
        }


class SellerDashboardOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    seller_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField()
    money_status = serializers.CharField()
    payout_status = serializers.CharField()


class SellerDashboardSerializer(serializers.Serializer):
    balance_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance_available = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance_paid_out = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = SellerDashboardOrderSerializer(many=True)


class SellerOrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    price_at_purchase = serializers.FloatField(read_only=True)
    product = ProductSerializer(read_only=True)
    seller_amount = serializers.FloatField(read_only=True)
    order_status = serializers.CharField(read_only=True)
    payout_status = serializers.CharField(read_only=True)
    product_title = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "order_id",
            "product_id",
            "quantity",
            "price_at_purchase",
            "seller_amount",
            "order_status",
            "payout_status",
            "product_title",
            "product_image",
            "product",
        )

    def get_product_title(self, obj):
        return obj.product_title_snapshot or getattr(obj.product, "title", "")

    def get_product_image(self, obj):
        request = self.context.get("request")
        image_value = obj.product_image_snapshot
        if not image_value and getattr(obj.product, "images", None):
            image_value = obj.product.images[0]
        return normalize_media_url(image_value, request=request)


class CheckoutItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class CheckoutSerializer(serializers.Serializer):
    items = CheckoutItemSerializer(many=True)
