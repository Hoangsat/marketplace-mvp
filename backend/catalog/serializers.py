from rest_framework import serializers

from common.media import normalize_media_urls

from .models import Category, Game, OfferType, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "slug", "display_name_vi")


class OfferTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferType
        fields = ("id", "name", "slug", "display_name_vi")


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(read_only=True)
    images = serializers.SerializerMethodField()
    seller_id = serializers.IntegerField(read_only=True)
    category_id = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "price",
            "stock",
            "images",
            "seller_id",
            "category_id",
            "category",
        )

    def get_images(self, obj):
        request = self.context.get("request")
        return normalize_media_urls(obj.images or [], request=request)


class ProductCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock = serializers.IntegerField()
    category_id = serializers.IntegerField(required=False)
    game_id = serializers.IntegerField(required=False)
    offer_type_id = serializers.IntegerField(required=False)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value


class ProductUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=255)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    stock = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
