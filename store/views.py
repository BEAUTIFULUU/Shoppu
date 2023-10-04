from typing import Type
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, generics, permissions, views
from django_filters.rest_framework import DjangoFilterBackend
from .logic import get_list_categories, get_category_details, get_list_products, get_product_details, \
    get_list_promotions, get_promotion_details, create_update_product_categories, create_update_product_promotions, \
    pop_categories_from_product_data, pop_promotions_from_product_data, \
    get_cart_details, get_or_create_user_cart, get_user_cart_history, get_product, create_update_delete_cart_item, \
    get_cart_item
from .models import Category, Promotion, Product, Cart
from .serializers import CategoryInputSerializer, CategoryOutputSerializer, ProductInputSerializer, \
    ProductOutputSerializer, PromotionInputSerializer, PromotionOutputSerializer, CartHistoryOutputSerializer, \
    CartItemInputSerializer, CartDetailsOutputSerializer
from .permissions import IsAdminOrReadOnly


class CategoryView(generics.ListCreateAPIView):
    queryset = get_list_categories()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'description']

    def get_serializer_class(self) -> Type[CategoryInputSerializer] | Type[CategoryOutputSerializer]:
        return CategoryInputSerializer if self.request.method == 'POST' else CategoryOutputSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category_obj = Category.objects.create(**serializer.validated_data)

        output_serializer = CategoryOutputSerializer(category_obj)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'category_id'

    def get_serializer_class(self) -> Type[CategoryInputSerializer | CategoryOutputSerializer]:
        return CategoryInputSerializer if self.request.method == 'PUT' else CategoryOutputSerializer

    def get_object(self) -> Category:
        category_id = self.kwargs['category_id']
        return get_category_details(category_id=category_id)

    def update(self, request, *args, **kwargs) -> Response:
        category_obj = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        fields_to_update = ['title', 'description']
        for field in fields_to_update:
            setattr(category_obj, field, serializer.validated_data.get(field, getattr(category_obj, field)))

        category_obj.save()

        output_serializer = CategoryOutputSerializer(category_obj)
        return Response(output_serializer.data)


class ProductView(generics.ListCreateAPIView):
    queryset = get_list_products()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'unit_price', 'is_available', 'promotions']

    def get_serializer_class(self) -> Type[ProductInputSerializer] | Type[ProductOutputSerializer]:
        return ProductInputSerializer if self.request.method == 'POST' else ProductOutputSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categories = pop_categories_from_product_data(serializer=serializer)
        promotions = pop_promotions_from_product_data(serializer=serializer)

        product_obj = Product.objects.create(**serializer.validated_data)

        create_update_product_categories(product_obj=product_obj, categories=categories)
        create_update_product_promotions(product_obj=product_obj, promotions=promotions)

        output_serializer = ProductOutputSerializer(product_obj)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'product_id'

    def get_serializer_class(self) -> Type[ProductInputSerializer] | Type[ProductOutputSerializer]:
        return ProductInputSerializer if self.request.method == 'PUT' else ProductOutputSerializer

    def get_object(self) -> Product:
        product_id = self.kwargs['product_id']
        return get_product_details(product_id=product_id)

    def update(self, request: Request, *args, **kwargs) -> Response:
        product_obj = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categories = pop_categories_from_product_data(serializer=serializer)
        promotions = pop_promotions_from_product_data(serializer=serializer)

        fields_to_update = ['title', 'description', 'unit_price', 'on_stock', 'is_available']
        for field in fields_to_update:
            setattr(product_obj, field, serializer.validated_data.get(field, getattr(product_obj, field)))

        product_obj.save()

        create_update_product_categories(product_obj=product_obj, categories=categories)
        create_update_product_promotions(product_obj=product_obj, promotions=promotions)

        output_serializer = ProductOutputSerializer(product_obj)
        return Response(output_serializer.data)


class PromotionView(generics.ListCreateAPIView):
    queryset = get_list_promotions()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'start_date', 'end_date']

    def get_serializer_class(self) -> Type[PromotionInputSerializer] | Type[PromotionOutputSerializer]:
        return PromotionInputSerializer if self.request.method == 'POST' else PromotionOutputSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promotion_obj = Promotion.objects.create(**serializer.validated_data)
        output_serializer = PromotionOutputSerializer(promotion_obj)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class PromotionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'promotion_id'

    def get_serializer_class(self) -> Type[PromotionInputSerializer] | Type[PromotionOutputSerializer]:
        return PromotionInputSerializer if self.request.method == 'PUT' else PromotionOutputSerializer

    def get_object(self) -> Promotion:
        promotion_id = self.kwargs['promotion_id']
        return get_promotion_details(promotion_id=promotion_id)

    def update(self, request: Request, *args, **kwargs) -> Response:
        promotion_obj = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        fields_to_update = ['title', 'description', 'start_date', 'end_date', 'discount_percentage']
        for field in fields_to_update:
            setattr(promotion_obj, field, serializer.validated_data.get(field, getattr(promotion_obj, field)))

        promotion_obj.save()

        output_serializer = PromotionOutputSerializer(promotion_obj)
        return Response(output_serializer.data)


class CartHistoryView(generics.ListAPIView):
    serializer_class = CartHistoryOutputSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'cart_id'

    def get_queryset(self) -> list[Cart]:
        user = self.request.user
        get_or_create_user_cart(user=user)
        carts = get_user_cart_history(user=user)
        all_carts = list(carts)
        return all_carts


class CartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        cart_details = get_cart_details(user=request.user)
        serializer = CartDetailsOutputSerializer(cart_details)
        return Response(serializer.data)

    def put(self, request: Request) -> Response:
        serializer = CartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        cart_obj = get_cart_details(user=request.user)
        product_obj = get_product(product_id=product_id.id)
        cart_item_obj = get_cart_item(cart_obj=cart_obj, product_id=product_id)

        return create_update_delete_cart_item(
            product_obj=product_obj, quantity=quantity, cart_item_obj=cart_item_obj, product_id=product_id, cart_obj=cart_obj)



