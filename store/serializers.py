from rest_framework import serializers
from .models import Category, Product, Promotion


class CategoryInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'description']


class CategoryOutputSerializer(serializers.ModelSerializer):
    products_count = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'products_count']


class ProductInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'categories', 'description', 'unit_price', 'on_stock', 'is_available', 'promotions']


class ProductOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'categories', 'description', 'unit_price', 'on_stock', 'is_available', 'promotions']
