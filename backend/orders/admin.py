from django.contrib import admin
from django.contrib import messages

from .models import Order, OrderItem, SellerTransaction
from django.utils import timezone

from .services import (
    OrderFlowError,
    confirm_order_payment,
    mark_seller_transaction_paid_out,
    release_order_funds,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "total", "status", "payment_method", "created_at")
    search_fields = ("buyer__email", "payment_reference", "payment_provider")
    list_filter = ("status", "created_at")
    ordering = ("-id",)
    autocomplete_fields = ("buyer",)
    inlines = [OrderItemInline]
    actions = ("mark_as_paid", "release_held_funds", "mark_as_shipped")
    list_select_related = ("buyer",)
    date_hierarchy = "created_at"

    @admin.action(description="Mark selected orders as paid")
    def mark_as_paid(self, request, queryset):
        confirmed_count = 0
        for order in queryset:
            try:
                confirm_order_payment(order_id=order.id)
                confirmed_count += 1
            except OrderFlowError as exc:
                self.message_user(request, str(exc.detail), level=messages.WARNING)
        if confirmed_count:
            self.message_user(
                request,
                f"Confirmed payment for {confirmed_count} order(s).",
                level=messages.SUCCESS,
            )

    @admin.action(description="Release held seller funds")
    def release_held_funds(self, request, queryset):
        released_count = 0
        for order in queryset:
            try:
                release_order_funds(order_id=order.id)
                released_count += 1
            except OrderFlowError as exc:
                self.message_user(request, str(exc.detail), level=messages.WARNING)
        if released_count:
            self.message_user(
                request,
                f"Released held funds for {released_count} order(s).",
                level=messages.SUCCESS,
            )

    @admin.action(description="Mark selected orders as shipped")
    def mark_as_shipped(self, request, queryset):
        updated_count = queryset.filter(status=Order.Status.PAID).update(
            status=Order.Status.DELIVERED,
            delivered_at=timezone.now(),
        )
        if updated_count:
            self.message_user(
                request,
                f"Marked {updated_count} paid order(s) as delivered.",
                level=messages.SUCCESS,
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price_at_purchase")
    search_fields = ("order__payment_reference", "order__buyer__email", "product__title")
    list_filter = ("order__status", "product__category")
    ordering = ("-id",)
    autocomplete_fields = ("order", "product")


@admin.register(SellerTransaction)
class SellerTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "seller",
        "order",
        "amount",
        "status",
        "paid_at",
        "created_at",
        "updated_at",
    )
    search_fields = ("seller__email", "order__payment_reference")
    list_filter = ("status", "created_at")
    ordering = ("-id",)
    autocomplete_fields = ("seller", "order")
    actions = ("mark_as_paid_out",)
    readonly_fields = (
        "seller",
        "order",
        "amount",
        "status",
        "paid_at",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Mark selected seller transactions as paid out")
    def mark_as_paid_out(self, request, queryset):
        paid_out_count = 0
        for seller_transaction in queryset:
            try:
                mark_seller_transaction_paid_out(
                    seller_transaction_id=seller_transaction.id
                )
                paid_out_count += 1
            except OrderFlowError as exc:
                self.message_user(request, str(exc.detail), level=messages.WARNING)
        if paid_out_count:
            self.message_user(
                request,
                f"Marked {paid_out_count} seller transaction(s) as paid out.",
                level=messages.SUCCESS,
            )
