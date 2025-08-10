from django.db import models
from django.conf import settings
from django.utils import timezone
from store.models import Product
from userlogin.models import ContactInfo

# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Cart of {self.user.username}"

    class Meta:
        verbose_name_plural = "Cart"

# Cart Item Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
    def get_total_price(self):
        return self.product.price * self.quantity
    
    class Meta:
        verbose_name_plural = "Cart Item"

# Shipping Model
class Shipping(models.Model):
    charge = models.DecimalField(max_digits=10, decimal_places=2, default=70.00)
    
    def __str__(self):
        return f"Shipping Charge: ${self.charge}"
    
    class Meta:
        verbose_name_plural = "Shipping Charge"

# Order Model
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.JSONField(default=dict)  # Store multiple products as {"product_name": quantity}
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(ContactInfo, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('canceled', 'Canceled')], default='pending')
    order_date = models.DateField(auto_now_add=True)
    order_time = models.TimeField(auto_now_add=True)
    order_day = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        self.order_day = timezone.now().strftime('%A')  # Set dynamically on save
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

    class Meta:
        verbose_name_plural = "Order"
# Shipped Orders Model
class Shipped(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.JSONField(default=dict)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(ContactInfo, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=[('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')], default='shipped')
    shipped_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Shipped Order {self.id} - {self.user.username} - {self.status}"

    class Meta:
        verbose_name_plural = "Shipped"
# Delivered Orders Model
class Delivered(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.JSONField(default=dict)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(ContactInfo, on_delete=models.SET_NULL, null=True)
    delivered_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Delivered Order {self.id} - {self.user.username}"

    class Meta:
        verbose_name_plural = "Delivered"
# Canceled Orders Model
class Canceled(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.JSONField(default=dict)  # Store product details as JSON
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(ContactInfo, on_delete=models.SET_NULL, null=True)
    canceled_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Canceled Order {self.id} - {self.user.username}"

    class Meta:
        verbose_name_plural = "Canceled"