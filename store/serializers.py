from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from .models import Category, Product, Promotion, Cart, CartItem
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
    on_stock = serializers.IntegerField(required=True, validators=[MinValueValidator(0), MaxValueValidator(5000)])
    is_available = serializers.BooleanField(required=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=True
    )
    promotions = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(), many=True, required=False
    )

    def validate_categories(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("At least one category is required.")
        return value


class ProductOutputSerializer(serializers.ModelSerializer):
    discount_price = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    promotions = serializers.SerializerMethodField()

    def get_categories(self, obj):
        return [category.title for category in obj.categories.all()]

    def get_discount_price(self, obj):
        max_discount = 0

        for promotion in obj.promotions.all():
            max_discount = max(max_discount, promotion.discount_percentage)

        if max_discount > 0:
            discount_multiplier = 1 - (Decimal(max_discount) / 100)
            discounted_price = obj.unit_price * discount_multiplier
            return str(round(discounted_price, 2))
        else:
            return str(round(obj.unit_price, 2))

    def get_promotions(self, obj):
        return [promotion.title for promotion in obj.promotions.all()]

    class Meta:
        model = Product
        fields = ['id', 'title', 'categories', 'description', 'unit_price', 'on_stock', 'is_available',
                  'discount_price', 'promotions']


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


class CartHistoryOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'is_completed']


class CartItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    quantity = serializers.IntegerField(required=True, validators=[MinValueValidator(0), MaxValueValidator(5000)])


class CartItemOutputSerializer(serializers.ModelSerializer):
    product_id = serializers.ReadOnlyField(source='product.id')
    product_title = serializers.ReadOnlyField(source='product.title')
    product_unit_price = serializers.ReadOnlyField(source='product.unit_price')
    product_promotions = serializers.SerializerMethodField()
    quantity = serializers.ReadOnlyField()
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, obj):
        if obj.product.promotions.exists():
            max_discount = max(promotion.discount_percentage for promotion in obj.product.promotions.all())
            discount_multiplier = 1 - (Decimal(max_discount / 100))
            total_price_with_discount = obj.product.unit_price * discount_multiplier
            return str(round(total_price_with_discount * obj.quantity, 2))
        else:
            return str(round(obj.product.unit_price * obj.quantity, 2))

    def get_product_promotions(self, obj):
        return [promotion.title for promotion in obj.product.promotions.all()]

    class Meta:
        model = CartItem
        fields = ['product_id', 'product_title', 'product_unit_price', 'product_promotions', 'quantity', 'total_price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['product_unit_price'] = "{:.2f}".format(instance.product.unit_price)

        return representation


class CartDetailsOutputSerializer(serializers.ModelSerializer):
    cart_items = CartItemOutputSerializer(many=True, read_only=True)
    cart_total_cost = serializers.SerializerMethodField()

    def get_cart_total_cost(self, obj):
        total_cost = Decimal(0)
        cart_items_data = CartItemOutputSerializer(obj.cart_items, many=True).data
        for cart_item_data in cart_items_data:
            total_cost += Decimal(cart_item_data['total_price'])
        return str(round(total_cost, 2))

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'cart_total_cost', 'cart_items']
