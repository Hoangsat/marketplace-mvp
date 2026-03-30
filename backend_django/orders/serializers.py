from rest_framework import serializers

from catalog.serializers import ProductSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "order_id",
            "product_id",
            "quantity",
            "price_at_purchase",
            "product",
        )


class OrderSerializer(serializers.ModelSerializer):
    buyer_id = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(allow_null=True, required=False)
    payment_provider = serializers.CharField(allow_null=True, required=False)
    payment_reference = serializers.CharField(allow_null=True, required=False)
    payment_confirmed_at = serializers.DateTimeField(allow_null=True, required=False)
    buyer_marked_paid_at = serializers.DateTimeField(allow_null=True, required=False)
    items = OrderItemSerializer(many=True, read_only=True)

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
            "created_at",
            "items",
        )


class CheckoutItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class CheckoutSerializer(serializers.Serializer):
    items = CheckoutItemSerializer(many=True)
