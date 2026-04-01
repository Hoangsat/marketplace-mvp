from decimal import Decimal, InvalidOperation
import uuid

from django.core.files.storage import default_storage
from django.db.models import Count, ProtectedError, Q
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAuthenticatedSeller
from .models import Category, OfferType, Platform, Product
from .serializers import (
    CategoryDetailSerializer,
    CategorySerializer,
    OfferTypeSerializer,
    PlatformDetailSerializer,
    PlatformSerializer,
    ProductCreateSerializer,
    ProductSerializer,
    ProductUpdateSerializer,
)


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_IMAGES_PER_PRODUCT = 5


def _detail_response(message: str, status_code: int) -> Response:
    return Response({"detail": message}, status=status_code)


def _first_error(errors) -> str:
    if isinstance(errors, dict):
        first_value = next(iter(errors.values()), ["Invalid input"])
        if isinstance(first_value, list) and first_value:
            return str(first_value[0])
        if isinstance(first_value, dict):
            return _first_error(first_value)
        return str(first_value)
    return "Invalid input"


def _save_images(files) -> list[str]:
    if len(files) > MAX_IMAGES_PER_PRODUCT:
        raise ValueError(f"Maximum {MAX_IMAGES_PER_PRODUCT} images allowed")

    saved_paths: list[str] = []
    for file in files:
        filename = getattr(file, "name", "")
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File '{filename}' is not allowed. Use jpg, jpeg, or png."
            )
        if file.size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File '{filename}' exceeds 5MB limit")

        unique_name = f"{uuid.uuid4().hex}.{ext}"
        storage_name = default_storage.save(f"uploads/{unique_name}", file)
        saved_paths.append(storage_name)

    return saved_paths


def _catalog_product_queryset():
    return Product.objects.select_related(
        "category",
        "platform",
        "platform__category",
        "offer_type",
        "seller",
        "seller__profile",
    )


def _resolve_category(category_id):
    if category_id is None:
        return None
    return Category.objects.filter(id=category_id, parent__isnull=True).first()


def _resolve_active_platform(platform_id):
    if platform_id is None:
        return None
    return Platform.objects.select_related("category").filter(
        id=platform_id,
        is_active=True,
    ).first()


def _resolve_platform_from_data(validated_data):
    platform_id = validated_data.get("platform_id")
    game_id = validated_data.get("game_id")

    if platform_id is not None and game_id is not None and platform_id != game_id:
        return None, "Platform selection is inconsistent"

    resolved_id = platform_id if platform_id is not None else game_id
    return _resolve_active_platform(resolved_id), None


def _resolve_active_offer_type(offer_type_id, platform=None):
    if offer_type_id is None:
        return None

    queryset = OfferType.objects.filter(id=offer_type_id, is_active=True)
    if platform is not None:
        queryset = queryset.filter(platform_id=platform.id)
    return queryset.first()


def _platform_has_active_offer_types(platform):
    if platform is None:
        return False
    if hasattr(platform, "active_offer_type_count"):
        return platform.active_offer_type_count > 0
    return platform.offer_types.filter(is_active=True).exists()


def _resolve_create_category(validated_data, platform):
    if platform and platform.category_id:
        return platform.category

    category_id = validated_data.get("category_id")
    if category_id is None:
        return None
    return _resolve_category(category_id)


def _category_queryset():
    return Category.objects.filter(parent__isnull=True)


class CategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = _category_queryset().order_by("name", "id")
        return Response(CategorySerializer(categories, many=True).data)


class CategoryTopListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = _category_queryset().order_by(
            "-is_featured_home",
            "featured_rank",
            "name",
            "id",
        )
        return Response(CategorySerializer(categories, many=True).data)


class CategoryFeaturedListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = _category_queryset().filter(is_featured_home=True).order_by(
            "featured_rank",
            "name",
            "id",
        )
        return Response(CategorySerializer(categories, many=True).data)


class CategoryDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug):
        category = _category_queryset().filter(slug=category_slug).first()
        if not category:
            return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)
        return Response(CategoryDetailSerializer(category).data)


class CategoryPlatformListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug):
        category = _category_queryset().filter(slug=category_slug).first()
        if not category:
            return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)

        platforms = (
            Platform.objects.filter(category_id=category.id, is_active=True)
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__is_active=True, products__stock__gt=0),
                )
            )
            .filter(product_count__gt=0)
            .order_by("name", "id")
        )
        return Response(PlatformSerializer(platforms, many=True).data)


class CategoryProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug):
        category = _category_queryset().filter(slug=category_slug).first()
        if not category:
            return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)

        products = _catalog_product_queryset().filter(
            category_id=category.id,
            is_active=True,
            stock__gt=0,
        )
        return Response(
            ProductSerializer(products, many=True, context={"request": request}).data
        )


class PlatformListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        category_slug = request.query_params.get("category")
        queryset = Platform.objects.select_related("category").filter(is_active=True)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        platforms = queryset.order_by("name", "id")
        return Response(PlatformSerializer(platforms, many=True).data)


class GameListView(PlatformListView):
    pass


class PlatformDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, platform_slug):
        platform = (
            Platform.objects.select_related("category")
            .prefetch_related("offer_types")
            .filter(
            slug=platform_slug,
            is_active=True,
            )
            .first()
        )
        if not platform:
            return _detail_response("Platform not found", status.HTTP_404_NOT_FOUND)
        active_offer_types = list(
            platform.offer_types.filter(is_active=True).order_by("name", "id")
        )
        platform.active_offer_types = active_offer_types
        platform.active_offer_type_count = len(active_offer_types)
        return Response(PlatformDetailSerializer(platform).data)


class OfferTypeListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        platform_slug = request.query_params.get("platform") or request.query_params.get(
            "game"
        )
        platform_id = request.query_params.get("platform_id") or request.query_params.get(
            "game_id"
        )

        offer_types = OfferType.objects.select_related("platform").filter(is_active=True)

        if platform_slug:
            offer_types = offer_types.filter(platform__slug=platform_slug)
        elif platform_id:
            offer_types = offer_types.filter(platform_id=platform_id)

        return Response(
            OfferTypeSerializer(offer_types.order_by("name", "id"), many=True).data
        )


class ProductCollectionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAuthenticatedSeller()]
        return [permissions.AllowAny()]

    def get(self, request):
        products = _catalog_product_queryset().filter(
            is_active=True,
            stock__gt=0,
        )

        search = request.query_params.get("search")
        category_id = request.query_params.get("category_id")
        platform_slug = request.query_params.get("platform") or request.query_params.get(
            "game"
        )
        offer_type_slug = request.query_params.get("offer_type")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        try:
            if category_id:
                category_id = int(category_id)
            if min_price not in (None, ""):
                min_price = Decimal(min_price)
            else:
                min_price = None
            if max_price not in (None, ""):
                max_price = Decimal(max_price)
            else:
                max_price = None
        except (TypeError, ValueError, InvalidOperation):
            return _detail_response("Invalid filter value", status.HTTP_400_BAD_REQUEST)

        if search:
            products = products.filter(title__icontains=search)
        if category_id:
            products = products.filter(category_id=category_id)
        if platform_slug:
            products = products.filter(
                platform__slug=platform_slug,
                platform__is_active=True,
            )
        if offer_type_slug:
            products = products.filter(
                offer_type__slug=offer_type_slug,
                offer_type__is_active=True,
            )
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        return Response(
            ProductSerializer(products, many=True, context={"request": request}).data
        )

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _detail_response(
                _first_error(serializer.errors), status.HTTP_400_BAD_REQUEST
            )

        platform, platform_error = _resolve_platform_from_data(serializer.validated_data)
        if platform_error:
            return _detail_response(platform_error, status.HTTP_400_BAD_REQUEST)
        if (
            "platform_id" in serializer.validated_data
            or "game_id" in serializer.validated_data
        ) and not platform:
            return _detail_response("Platform not found", status.HTTP_404_NOT_FOUND)

        offer_type = _resolve_active_offer_type(
            serializer.validated_data.get("offer_type_id"),
            platform=platform,
        )
        if "offer_type_id" in serializer.validated_data and not offer_type:
            return _detail_response(
                "Offer type not found", status.HTTP_404_NOT_FOUND
            )
        if not platform:
            return _detail_response("Platform is required", status.HTTP_400_BAD_REQUEST)
        if _platform_has_active_offer_types(platform) and not offer_type:
            return _detail_response(
                "Offer type is required for this platform",
                status.HTTP_400_BAD_REQUEST,
            )

        category = _resolve_create_category(serializer.validated_data, platform)
        if not category and "category_id" not in serializer.validated_data and not platform:
            return _detail_response(
                "Category is required", status.HTTP_400_BAD_REQUEST
            )
        if platform and category and platform.category_id != category.id:
            return _detail_response(
                "Category does not match the selected platform",
                status.HTTP_400_BAD_REQUEST,
            )
        if not category:
            return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist("images")
        try:
            image_paths = _save_images(files) if files else []
        except ValueError as exc:
            return _detail_response(str(exc), status.HTTP_400_BAD_REQUEST)

        product = Product.objects.create(
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
            price=serializer.validated_data["price"],
            stock=serializer.validated_data["stock"],
            category=category,
            platform=platform,
            offer_type=offer_type,
            seller=request.user,
            images=image_paths,
        )
        product = _catalog_product_queryset().get(pk=product.pk)
        return Response(
            ProductSerializer(product, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]

    def get_permissions(self):
        if self.request.method in {"PUT", "DELETE"}:
            return [permissions.IsAuthenticated(), IsAuthenticatedSeller()]
        return [permissions.AllowAny()]

    def get(self, request, product_id):
        product = _catalog_product_queryset().filter(id=product_id).first()
        if not product:
            return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        if not product.is_active:
            if not request.user.is_authenticated or product.seller_id != request.user.id:
                return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product, context={"request": request}).data)

    def put(self, request, product_id):
        product = _catalog_product_queryset().filter(id=product_id).first()
        if not product:
            return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        if product.seller_id != request.user.id:
            return _detail_response("Not your product", status.HTTP_403_FORBIDDEN)

        serializer = ProductUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _detail_response(
                _first_error(serializer.errors), status.HTTP_400_BAD_REQUEST
            )

        validated = serializer.validated_data
        next_platform = product.platform
        next_offer_type = product.offer_type

        if "platform_id" in validated or "game_id" in validated:
            next_platform, platform_error = _resolve_platform_from_data(validated)
            if platform_error:
                return _detail_response(platform_error, status.HTTP_400_BAD_REQUEST)
            if not next_platform:
                return _detail_response("Platform not found", status.HTTP_404_NOT_FOUND)

        if "offer_type_id" in validated:
            next_offer_type = _resolve_active_offer_type(
                validated.get("offer_type_id"),
                platform=next_platform,
            )
            if validated.get("offer_type_id") is not None and not next_offer_type:
                return _detail_response("Offer type not found", status.HTTP_404_NOT_FOUND)
        elif (
            ("platform_id" in validated or "game_id" in validated)
            and next_offer_type
            and next_offer_type.platform_id != getattr(next_platform, "id", None)
        ):
            next_offer_type = None

        if next_platform and _platform_has_active_offer_types(next_platform) and not next_offer_type:
            return _detail_response(
                "Offer type is required for this platform",
                status.HTTP_400_BAD_REQUEST,
            )

        product.platform = next_platform
        product.offer_type = next_offer_type
        if product.platform_id:
            product.category = product.platform.category
        elif "category_id" in validated:
            category = _resolve_category(validated["category_id"])
            if not category:
                return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)
            product.category = category

        for field in ("title", "description", "price", "stock"):
            if field in validated:
                setattr(product, field, validated[field])

        product.save()
        product.refresh_from_db()
        product = _catalog_product_queryset().get(pk=product.pk)
        return Response(ProductSerializer(product, context={"request": request}).data)

    def delete(self, request, product_id):
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        if product.seller_id != request.user.id:
            return _detail_response("Not your product", status.HTTP_403_FORBIDDEN)

        try:
            product.delete()
        except ProtectedError:
            product.is_active = False
            product.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImagesReplaceView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedSeller]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, product_id):
        product = Product.objects.select_related("category").filter(id=product_id).first()
        if not product:
            return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        if product.seller_id != request.user.id:
            return _detail_response("Not your product", status.HTTP_403_FORBIDDEN)

        files = request.FILES.getlist("images")
        if not files:
            return _detail_response("No images uploaded", status.HTTP_400_BAD_REQUEST)

        try:
            product.images = _save_images(files)
        except ValueError as exc:
            return _detail_response(str(exc), status.HTTP_400_BAD_REQUEST)

        product.save(update_fields=["images"])
        return Response(ProductSerializer(product, context={"request": request}).data)


class SellerProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedSeller]

    def get(self, request):
        products = _catalog_product_queryset().filter(
            seller_id=request.user.id,
            is_active=True,
        )
        return Response(
            ProductSerializer(products, many=True, context={"request": request}).data
        )
