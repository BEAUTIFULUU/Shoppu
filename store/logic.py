from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import Category, Product, Promotion


def get_list_categories():
    categories = Category.objects.all().annotate(products_count=Count('products'))
    return categories


def get_category_details(category_id):
    category_obj = Category.objects.filter(id=category_id)
    return get_object_or_404(category_obj)


def get_list_products():
    products = Product.objects.prefetch_related('categories', 'promotions')
    return products


def get_product_details(product_id):
    product_obj = Product.objects.filter(id=product_id).prefetch_related('categories', 'promotions')
    return get_object_or_404(product_obj)


def get_list_promotions():
    promotions = Promotion.objects.all()
    return promotions


def get_promotion_details(promotion_id):
    promotion_obj = Promotion.objects.filter(id=promotion_id)
    return get_object_or_404(promotion_obj)


def update_product_categories(product_obj, category_ids):
    product_obj.categories.set(category_ids)
    product_obj.save()
    return product_obj


def update_product_promotions(product_obj, promotion_ids):
    product_obj.promotions.set(promotion_ids)
    product_obj.save()
    return product_obj


def create_product_categories(product_obj, categories):
    product_obj.categories.set(categories)
    product_obj.save()
    return product_obj


def create_product_promotions(product_obj, promotions):
    product_obj.promotions.set(promotions)
    product_obj.save()
    return product_obj
