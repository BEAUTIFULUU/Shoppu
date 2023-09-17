from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .logic import get_list_categories, get_category_details, get_list_products, get_product_details
from .serializers import CategorySerializer, UpdateDeleteCategorySerializer, ProductSerializer, UpdateDeleteProductSerializer
from .permissions import IsAdminOrReadOnly


class CategoryView(generics.ListCreateAPIView):
    queryset = get_list_categories()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateDeleteCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'category_id'

    def get_object(self):
        category_id = self.kwargs['category_id']
        return get_category_details(category_id=category_id)

    def update(self, request, *args, **kwargs):
        update_category = self.get_object()
        serializer = self.get_serializer(update_category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)


class ProductView(generics.ListCreateAPIView):
    queryset = get_list_products()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateDeleteProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        product_id = self.kwargs['product_id']
        return get_product_details(product_id=product_id)

    def update(self, request, *args, **kwargs):
        update_product = self.get_object()
        serializer = self.get_serializer(update_product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)




