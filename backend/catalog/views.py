import os
import uuid

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAuthenticatedSeller
from .models import Category, Product
from .serializers import (
    CategorySerializer,
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

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
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
        dest_path = os.path.join(settings.MEDIA_ROOT, unique_name)
        with open(dest_path, "wb") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        saved_paths.append(f"{settings.MEDIA_URL}{unique_name}")

    return saved_paths


class CategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = Category.objects.all().order_by("id")
        return Response(CategorySerializer(categories, many=True).data)


class ProductCollectionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAuthenticatedSeller()]
        return [permissions.AllowAny()]

    def get(self, request):
        products = Product.objects.select_related("category")

        search = request.query_params.get("search")
        category_id = request.query_params.get("category_id")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if search:
            products = products.filter(title__icontains=search)
        if category_id:
            products = products.filter(category_id=category_id)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _detail_response(
                _first_error(serializer.errors), status.HTTP_400_BAD_REQUEST
            )

        category = Category.objects.filter(
            id=serializer.validated_data["category_id"]
        ).first()
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
            seller=request.user,
            images=image_paths,
        )
        product = Product.objects.select_related("category").get(pk=product.pk)
        return Response(
            ProductSerializer(product).data,
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
        product = Product.objects.select_related("category").filter(id=product_id).first()
        if not product:
            return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product).data)

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
        product = Product.objects.select_related("category").get(pk=product.pk)
        return Response(ProductSerializer(product).data)

    def delete(self, request, product_id):
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return _detail_response("Product not found", status.HTTP_404_NOT_FOUND)
        if product.seller_id != request.user.id:
            return _detail_response("Not your product", status.HTTP_403_FORBIDDEN)

        product.delete()
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
        return Response(ProductSerializer(product).data)


class SellerProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedSeller]

    def get(self, request):
        products = Product.objects.select_related("category").filter(
            seller_id=request.user.id
        )
        return Response(ProductSerializer(products, many=True).data)
