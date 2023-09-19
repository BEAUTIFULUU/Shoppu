from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from .models import Category, Product, Promotion
from decimal import Decimal


class CategoryInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=2100, required=True)
    description = serializers.CharField(max_length=500, required=True)


class CategoryOutputSerializer(serializers.ModelSerializer):
    products_count = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'products_count']


class ProductInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(max_length=200, required=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, required=True)
    on_stock = serializers.IntegerField(required=True)
    is_available = serializers.BooleanField(required=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=True
    )
    promotions = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(), many=True, required=False
    )


class ProductOutputSerializer(serializers.ModelSerializer):
    discount_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'categories', 'description', 'unit_price', 'on_stock', 'is_available',
                  'discount_price', 'promotions']

    def get_categories(self, obj):
        return [category.title for category in obj.categories.all()]

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['categories'] = self.get_categories(instance)
        return data


class PromotionInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=150, required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    discount_percentage = serializers.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        required=True
    )


class PromotionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'discount_percentage']
