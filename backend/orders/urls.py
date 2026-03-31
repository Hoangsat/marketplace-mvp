from django.urls import path

from .views import (
    AdminCancelOrderView,
    AdminConfirmPaymentView,
    BuyerCancelOrderView,
    BuyerOrderListView,
    CheckoutView,
    ConfirmPaymentView,
    MarkCompletedView,
    MarkDeliveredView,
    MarkPaymentSubmittedView,
    OrderDetailView,
    SellerDashboardView,
    SellerOrderItemListView,
)


urlpatterns = [
    path("orders/checkout", CheckoutView.as_view(), name="orders-checkout"),
    path("orders/buyer", BuyerOrderListView.as_view(), name="orders-buyer"),
    path("seller/dashboard", SellerDashboardView.as_view(), name="seller-dashboard"),
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
        "orders/<int:order_id>/mark-delivered",
        MarkDeliveredView.as_view(),
        name="orders-mark-delivered",
    ),
    path(
        "orders/<int:order_id>/mark-completed",
        MarkCompletedView.as_view(),
        name="orders-mark-completed",
    ),
    path(
        "orders/<int:order_id>/cancel",
        BuyerCancelOrderView.as_view(),
        name="orders-cancel",
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
