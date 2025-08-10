from django.db import models
from django.core.exceptions import ValidationError



class SliderImage(models.Model):
    image = models.ImageField(upload_to='slider_images/')
    title = models.CharField(max_length=200, blank=True, null=True)
    

    def __str__(self):
        return self.title if self.title else "Slider Image"
    
    class Meta:
        verbose_name_plural ="Slider Image"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def delete(self, *args, **kwargs):
        
        if self.subcategories.exists():
            raise ValidationError(f"Cannot delete category '{self.name}' because it has associated subcategories.")
        if self.products.exists():
            raise ValidationError(f"Cannot delete category '{self.name}' because it has associated products.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural ="Category"

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100, blank=False, null=False)

    def delete(self, *args, **kwargs):
        
        if self.products.exists():
            raise ValidationError(f"Cannot delete subcategory '{self.name}' because it has associated products.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    class Meta:
        verbose_name_plural ="SubCategory"

class Product(models.Model):
    name = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Selling price
    quantity_available = models.PositiveIntegerField(default=1)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Original price
    discount = models.PositiveIntegerField(blank=True, null=True)  # Auto-calculated if applicable
    best_selling = models.BooleanField(default=False)

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")
        if self.discount and (self.discount < 0 or self.discount > 100):
            raise ValidationError("Discount must be between 0 and 100.")
        if self.subcategory and self.subcategory.category != self.category:
            raise ValidationError("The subcategory does not belong to the selected category.")

    def save(self, *args, **kwargs):
        self.clean()

        # Ensure old_price is set before calculating the discount
        if self.old_price and self.old_price > self.price:
            self.discount = round(((self.old_price - self.price) / self.old_price) * 100)
        else:
            self.discount = None  # No discount if old_price is not set or price == old_price

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural ="Product"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name_plural ="Product Image"