from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .logic import get_list_categories, get_category_details, get_list_products, get_product_details
from .models import Category
from .serializers import CategoryInputSerializer, CategoryOutputSerializer, ProductInputSerializer, \
    ProductOutputSerializer
from .permissions import IsAdminOrReadOnly


class CategoryView(generics.ListCreateAPIView):
    queryset = get_list_categories()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryOutputSerializer
        elif self.request.method == 'POST':
            return CategoryInputSerializer
        else:
            return CategoryOutputSerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'category_id'

    def get_object(self):
        category_id = self.kwargs['category_id']
        return get_category_details(category_id=category_id)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryOutputSerializer
        elif self.request.method == 'PUT':
            return CategoryInputSerializer

    def update(self, request, *args, **kwargs):
        update_category = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_category.title = serializer.validated_data['title']
        update_category.description = serializer.validated_data['description']
        update_category.save()

        output_serializer = CategoryOutputSerializer(update_category)
        return Response(output_serializer.data)


class ProductView(generics.ListCreateAPIView):
    queryset = get_list_products()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductOutputSerializer
        elif self.request.method == 'POST':
            return ProductInputSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'product_id'

    def get_object(self):
        product_id = self.kwargs['product_id']
        return get_product_details(product_id=product_id)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductOutputSerializer
        elif self.request.method == 'PUT':
            return ProductInputSerializer
        else:
            return ProductOutputSerializer

    def update(self, request, *args, **kwargs):
        updated_product = self.get_object()
        serializer = self.get_serializer(updated_product, data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_product.title = serializer.validated_data.get('title', updated_product.title)
        updated_product.description = serializer.validated_data.get('description', updated_product.description)
        updated_product.unit_price = serializer.validated_data.get('unit_price', updated_product.unit_price)
        updated_product.on_stock = serializer.validated_data.get('on_stock', updated_product.on_stock)
        updated_product.is_available = serializer.validated_data.get('is_available', updated_product.is_available)

        if 'promotions' in serializer.validated_data:
            updated_product.promotions.set(serializer.validated_data['promotions'])
        if 'categories' in serializer.validated_data:
            updated_product.categories.set(serializer.validated_data['categories'])

        updated_product.save()

        output_serializer = ProductOutputSerializer(updated_product)
        return Response(output_serializer.data)
