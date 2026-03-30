from django.urls import path

from .views import (
    AdminCancelOrderView,
    AdminConfirmPaymentView,
    BuyerOrderListView,
    CheckoutView,
    ConfirmPaymentView,
    MarkPaymentSubmittedView,
    OrderDetailView,
    SellerOrderItemListView,
)


urlpatterns = [
    path("orders/checkout", CheckoutView.as_view(), name="orders-checkout"),
    path("orders/buyer", BuyerOrderListView.as_view(), name="orders-buyer"),
    path("orders/seller", SellerOrderItemListView.as_view(), name="orders-seller"),
    path("orders/<int:order_id>", OrderDetailView.as_view(), name="orders-detail"),
    path(
        "orders/<int:order_id>/mark-payment-submitted",
        MarkPaymentSubmittedView.as_view(),
        name="orders-mark-payment-submitted",
    ),
    path(
        "orders/<int:order_id>/confirm-payment",
        ConfirmPaymentView.as_view(),
        name="orders-confirm-payment",
    ),
    path(
        "admin/orders/<int:order_id>/confirm-payment",
        AdminConfirmPaymentView.as_view(),
        name="admin-orders-confirm-payment",
    ),
    path(
        "admin/orders/<int:order_id>/cancel",
        AdminCancelOrderView.as_view(),
        name="admin-orders-cancel",
    ),
]
