import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class Promotion(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=150, blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], blank=False
    )


class Category(models.Model):
    title = models.CharField(max_length=200, blank=False)
    description = models.CharField(max_length=500, blank=False)


class Address(models.Model):
    street = models.CharField(max_length=200, blank=False)
    city = models.CharField(max_length=100, blank=False)
    postal_code = models.CharField(max_length=10, blank=False)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Product(models.Model):
    title = models.CharField(max_length=200, blank=False)
    categories = models.ManyToManyField(Category, related_name="products")
    description = models.CharField(max_length=200, blank=False)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, blank=False)
    on_stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True, blank=False)
    promotions = models.ManyToManyField(Promotion, related_name="products", blank=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="carts", blank=False
    )
    products = models.ManyToManyField(Product, related_name="carts", through="CartItem")
    is_completed = models.BooleanField(default=False, blank=False)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, blank=False, related_name="cart_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveSmallIntegerField(blank=False)


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", blank=False
    )
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="orders", blank=False
    )
    order_date = models.DateField(auto_now_add=True)
