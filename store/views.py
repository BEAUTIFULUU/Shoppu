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
        return CategoryInputSerializer if self.request.method == 'POST' else CategoryOutputSerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'category_id'

    def get_object(self):
        category_id = self.kwargs['category_id']
        return get_category_details(category_id=category_id)

    def get_serializer_class(self):
        return CategoryInputSerializer if self.request.method == 'PUT' else CategoryOutputSerializer

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

    def get_serializer_class(self):
        return ProductInputSerializer if self.request.method == 'POST' else ProductOutputSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'product_id'

    def get_object(self):
        product_id = self.kwargs['product_id']
        return get_product_details(product_id=product_id)

    def get_serializer_class(self):
        return ProductInputSerializer if self.request.method == 'PUT' else ProductOutputSerializer

    def update(self, request, *args, **kwargs):
        updated_product = self.get_object()
        serializer = self.get_serializer(updated_product, data=request.data)
        serializer.is_valid(raise_exception=True)

        fields_to_update = ['title', 'description', 'unit_price', 'on_stock', 'is_available']
        for field in fields_to_update:
            setattr(updated_product, field, serializer.validated_data.get(field, getattr(updated_product, field)))

        if 'promotions' in serializer.validated_data:
            updated_product.promotions.set(serializer.validated_data['promotions'])
        if 'categories' in serializer.validated_data:
            updated_product.categories.set(serializer.validated_data['categories'])

        updated_product.save()

        output_serializer = ProductOutputSerializer(updated_product)
        return Response(output_serializer.data)
