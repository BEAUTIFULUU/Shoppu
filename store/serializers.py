from rest_framework import serializers
from .models import Category, Product, Promotion
from decimal import Decimal


class CategoryInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'description']


class CategoryOutputSerializer(serializers.ModelSerializer):
    products_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'products_count']


class ProductInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'categories', 'description', 'unit_price', 'on_stock', 'is_available', 'promotions']


class ProductOutputSerializer(serializers.ModelSerializer):
    discount_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'categories', 'description', 'unit_price', 'on_stock', 'is_available',
                  'discount_price', 'promotions']

    def get_discount_price(self, obj):
        max_discount = 0

        for promotion in obj.promotions.all():
            max_discount = max(max_discount, promotion.discount_percentage)

        if max_discount > 0:
            discount_multiplier = 1 - (Decimal(max_discount / 100))
            discounted_price = obj.unit_price * discount_multiplier
            return round(float(discounted_price), 2)
        else:
            return float(obj.unit_price)


class PromotionInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['title', 'description', 'start_date', 'end_date', 'discount_percentage']


class PromotionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'discount_percentage']
