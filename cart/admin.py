from django.contrib import admin
from .models import Cart, CartItem, Shipping, Order, Shipped, Delivered, Canceled
from store.models import Product  # ✅ Import Product model

# ======================= CART ADMIN ======================= #
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    inlines = [CartItemInline]

class ShippingAdmin(admin.ModelAdmin):
    list_display = ('charge',)
    list_editable = ('charge',)
    list_display_links = None
    # Prevent adding new Shipping instances, but allow editing
    def has_add_permission(self, request, obj=None):
        return False  # This will disable the ability to add new Shipping entries

admin.site.register(Shipping, ShippingAdmin)

# ======================= ORDER ADMIN ======================= #
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','product_details', 'total_price', 'status', 'order_date', 'order_time', 'address')
    list_filter = ('status', 'order_date')
    actions = ['mark_as_shipped', 'mark_as_canceled']

    def product_details(self, obj):
        return ", ".join([f"{name} ({qty})" for name, qty in obj.products.items()])
    product_details.short_description = "Products"
    def mark_as_shipped(self, request, queryset):
        for order in queryset.filter(status="pending"):
            Shipped.objects.create(
                user=order.user,
                products=order.products,
                total_price=order.total_price,
                shipping=order.shipping,
                address=order.address,
                status="shipped"
            )
            order.delete()  # ✅ Remove the order after shipping

    def mark_as_canceled(self, request, queryset):
        for order in queryset.filter(status="pending"):
            # ✅ Restore stock for each product in the order
            for product_name, quantity in order.products.items():
                try:
                    product = Product.objects.get(name=product_name)
                    product.quantity_available += quantity
                    product.save()
                except Product.DoesNotExist:
                    pass  # Product might have been deleted

            # ✅ Move order to Canceled table
            Canceled.objects.create(
                user=order.user,
                products=order.products,
                total_price=order.total_price,
                shipping=order.shipping,
                address=order.address,
            )
            order.delete()  # ✅ Remove the canceled order

    mark_as_shipped.short_description = "Mark selected orders as shipped"
    mark_as_canceled.short_description = "Cancel selected orders and restore stock"

# ======================= SHIPPED ADMIN ======================= #
@admin.register(Shipped)
class ShippedAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_details','total_price', 'status', 'shipped_date' ,'address')
    actions = ['mark_as_delivered', 'mark_as_canceled']

    def product_details(self, obj):
        return ", ".join([f"{name} ({qty})" for name, qty in obj.products.items()])
    product_details.short_description = "Products"
    def mark_as_delivered(self, request, queryset):
        for shipped in queryset.filter(status="shipped"):
            Delivered.objects.create(
                user=shipped.user,
                products=shipped.products,
                total_price=shipped.total_price,
                shipping=shipped.shipping,
                address=shipped.address,
            )
            shipped.delete()  # ✅ Remove the shipped order

    def mark_as_canceled(self, request, queryset):
        for shipped in queryset.filter(status="shipped"):
            # ✅ Restore stock for each product in the canceled shipped order
            for product_name, quantity in shipped.products.items():
                try:
                    product = Product.objects.get(name=product_name)
                    product.quantity_available += quantity
                    product.save()
                except Product.DoesNotExist:
                    pass  # Product might have been deleted

            Canceled.objects.create(
                user=shipped.user,
                products=shipped.products,
                total_price=shipped.total_price,
                shipping=shipped.shipping,
                address=shipped.address,
            )
            shipped.delete()  # ✅ Remove the shipped order

    mark_as_delivered.short_description = "Mark selected orders as delivered"
    mark_as_canceled.short_description = "Cancel selected orders and restore stock"

# ======================= DELIVERED ADMIN ======================= #
@admin.register(Delivered)
class DeliveredAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_details','total_price', 'delivered_date' ,  'address')

    def product_details(self, obj):
        return ", ".join([f"{name} ({qty})" for name, qty in obj.products.items()])
    product_details.short_description = "Products"
# ======================= CANCELED ADMIN ======================= #
@admin.register(Canceled)
class CanceledAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_details','total_price', 'canceled_date',  'address')

    def product_details(self, obj):
        return ", ".join([f"{name} ({qty})" for name, qty in obj.products.items()])
    product_details.short_description = "Products"

from django.contrib import admin
from django.contrib.auth.models import Group

# Unregister the Group model from the admin
admin.site.unregister(Group)
