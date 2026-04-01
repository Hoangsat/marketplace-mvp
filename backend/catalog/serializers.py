from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from common.media import normalize_media_urls

from .models import Category, OfferType, Platform, Product


class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent_id",
            "is_featured_home",
            "featured_rank",
        )


class CategoryDetailSerializer(CategorySerializer):
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields


class PlatformSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Platform
        fields = ("id", "name", "slug", "display_name_vi", "category_id")


class PlatformDetailSerializer(PlatformSerializer):
    has_offer_types = serializers.SerializerMethodField()
    offer_types = serializers.SerializerMethodField()

    class Meta(PlatformSerializer.Meta):
        fields = PlatformSerializer.Meta.fields + ("has_offer_types", "offer_types")

    def get_has_offer_types(self, obj):
        if hasattr(obj, "active_offer_type_count"):
            return obj.active_offer_type_count > 0
        return obj.offer_types.filter(is_active=True).exists()

    def get_offer_types(self, obj):
        offer_types = getattr(obj, "active_offer_types", None)
        if offer_types is None:
            offer_types = obj.offer_types.filter(is_active=True).order_by("name", "id")
        return OfferTypeSerializer(offer_types, many=True).data


class OfferTypeSerializer(serializers.ModelSerializer):
    platform_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = OfferType
        fields = ("id", "name", "slug", "display_name_vi", "platform_id")


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(read_only=True)
    images = serializers.SerializerMethodField()
    seller_id = serializers.IntegerField(read_only=True)
    seller_nickname = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(read_only=True)
    platform_id = serializers.IntegerField(read_only=True)
    offer_type_id = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    platform = PlatformSerializer(read_only=True)
    offer_type = OfferTypeSerializer(read_only=True)

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
            "seller_nickname",
            "category_id",
            "platform_id",
            "offer_type_id",
            "category",
            "platform",
            "offer_type",
        )

    def get_images(self, obj):
        request = self.context.get("request")
        return normalize_media_urls(obj.images or [], request=request)

    def get_seller_nickname(self, obj):
        seller = getattr(obj, "seller", None)
        if seller is None:
            return "Seller"

        try:
            nickname = seller.profile.nickname
        except ObjectDoesNotExist:
            nickname = None

        if isinstance(nickname, str) and nickname.strip():
            return nickname.strip()

        username = getattr(seller, "username", "")
        if isinstance(username, str) and username.strip():
            return username.strip()

        return "Seller"


class ProductCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock = serializers.IntegerField()
    category_id = serializers.IntegerField(required=False)
    platform_id = serializers.IntegerField(required=False)
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
    platform_id = serializers.IntegerField(required=False, allow_null=True)
    game_id = serializers.IntegerField(required=False, allow_null=True)
    offer_type_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value


# Temporary alias for compatibility while the frontend/backend move away from game naming.
GameSerializer = PlatformSerializer
