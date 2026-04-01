from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
import uuid

from django.core.files.storage import default_storage
from django.db.models import Case, IntegerField, ProtectedError, Q, Value, When
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAuthenticatedSeller
from .models import (
    Category,
    OfferType,
    Platform,
    Product,
    SearchAlias,
    filter_publicly_available_products,
    is_product_publicly_available,
    normalize_search_query,
)
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
SEARCH_PAGE_SIZE = 24


def _detail_response(message: str, status_code: int) -> Response:
    return Response({"detail": message}, status=status_code)


def _search_suggest_empty_response(query: str) -> Response:
    return Response(
        {
            "query": query,
            "categories": [],
            "search_terms": [],
        }
    )


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


def _category_has_active_platforms(category):
    if category is None:
        return False
    return Platform.objects.filter(category_id=category.id, is_active=True).exists()


def _category_queryset():
    return Category.objects.filter(parent__isnull=True)


def _display_platform_name(platform):
    return platform.display_name_vi or platform.name


def _display_offer_type_name(offer_type):
    return offer_type.display_name_vi or offer_type.name


def _rank_search_text(query, text, *, exact, startswith, contains):
    normalized_text = normalize_search_query(text)
    if not normalized_text:
        return None
    if normalized_text == query:
        return exact
    if normalized_text.startswith(query):
        return startswith
    if query in normalized_text:
        return contains
    return None


def _search_entity_score(query, values):
    scores = [
        _rank_search_text(query, value, exact=600, startswith=500, contains=400)
        for value in values
    ]
    scores = [score for score in scores if score is not None]
    return max(scores) if scores else None


def _search_alias_score(query, values):
    scores = [
        _rank_search_text(query, value, exact=550, startswith=450, contains=350)
        for value in values
    ]
    scores = [score for score in scores if score is not None]
    return max(scores) if scores else None


def _category_suggestion_item(category):
    slug = getattr(category, "slug", "")
    if not slug:
        return None
    return {
        "type": SearchAlias.EntityType.CATEGORY,
        "id": category.id,
        "label": category.name,
        "subtitle": None,
        "slug": slug,
        "image": None,
        "url": f"/categories/{slug}",
    }


def _platform_suggestion_item(platform):
    if platform is None:
        return None
    platform_slug = getattr(platform, "slug", "")
    if not platform_slug:
        return None
    return {
        "type": SearchAlias.EntityType.GAME,
        "id": platform.id,
        "label": _display_platform_name(platform),
        "subtitle": getattr(platform.category, "name", None),
        "slug": platform_slug,
        "image": None,
        "url": f"/catalog/{platform_slug}",
    }


def _offer_type_suggestion_item(offer_type):
    platform = getattr(offer_type, "platform", None)
    if platform is None:
        return None
    platform_slug = getattr(platform, "slug", "")
    offer_type_slug = getattr(offer_type, "slug", "")
    if not platform_slug or not offer_type_slug:
        return None
    platform_name = _display_platform_name(platform)
    return {
        "type": SearchAlias.EntityType.OFFER_TYPE,
        "id": offer_type.id,
        "label": _display_offer_type_name(offer_type),
        "subtitle": platform_name,
        "slug": offer_type_slug,
        "image": None,
        "url": f"/catalog/{platform_slug}/{offer_type_slug}",
    }


def _search_term_item(alias):
    return {
        "label": alias.query,
        "query": alias.query,
        "url": f"/search?{urlencode({'q': alias.query})}",
    }


def _safe_suggestion_item(builder, entity):
    try:
        return builder(entity)
    except Exception as exc:
        print("SearchSuggestView item mapping error:", exc)
        return None


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

        platforms = Platform.objects.filter(
            category_id=category.id,
            is_active=True,
        ).order_by("name", "id")
        return Response(PlatformSerializer(platforms, many=True).data)


class CategoryProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug):
        category = _category_queryset().filter(slug=category_slug).first()
        if not category:
            return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)

        products = filter_publicly_available_products(_catalog_product_queryset()).filter(
            category_id=category.id,
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


class SearchSuggestView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = normalize_search_query(request.query_params.get("q"))
        print("Suggest query:", query)
        if len(query) < 2:
            return _search_suggest_empty_response(query)

        try:
            categories = list(
                _category_queryset().filter(name__icontains=query).order_by("name", "id")[:24]
            )
            platforms = list(
                Platform.objects.select_related("category")
                .filter(is_active=True)
                .filter(Q(name__icontains=query) | Q(display_name_vi__icontains=query))
                .order_by("name", "id")[:24]
            )
            offer_types = list(
                OfferType.objects.select_related("platform", "platform__category")
                .filter(is_active=True)
                .filter(Q(name__icontains=query) | Q(display_name_vi__icontains=query))
                .order_by("name", "id")[:24]
            )
            try:
                aliases = list(
                    SearchAlias.objects.filter(
                        is_active=True,
                        normalized_query__contains=query,
                    )
                    .order_by("-weight", "query", "id")[:48]
                )
            except Exception as exc:
                print("SearchSuggestView alias error:", exc)
                aliases = []

            category_alias_ids = {
                alias.entity_id
                for alias in aliases
                if alias.entity_type == SearchAlias.EntityType.CATEGORY and alias.entity_id is not None
            }
            game_alias_ids = {
                alias.entity_id
                for alias in aliases
                if alias.entity_type == SearchAlias.EntityType.GAME and alias.entity_id is not None
            }
            offer_type_alias_ids = {
                alias.entity_id
                for alias in aliases
                if alias.entity_type == SearchAlias.EntityType.OFFER_TYPE and alias.entity_id is not None
            }

            category_map = {
                category.id: category
                for category in _category_queryset().filter(id__in=category_alias_ids)
            }
            platform_map = {
                platform.id: platform
                for platform in Platform.objects.select_related("category").filter(
                    id__in=game_alias_ids,
                    is_active=True,
                )
            }
            offer_type_map = {
                offer_type.id: offer_type
                for offer_type in OfferType.objects.select_related("platform", "platform__category").filter(
                    id__in=offer_type_alias_ids,
                    is_active=True,
                )
            }

            category_aliases_by_id = {}
            game_aliases_by_id = {}
            offer_type_aliases_by_id = {}
            search_term_aliases = []
            for alias in aliases:
                if alias.entity_type == SearchAlias.EntityType.CATEGORY and alias.entity_id in category_map:
                    category_aliases_by_id.setdefault(alias.entity_id, []).append(alias)
                elif alias.entity_type == SearchAlias.EntityType.GAME and alias.entity_id in platform_map:
                    game_aliases_by_id.setdefault(alias.entity_id, []).append(alias)
                elif (
                    alias.entity_type == SearchAlias.EntityType.OFFER_TYPE
                    and alias.entity_id in offer_type_map
                ):
                    offer_type_aliases_by_id.setdefault(alias.entity_id, []).append(alias)
                elif alias.entity_type == SearchAlias.EntityType.SEARCH_TERM:
                    search_term_aliases.append(alias)

            ranked_entities = {}
            for category in categories:
                item = _safe_suggestion_item(_category_suggestion_item, category)
                if not item:
                    continue
                ranked_entities[(SearchAlias.EntityType.CATEGORY, category.id)] = {
                    "item": item,
                    "score": _search_entity_score(query, [category.name]) or 0,
                    "weight": 0,
                }
            for platform in platforms:
                item = _safe_suggestion_item(_platform_suggestion_item, platform)
                if not item:
                    continue
                ranked_entities[(SearchAlias.EntityType.GAME, platform.id)] = {
                    "item": item,
                    "score": _search_entity_score(query, [platform.name, platform.display_name_vi]) or 0,
                    "weight": 0,
                }
            for offer_type in offer_types:
                item = _safe_suggestion_item(_offer_type_suggestion_item, offer_type)
                if not item:
                    continue
                ranked_entities[(SearchAlias.EntityType.OFFER_TYPE, offer_type.id)] = {
                    "item": item,
                    "score": _search_entity_score(query, [offer_type.name, offer_type.display_name_vi]) or 0,
                    "weight": 0,
                }

            alias_entity_sets = [
                (SearchAlias.EntityType.CATEGORY, category_map, category_aliases_by_id, _category_suggestion_item, lambda entity: [entity.name]),
                (SearchAlias.EntityType.GAME, platform_map, game_aliases_by_id, _platform_suggestion_item, lambda entity: [entity.name, entity.display_name_vi]),
                (SearchAlias.EntityType.OFFER_TYPE, offer_type_map, offer_type_aliases_by_id, _offer_type_suggestion_item, lambda entity: [entity.name, entity.display_name_vi]),
            ]
            for entity_type, entity_map, alias_map, serializer, text_values in alias_entity_sets:
                for entity_id, entity_aliases in alias_map.items():
                    entity = entity_map[entity_id]
                    alias_score = _search_alias_score(
                        query,
                        [alias.normalized_query for alias in entity_aliases],
                    )
                    if alias_score is None:
                        continue
                    item = _safe_suggestion_item(serializer, entity)
                    if not item:
                        continue
                    key = (entity_type, entity_id)
                    current = ranked_entities.get(key)
                    best_weight = max(alias.weight for alias in entity_aliases)
                    direct_score = _search_entity_score(query, text_values(entity)) or 0
                    candidate_score = max(direct_score, alias_score)
                    candidate = {
                        "item": current["item"] if current else item,
                        "score": candidate_score,
                        "weight": max(best_weight, current["weight"] if current else 0),
                    }
                    if (
                        current is None
                        or candidate["score"] > current["score"]
                        or (
                            candidate["score"] == current["score"]
                            and candidate["weight"] > current["weight"]
                        )
                    ):
                        ranked_entities[key] = candidate

            ranked_category_items = [
                value["item"]
                for value in sorted(
                    ranked_entities.values(),
                    key=lambda value: (
                        -value["score"],
                        -value["weight"],
                        value["item"]["label"].lower(),
                        value["item"]["id"],
                    ),
                )[:8]
            ]

            ranked_search_terms = []
            seen_search_queries = set()
            for alias in sorted(
                search_term_aliases,
                key=lambda alias: (
                    -(_search_alias_score(query, [alias.normalized_query]) or 0),
                    -alias.weight,
                    alias.query.lower(),
                    alias.id,
                ),
            ):
                normalized_alias_query = normalize_search_query(alias.query)
                if normalized_alias_query in seen_search_queries:
                    continue
                seen_search_queries.add(normalized_alias_query)
                ranked_search_terms.append(_search_term_item(alias))
                if len(ranked_search_terms) == 8:
                    break

            return Response(
                {
                    "query": query,
                    "categories": ranked_category_items,
                    "search_terms": ranked_search_terms,
                }
            )
        except Exception as exc:
            print("SearchSuggestView error:", exc)
            return _search_suggest_empty_response(query)


class SearchResultsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = normalize_search_query(request.query_params.get("q"))
        try:
            page = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            page = 1
        page = max(page, 1)

        if not query:
            return Response(
                {
                    "query": query,
                    "count": 0,
                    "page": page,
                    "page_size": SEARCH_PAGE_SIZE,
                    "has_more": False,
                    "results": [],
                }
            )

        products = filter_publicly_available_products(_catalog_product_queryset()).filter(
            stock__gt=0,
        )
        products = products.filter(
            Q(title__icontains=query)
            | Q(category__name__icontains=query)
            | Q(platform__name__icontains=query)
            | Q(platform__display_name_vi__icontains=query)
            | Q(offer_type__name__icontains=query)
            | Q(offer_type__display_name_vi__icontains=query)
        ).annotate(
            relevance=Case(
                When(title__iexact=query, then=Value(600)),
                When(title__istartswith=query, then=Value(500)),
                When(title__icontains=query, then=Value(400)),
                When(category__name__iexact=query, then=Value(300)),
                When(platform__name__iexact=query, then=Value(300)),
                When(platform__display_name_vi__iexact=query, then=Value(300)),
                When(offer_type__name__iexact=query, then=Value(300)),
                When(offer_type__display_name_vi__iexact=query, then=Value(300)),
                When(category__name__istartswith=query, then=Value(250)),
                When(platform__name__istartswith=query, then=Value(250)),
                When(platform__display_name_vi__istartswith=query, then=Value(250)),
                When(offer_type__name__istartswith=query, then=Value(250)),
                When(offer_type__display_name_vi__istartswith=query, then=Value(250)),
                default=Value(100),
                output_field=IntegerField(),
            )
        ).order_by("-relevance", "title", "id")

        count = products.count()
        start = (page - 1) * SEARCH_PAGE_SIZE
        end = start + SEARCH_PAGE_SIZE
        results = list(products[start:end])
        has_more = end < count

        return Response(
            {
                "query": query,
                "count": count,
                "page": page,
                "page_size": SEARCH_PAGE_SIZE,
                "has_more": has_more,
                "results": ProductSerializer(
                    results,
                    many=True,
                    context={"request": request},
                ).data,
            }
        )


class ProductCollectionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAuthenticatedSeller()]
        return [permissions.AllowAny()]

    def get(self, request):
        products = filter_publicly_available_products(_catalog_product_queryset()).filter(
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

        category = _resolve_create_category(serializer.validated_data, platform)
        if not category and "category_id" not in serializer.validated_data and not platform:
            return _detail_response(
                "Category is required", status.HTTP_400_BAD_REQUEST
            )
        if not category:
            return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)

        if "offer_type_id" in serializer.validated_data and not platform:
            return _detail_response("Platform is required", status.HTTP_400_BAD_REQUEST)

        offer_type = _resolve_active_offer_type(
            serializer.validated_data.get("offer_type_id"),
            platform=platform,
        )
        if "offer_type_id" in serializer.validated_data and not offer_type:
            return _detail_response(
                "Offer type not found", status.HTTP_404_NOT_FOUND
            )
        if not platform:
            if _category_has_active_platforms(category):
                return _detail_response("Platform is required", status.HTTP_400_BAD_REQUEST)
        if _platform_has_active_offer_types(platform) and not offer_type:
            return _detail_response(
                "Offer type is required for this platform",
                status.HTTP_400_BAD_REQUEST,
            )
        if platform and category and platform.category_id != category.id:
            return _detail_response(
                "Category does not match the selected platform",
                status.HTTP_400_BAD_REQUEST,
            )

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
        if not is_product_publicly_available(product):
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
        next_category = product.category
        next_platform = product.platform
        next_offer_type = product.offer_type

        if "platform_id" in validated or "game_id" in validated:
            next_platform, platform_error = _resolve_platform_from_data(validated)
            if platform_error:
                return _detail_response(platform_error, status.HTTP_400_BAD_REQUEST)
            resolved_platform_id = (
                validated.get("platform_id")
                if "platform_id" in validated
                else validated.get("game_id")
            )
            if resolved_platform_id is not None and not next_platform:
                return _detail_response("Platform not found", status.HTTP_404_NOT_FOUND)

        if next_platform:
            next_category = next_platform.category
        elif "category_id" in validated:
            next_category = _resolve_category(validated["category_id"])
            if not next_category:
                return _detail_response("Category not found", status.HTTP_404_NOT_FOUND)

        if "offer_type_id" in validated and validated.get("offer_type_id") is not None and not next_platform:
            return _detail_response("Platform is required", status.HTTP_400_BAD_REQUEST)

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
        if not next_platform and _category_has_active_platforms(next_category):
            return _detail_response("Platform is required", status.HTTP_400_BAD_REQUEST)

        product.category = next_category
        product.platform = next_platform
        product.offer_type = next_offer_type

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
