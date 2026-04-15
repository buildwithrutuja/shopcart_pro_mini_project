from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Product, Cart, CartItem, Coupon,
                     Order, OrderItem, Transaction, Review, UserProfile)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'line_total']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    list_editable = ['price', 'stock', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'subtotal', 'created_at']
    readonly_fields = ['user', 'created_at', 'updated_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'is_active', 'valid_until']
    list_editable = ['is_active']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status']
    list_editable = ['status', 'payment_status']
    search_fields = ['order_number', 'user__username', 'email']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'transaction_type']
    search_fields = ['transaction_id', 'order__order_number']
    readonly_fields = ['transaction_id', 'created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'created_at']
    list_filter = ['rating']
    search_fields = ['product__name', 'user__username']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'is_customer', 'created_at']
    search_fields = ['user__username', 'user__email']


admin.site.site_header = "ShopCart Pro Admin"
admin.site.site_title = "ShopCart Pro"
admin.site.index_title = "Store Management"
