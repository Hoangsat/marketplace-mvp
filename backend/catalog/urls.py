from django.urls import path

from .views import (
    CategoryListView,
    ProductCollectionView,
    ProductDetailView,
    ProductImagesReplaceView,
    SellerProductListView,
)


urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("products", ProductCollectionView.as_view(), name="products-collection"),
    path("products/<int:product_id>", ProductDetailView.as_view(), name="products-detail"),
    path("products/<int:product_id>/images", ProductImagesReplaceView.as_view(), name="products-images"),
    path("seller/products", SellerProductListView.as_view(), name="seller-products"),
]
