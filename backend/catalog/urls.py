from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryFeaturedListView,
    CategoryListView,
    CategoryPlatformListView,
    CategoryProductsView,
    CategoryTopListView,
    GameListView,
    OfferTypeListView,
    PlatformDetailView,
    PlatformListView,
    ProductCollectionView,
    ProductDetailView,
    ProductImagesReplaceView,
    SearchResultsView,
    SearchSuggestView,
    SellerProductListView,
)


urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("games", GameListView.as_view(), name="games"),
    path("platforms", PlatformListView.as_view(), name="platforms"),
    path("platforms/<slug:platform_slug>", PlatformDetailView.as_view(), name="platform-detail"),
    path("offer-types", OfferTypeListView.as_view(), name="offer-types"),
    path("products", ProductCollectionView.as_view(), name="products-collection"),
    path("products/<int:product_id>", ProductDetailView.as_view(), name="products-detail"),
    path("products/<int:product_id>/images", ProductImagesReplaceView.as_view(), name="products-images"),
    path("seller/products", SellerProductListView.as_view(), name="seller-products"),
    path("api/search", SearchResultsView.as_view(), name="search-results"),
    path("api/search/suggest", SearchSuggestView.as_view(), name="search-suggest"),
    path("api/catalog/categories/top", CategoryTopListView.as_view(), name="catalog-categories-top"),
    path(
        "api/catalog/categories/featured",
        CategoryFeaturedListView.as_view(),
        name="catalog-categories-featured",
    ),
    path(
        "api/catalog/categories/<slug:category_slug>",
        CategoryDetailView.as_view(),
        name="catalog-category-detail",
    ),
    path(
        "api/catalog/categories/<slug:category_slug>/platforms",
        CategoryPlatformListView.as_view(),
        name="catalog-category-platforms",
    ),
    path(
        "api/catalog/categories/<slug:category_slug>/products",
        CategoryProductsView.as_view(),
        name="catalog-category-products",
    ),
]
