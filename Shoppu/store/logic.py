from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import Category, Product


def get_list_categories():
    categories = Category.objects.all().annotate(products_count=Count('products'))
    return categories


def get_category_details(category_id):
    category_obj = Category.objects.filter(id=category_id)
    return get_object_or_404(category_obj)


def get_list_products():
    products = Product.objects.all()
    return products


def get_product_details(product_id):
    product_obj = Product.objects.filter(id=product_id)
    return get_object_or_404(product_obj)
