from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .logic import get_list_categories, get_category_details, get_list_products, get_product_details, \
    get_list_promotions, get_promotion_details
from .serializers import CategoryInputSerializer, CategoryOutputSerializer, ProductInputSerializer, \
    ProductOutputSerializer, PromotionInputSerializer, PromotionOutputSerializer
from .permissions import IsAdminOrReadOnly


class CategoryView(generics.ListCreateAPIView):
    queryset = get_list_categories()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'description']

    def get_serializer_class(self):
        return CategoryInputSerializer if self.request.method == 'POST' else CategoryOutputSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category_obj = serializer.save()
        output_serializer = CategoryOutputSerializer(category_obj)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'category_id'

    def get_serializer_class(self):
        return CategoryInputSerializer if self.request.method == 'PUT' else CategoryOutputSerializer

    def get_object(self):
        category_id = self.kwargs['category_id']
        return get_category_details(category_id=category_id)

    def update(self, request, *args, **kwargs):
        update_category = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        fields_to_update = ['title', 'description']
        for field in fields_to_update:
            setattr(update_category, field, serializer.validated_data.get(field, getattr(update_category, field)))

        update_category.save()

        output_serializer = CategoryOutputSerializer(update_category)
        return Response(output_serializer.data)


class ProductView(generics.ListCreateAPIView):
    queryset = get_list_products()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'unit_price', 'is_available', 'promotions']

    def get_serializer_class(self):
        return ProductInputSerializer if self.request.method == 'POST' else ProductOutputSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_obj = serializer.save()
        output_serializer = ProductOutputSerializer(product_obj)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'product_id'

    def get_serializer_class(self):
        return ProductInputSerializer if self.request.method == 'PUT' else ProductOutputSerializer

    def get_object(self):
        product_id = self.kwargs['product_id']
        return get_product_details(product_id=product_id)

    def update(self, request, *args, **kwargs):
        update_product = self.get_object()
        serializer = self.get_serializer(update_product, data=request.data)
        serializer.is_valid(raise_exception=True)

        fields_to_update = ['title', 'description', 'unit_price', 'on_stock', 'is_available']
        for field in fields_to_update:
            setattr(update_product, field, serializer.validated_data.get(field, getattr(update_product, field)))

        if 'categories' in serializer.validated_data:
            update_product.categories.set(serializer.validated_data['categories'])

        if 'promotions' in serializer.validated_data:
            update_product.promotions.set(serializer.validated_data['promotions'])

        update_product.save()

        output_serializer = ProductOutputSerializer(update_product)
        return Response(output_serializer.data)


class PromotionView(generics.ListCreateAPIView):
    queryset = get_list_promotions()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'start_date', 'end_date']

    def get_serializer_class(self):
        return PromotionInputSerializer if self.request.method == 'POST' else PromotionOutputSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promotion_obj = serializer.save()
        output_serializer = PromotionOutputSerializer(promotion_obj)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class PromotionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    lookup_field = 'promotion_id'

    def get_serializer_class(self):
        return PromotionInputSerializer if self.request.method == 'PUT' else PromotionOutputSerializer

    def get_object(self):
        promotion_id = self.kwargs['promotion_id']
        return get_promotion_details(promotion_id=promotion_id)

    def update(self, request, *args, **kwargs):
        update_promotion = self.get_object()
        serializer = self.get_serializer(update_promotion, data=request.data)
        serializer.is_valid(raise_exception=True)

        fields_to_update = ['title', 'description', 'start_date', 'end_date', 'discount_percentage']
        for field in fields_to_update:
            setattr(update_promotion, field, serializer.validated_data.get(field, getattr(update_promotion, field)))

        update_promotion.save()

        output_serializer = PromotionOutputSerializer(update_promotion)
        return Response(output_serializer.data)
