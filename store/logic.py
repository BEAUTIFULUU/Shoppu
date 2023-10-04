from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Prefetch, QuerySet
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, serializers
from rest_framework.response import Response
from typing import Optional, Tuple, Union

from .models import Category, Product, Promotion, Cart, CartItem
from .serializers import CartDetailsOutputSerializer


def get_list_categories() -> QuerySet:
    categories = Category.objects.all().annotate(products_count=Count('products'))
    return categories


def get_category_details(category_id: int) -> Category:
    category_obj = Category.objects.filter(id=category_id)
    return get_object_or_404(category_obj)


def get_list_products() -> QuerySet:
    products = Product.objects.prefetch_related('categories', 'promotions')
    return products


def get_product_details(product_id: int) -> Product:
    product_obj = Product.objects.filter(id=product_id).prefetch_related('categories', 'promotions')
    return get_object_or_404(product_obj)


def get_product(product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


def get_list_promotions() -> QuerySet:
    promotions = Promotion.objects.all()
    return promotions


def get_promotion_details(promotion_id: int) -> Promotion:
    promotion_obj = get_object_or_404(Promotion, id=promotion_id)
    return promotion_obj


def create_update_product_categories(product_obj: Product, categories: list[Category]) -> Product:
    product_obj.categories.set(categories)
    return product_obj.save()


def create_update_product_promotions(product_obj: Product, promotions: list[Promotion]) -> Product:
    product_obj.promotions.set(promotions)
    return product_obj.save()


def pop_categories_from_product_data(serializer):
    return serializer.validated_data.pop('categories', [])


def pop_promotions_from_product_data(serializer):
    return serializer.validated_data.pop('promotions', [])


def get_or_create_user_cart(user) -> Tuple[Cart, bool]:
    cart, created = Cart.objects.get_or_create(user=user, is_completed=False)
    return cart, created


def get_user_cart_history(user) -> QuerySet:
    carts = Cart.objects.filter(user=user, is_completed=True)
    return carts


def get_cart_details(user) -> Cart:
    return get_object_or_404(
        Cart.objects.filter(user=user, is_completed=False).prefetch_related(
            Prefetch('cart_items', queryset=CartItem.objects.select_related('product')
                     .prefetch_related('product__promotions'))
        )
    )


def get_cart_item(cart_obj: Cart, product_id: Product) -> Optional[CartItem]:
    try:
        return CartItem.objects.get(cart=cart_obj, product_id=product_id)
    except ObjectDoesNotExist:
        return None


def update_cart_item(cart_item_obj: CartItem, product_obj: Product, quantity: id) -> CartItem:
    quantity_diff = quantity - cart_item_obj.quantity

    product_obj.on_stock -= quantity_diff
    product_obj.save()

    cart_item_obj.quantity = quantity
    return cart_item_obj.save()


def delete_cart_item(cart_item_obj: CartItem, product_obj: Product) -> None:
    product_obj.on_stock += cart_item_obj.quantity
    product_obj.save()
    cart_item_obj.delete()


def create_cart_item(cart: Cart, quantity: id, product_obj: Product, product_id: id) -> CartItem:
    new_cart_item = []

    cart_item_data = CartItem(cart=cart, product_id=product_id.id, quantity=quantity)
    new_cart_item.append(cart_item_data)

    CartItem.objects.bulk_create(new_cart_item)

    product_obj.on_stock -= quantity
    product_obj.save()

    return cart_item_data


def create_update_delete_cart_item(
        quantity: id, product_obj: Product, cart_item_obj: CartItem, cart_obj: Cart, product_id: int) -> Union[Response, None]:

    error_message = 'Invalid product_id or quantity.'
    effective_stock = product_obj.on_stock
    if cart_item_obj:
        effective_stock += cart_item_obj.quantity

    effective_stock -= quantity

    if cart_item_obj:
        if quantity == 0:
            delete_cart_item(cart_item_obj=cart_item_obj, product_obj=product_obj)
            output_serializer = CartDetailsOutputSerializer(cart_obj)
            return Response(output_serializer.data)

        elif effective_stock >= 0:
            update_cart_item(cart_item_obj=cart_item_obj, product_obj=product_obj, quantity=quantity)
            output_serializer = CartDetailsOutputSerializer(cart_obj)
            return Response(output_serializer.data)
    else:
        if quantity <= product_obj.on_stock:
            create_cart_item(cart=cart_obj, product_id=product_id, quantity=quantity, product_obj=product_obj)
            output_serializer = CartDetailsOutputSerializer(cart_obj)
            return Response(output_serializer.data)

    raise serializers.ValidationError(error_message)
