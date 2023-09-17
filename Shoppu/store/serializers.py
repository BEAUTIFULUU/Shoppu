from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    products_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'products_count']


class UpdateDeleteCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'description']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'unit_price', 'is_available', 'on_stock', 'category', 'promotion']


class UpdateDeleteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'unit_price', 'is_available', 'on_stock', 'category', 'promotion']
