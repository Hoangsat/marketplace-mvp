from decimal import Decimal, InvalidOperation
import uuid

from django.core.files.storage import default_storage
from django.db.models import ProtectedError
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAuthenticatedSeller
from .models import Category, Game, OfferType, Product
from .serializers import (
    CategorySerializer,
    GameSerializer,
    OfferTypeSerializer,
    ProductCreateSerializer,
    ProductSerializer,
    ProductUpdateSerializer,
)


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_IMAGES_PER_PRODUCT = 5
GAMES_CATEGORY_NAME = "Games"


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


def _resolve_active_game(game_id):
    if game_id is None:
        return None
    return Game.objects.filter(id=game_id, is_active=True).first()


def _resolve_active_offer_type(offer_type_id):
    if offer_type_id is None:
        return None
    return OfferType.objects.filter(id=offer_type_id, is_active=True).first()


def _resolve_create_category(validated_data, game, offer_type):
    if game and offer_type:
        games_category = Category.objects.filter(
            name__iexact=GAMES_CATEGORY_NAME
        ).first()
        if games_category:
            return games_category

    category_id = validated_data.get("category_id")
    if category_id is None:
        return None
    return Category.objects.filter(id=category_id).first()


class CategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = Category.objects.all().order_by("id")
        return Response(CategorySerializer(categories, many=True).data)


class GameListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        games = Game.objects.filter(is_active=True).order_by("id")
        return Response(GameSerializer(games, many=True).data)


class OfferTypeListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        offer_types = OfferType.objects.filter(is_active=True).order_by("id")
        return Response(OfferTypeSerializer(offer_types, many=True).data)


class ProductCollectionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAuthenticatedSeller()]
        return [permissions.AllowAny()]

    def get(self, request):
        products = Product.objects.select_related(
            "category", "seller", "seller__profile"
        ).filter(
            is_active=True,
            stock__gt=0,
        )

        search = request.query_params.get("search")
        category_id = request.query_params.get("category_id")
        game_slug = request.query_params.get("game")
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
        if game_slug:
            products = products.filter(game__slug=game_slug, game__is_active=True)
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

        game = _resolve_active_game(serializer.validated_data.get("game_id"))
        if "game_id" in serializer.validated_data and not game:
            return _detail_response("Game not found", status.HTTP_404_NOT_FOUND)

        offer_type = _resolve_active_offer_type(
            serializer.validated_data.get("offer_type_id")
        )
        if "offer_type_id" in serializer.validated_data and not offer_type:
            return _detail_response(
                "Offer type not found", status.HTTP_404_NOT_FOUND
            )

        category = _resolve_create_category(
            serializer.validated_data,
            game,
            offer_type,
        )
        if not category and "category_id" not in serializer.validated_data:
            return _detail_response(
                "Category is required", status.HTTP_400_BAD_REQUEST
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
            game=game,
            offer_type=offer_type,
            seller=request.user,
            images=image_paths,
        )
        product = Product.objects.select_related(
            "category", "seller", "seller__profile"
        ).get(pk=product.pk)
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
        product = Product.objects.select_related(
            "category", "seller", "seller__profile"
        ).filter(id=product_id).first()
        if not product:
            return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        if not product.is_active:
            if not request.user.is_authenticated or product.seller_id != request.user.id:
                return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product, context={"request": request}).data)

    def put(self, request, product_id):
        product = Product.objects.select_related("category").filter(id=product_id).first()
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
        if "category_id" in validated:
            category = Category.objects.filter(id=validated["category_id"]).first()
            if not category:
                return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)
            product.category = category

        for field in ("title", "description", "price", "stock"):
            if field in validated:
                setattr(product, field, validated[field])

        product.save()
        product.refresh_from_db()
        product = Product.objects.select_related(
            "category", "seller", "seller__profile"
        ).get(pk=product.pk)
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
        products = Product.objects.select_related("category").filter(
            seller_id=request.user.id,
            is_active=True,
        )
        return Response(
            ProductSerializer(products, many=True, context={"request": request}).data
        )
