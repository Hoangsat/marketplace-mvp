from django.contrib import admin
from django.utils import timezone

from .models import Order, OrderItem


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
    actions = ("mark_as_paid", "mark_as_shipped")
    list_select_related = ("buyer",)
    date_hierarchy = "created_at"

    @admin.action(description="Mark selected orders as paid")
    def mark_as_paid(self, request, queryset):
        queryset.update(
            status=Order.Status.PAID,
            payment_confirmed_at=timezone.now(),
        )

    @admin.action(description="Mark selected orders as shipped")
    def mark_as_shipped(self, request, queryset):
        queryset.update(status=Order.Status.DELIVERED)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price_at_purchase")
    search_fields = ("order__payment_reference", "order__buyer__email", "product__title")
    list_filter = ("order__status", "product__category")
    ordering = ("-id",)
    autocomplete_fields = ("order", "product")
