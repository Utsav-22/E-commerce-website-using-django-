from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Category, SubCategory, Product, ProductImage, SliderImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "subcategory", "price", "quantity_available", "best_selling")
    list_filter = ("category", "subcategory", "best_selling")
    search_fields = ("name", "description", "category__name", "subcategory__name")
    inlines = [ProductImageInline]  

    def save_model(self, request, obj, form, change):
        """
        Ensures `old_price` and `discount` are properly calculated before saving.
        """
        if not obj.old_price or obj.old_price <= obj.price:
            obj.old_price = None  
            obj.discount = None  

        obj.save()

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Category, SubCategory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def has_delete_permission(self, request, obj=None):
        """ Prevent deletion if the category has subcategories or products. """
        if obj:  # When deleting a single category
            if obj.subcategories.exists():
                messages.error(request, f"Cannot delete category '{obj.name}' because it has associated subcategories.")
                return False
            if obj.products.exists():
                messages.error(request, f"Cannot delete category '{obj.name}' because it has associated products.")
                return False
        return True  # Allow deletion if no related objects

    def delete_queryset(self, request, queryset):
        """ Prevent deletion if any selected category has subcategories or products. """
        to_delete = []
        for obj in queryset:
            if obj.subcategories.exists():
                self.message_user(request, f"Cannot delete category '{obj.name}' because it has associated subcategories.", level=messages.ERROR)
            elif obj.products.exists():
                self.message_user(request, f"Cannot delete category '{obj.name}' because it has associated products.", level=messages.ERROR)
            else:
                to_delete.append(obj)  # Only delete categories with no dependencies

        if to_delete:
            count = len(to_delete)
            queryset.filter(id__in=[obj.id for obj in to_delete]).delete()
            self.message_user(request, f"Successfully deleted {count} category(ies).", level=messages.SUCCESS)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category__name")

    def has_delete_permission(self, request, obj=None):
        """ Prevent deletion if the subcategory has associated products. """
        if obj and obj.products.exists():
            messages.error(request, f"Cannot delete subcategory '{obj.name}' because it has associated products.")
            return False
        return True

    def delete_queryset(self, request, queryset):
        """ Prevent deletion of subcategories that have products. """
        to_delete = []
        for obj in queryset:
            if obj.products.exists():
                self.message_user(request, f"Cannot delete subcategory '{obj.name}' because it has associated products.", level=messages.ERROR)
            else:
                to_delete.append(obj)  # Only delete subcategories without products

        if to_delete:
            count = len(to_delete)
            queryset.filter(id__in=[obj.id for obj in to_delete]).delete()
            self.message_user(request, f"Successfully deleted {count} subcategory(ies).", level=messages.SUCCESS)



@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ("title",)  
    search_fields = ("title",)  


