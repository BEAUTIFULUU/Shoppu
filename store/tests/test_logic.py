import pytest
import uuid
from django.contrib.auth import get_user_model
from django.http import Http404
from store.models import Category, Product, Promotion, Cart, CartItem
from store.logic import get_list_categories, get_category_details, get_list_products, get_product_details, \
    get_list_promotions, get_promotion_details, create_update_product_categories, create_update_product_promotions, \
    get_or_create_user_cart, get_user_cart_history, get_cart_item, get_product, update_cart_item, delete_cart_item, \
    create_cart_item, create_update_delete_cart_item
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def create_category():
    category_obj = Category.objects.create(title='123', description='123')
    return category_obj


@pytest.fixture
def create_product(create_category):
    category_obj = create_category
    product_obj = Product.objects.create(
        title='123',
        description='123',
        unit_price=123,
        is_available=True,
        on_stock=123,
    )
    product_obj.categories.add(category_obj)
    return product_obj


@pytest.fixture
def create_promotion():
    promotion_obj = Promotion.objects.create(
        title='123',
        start_date='2023-09-16',
        end_date='2023-09-18',
        discount_percentage=15
    )
    return promotion_obj


def create_authenticated_user(username, password):
    user = User.objects.create_user(username=username, password=password)
    client = APIClient()
    client.login(username=username, password=password)
    return user, client


def create_admin_user(username, password, email):
    admin_user = User.objects.create_superuser(
        username=username, password=password, email=email)
    return admin_user


@pytest.fixture
def create_not_completed_cart():
    cart_id = uuid.uuid4()
    user, client = create_authenticated_user(username='123', password='123')
    cart_obj = Cart.objects.create(id=cart_id, created_at='30-09-2023', user=user, is_completed=False)
    return cart_obj, user


@pytest.fixture
def create_completed_cart():
    cart_id = uuid.uuid4()
    user, client = create_authenticated_user(username='123', password='123')
    cart_obj = Cart.objects.create(id=cart_id, created_at='30-09-2023', user=user, is_completed=True)
    return cart_obj, user


@pytest.fixture
def create_completed_and_not_completed_cart(create_completed_cart):
    cart_id = uuid.uuid4()
    _, user = create_completed_cart
    cart_obj = Cart.objects.create(id=cart_id, created_at='30-09-2023', user=user, is_completed=False)
    return cart_obj, user


@pytest.fixture
def create_cart_item_fxt(create_not_completed_cart, create_product):
    cart_obj, user = create_not_completed_cart
    product_obj = create_product
    cart_item_obj = CartItem.objects.create(cart=cart_obj, product_id=product_obj.id, quantity=10)
    return cart_item_obj, user, cart_obj


@pytest.mark.django_db
class TestCategoryLogic:

    def test_get_list_categories(self, create_category):
        category_obj = create_category
        categories = get_list_categories()

        assert len(categories) == 1
        assert category_obj in categories

    def test_get_category_details(self, create_category):
        category_obj = create_category
        category_details = get_category_details(category_id=category_obj.id)

        assert category_obj == category_details

    def test_get_categories_details_invalid_data(self):
        with pytest.raises(Http404):
            get_category_details(category_id=99999)

    def test_get_categories_details_missing_data(self):
        with pytest.raises(Http404):
            get_category_details(category_id=None)


@pytest.mark.django_db
class TestProductLogic:
    def test_get_list_products(self, create_product):
        product_obj = create_product
        products = get_list_products()

        assert len(products) == 1
        assert product_obj in products

    def test_get_product_details(self, create_product):
        product_obj = create_product
        product_details = get_product_details(product_id=product_obj.id)

        assert product_details == product_obj
        assert list(product_details.categories.all()) == list(product_obj.categories.all())

    def test_get_product_or_404_product_exist(self, create_product):
        product_obj = create_product
        existing_product = get_product(product_id=product_obj.id)

        assert Product.objects.count() == 1
        assert existing_product == product_obj

    def test_create_update_product_categories(self, create_product, create_category):
        categories = [create_category.id]
        create_update_product_categories(product_obj=create_product, categories=categories)
        updated_product = Product.objects.get(id=create_product.id)

        assert list(updated_product.categories.values_list('id', flat=True)) == categories
        assert Product.objects.count() == 1

    def test_create_update_product_promotions(self, create_product, create_promotion):
        promotions = [create_promotion.id]
        create_update_product_promotions(product_obj=create_product, promotions=promotions)
        updated_product = Product.objects.get(id=create_product.id)

        assert list(updated_product.promotions.values_list('id', flat=True)) == promotions
        assert Product.objects.count() == 1

    def test_get_product_details_invalid_data(self):
        with pytest.raises(Http404):
            get_product_details(product_id=9999999)

    def test_get_product_details_missing_data(self):
        with pytest.raises(Http404):
            get_product_details(product_id=None)


@pytest.mark.django_db
class TestPromotionLogic:
    def test_get_list_promotions(self, create_promotion):
        promotion_obj = create_promotion
        promotions = get_list_promotions()

        assert len(promotions) == 1
        assert promotion_obj in promotions

    def test_get_promotion_details(self, create_promotion):
        promotion_obj = create_promotion
        promotion_details = get_promotion_details(promotion_id=promotion_obj.id)

        assert promotion_details == promotion_obj

    def test_get_promotion_details_invalid_data(self, create_promotion):
        with pytest.raises(Http404):
            get_promotion_details(promotion_id=99999)

    def test_get_promotion_details_missing_data(self, create_promotion):
        with pytest.raises(Http404):
            get_promotion_details(promotion_id=None)


@pytest.mark.django_db
class TestCartLogic:

    def test_get_or_create_user_cart_if_user_has_carts(self, create_completed_and_not_completed_cart):
        cart_obj, user = create_completed_and_not_completed_cart
        cart, created = get_or_create_user_cart(user=user)

        assert not created
        assert Cart.objects.count() == 2
        assert cart == cart_obj

    def test_get_or_create_user_cart_if_user_has_no_cart(self):
        user, client = create_authenticated_user(username='123', password='123')
        cart, created = get_or_create_user_cart(user=user)
        cart_obj = Cart.objects.get(user=user)

        assert created
        assert Cart.objects.count() == 1
        assert cart == cart_obj

    def test_get_user_cart_history_if_user_has_completed_and_not_completed_carts(
            self, create_completed_and_not_completed_cart):
        carts, user = create_completed_and_not_completed_cart
        get_user_cart_history(user=user)

        assert Cart.objects.count() == 2

    def test_get_cart_history_if_user_has_completed_cart(self, create_completed_cart):
        cart_obj, user = create_completed_cart
        get_user_cart_history(user=user)
        given_cart_obj = Cart.objects.get(user=user)

        assert Cart.objects.filter(user=user).count() == 1
        assert given_cart_obj == cart_obj

    def test_get_cart_history_if_user_has_not_completed_cart(self, create_not_completed_cart):
        cart_obj, user = create_not_completed_cart
        get_user_cart_history(user=user)
        given_cart_obj = Cart.objects.get(user=user)

        assert Cart.objects.filter(user=user).count() == 1
        assert given_cart_obj == cart_obj


@pytest.mark.django_db
class TestCartItemLogic:

    def test_get_cart_item_if_cart_item_exist(self, create_cart_item_fxt, create_product):
        product_obj = create_product
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        found_cart_item = get_cart_item(cart_obj=cart_obj, product_id=product_obj.id)

        assert Product.objects.count() == 1
        assert CartItem.objects.count() == 1
        assert found_cart_item == cart_item_obj

    def test_get_cart_item_if_cart_item_does_not_exist(self):
        found_cart_item = get_cart_item(cart_obj=None, product_id=None)

        assert CartItem.objects.count() == 0
        assert found_cart_item is None

    def test_update_cart_item(self, create_cart_item_fxt, create_product):
        cart_item_obj, _, _, = create_cart_item_fxt
        product_obj = create_product
        update_cart_item(cart_item_obj=cart_item_obj, product_obj=product_obj, quantity=15)

        updated_cart_item = CartItem.objects.get(product_id=product_obj.id)
        assert CartItem.objects.count() == 1
        assert Product.objects.count() == 1
        assert updated_cart_item.quantity == 15

    def test_delete_cart_item(self, create_cart_item_fxt, create_product):
        cart_item_obj, _, _, = create_cart_item_fxt
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        delete_cart_item(cart_item_obj=cart_item_obj, product_obj=product_obj)

        updated_on_stock = Product.objects.get(id=product_obj.id)
        assert Product.objects.count() == 1
        assert CartItem.objects.count() == 0
        assert updated_on_stock.on_stock == int(initial_on_stock + cart_item_obj.quantity)

    def test_create_cart_item_fxt(self, create_not_completed_cart, create_product,):
        cart_obj, _ = create_not_completed_cart
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        quantity = 10
        create_cart_item(cart=cart_obj, product_id=product_obj, product_obj=product_obj, quantity=quantity)

        cart_item_obj = CartItem.objects.get(product_id=product_obj)
        assert CartItem.objects.count() == 1
        assert Product.objects.count() == 1
        assert Cart.objects.count() == 1
        assert cart_item_obj.cart.id == cart_obj.id
        assert cart_item_obj.product_id == product_obj.id
        assert cart_item_obj.quantity == quantity
        assert product_obj.on_stock == int(initial_on_stock - quantity)

    def test_create_update_delete_cart_item_create_situation(
            self, create_cart_item_fxt, create_product):

        cart_item_obj, _, cart_obj = create_cart_item_fxt
        product_obj = create_product
        initial_cart_item_count = CartItem.objects.count()
        initial_cart_count = Cart.objects.count()

        created_cart_item = create_update_delete_cart_item(
            cart_obj=cart_obj, cart_item_obj=None, product_obj=product_obj, product_id=product_obj, quantity=5)

        assert Cart.objects.count() == initial_cart_count
        assert CartItem.objects.count() == initial_cart_item_count + 1
        assert created_cart_item is not None

    def test_create_update_delete_cart_item_update_situation(
            self, create_cart_item_fxt, create_not_completed_cart, create_product):

        cart_item_obj, _, cart_obj = create_cart_item_fxt
        product_obj = create_product
        initial_product_on_stock = product_obj.on_stock
        initial_cart_item_quantity = cart_item_obj.quantity
        initial_cart_items_count = CartItem.objects.count()
        initial_cart_count = Cart.objects.count()
        quantity = 1

        create_update_delete_cart_item(
            cart_obj=cart_obj, cart_item_obj=cart_item_obj, product_obj=product_obj, product_id=product_obj, quantity=quantity)

        updated_cart_item = CartItem.objects.get(id=cart_item_obj.id)

        assert CartItem.objects.count() == initial_cart_items_count
        assert Cart.objects.count() == initial_cart_count
        assert updated_cart_item.quantity == 1
        assert product_obj.on_stock == initial_product_on_stock + (initial_cart_item_quantity - quantity)

    def test_create_delete_cart_item_delete_situation(self, create_cart_item_fxt, create_not_completed_cart, create_product):
        cart_item_obj, _, cart_obj = create_cart_item_fxt
        product_obj = create_product
        initial_product_on_stock = product_obj.on_stock
        initial_cart_item_quantity = cart_item_obj.quantity
        quantity = 0

        create_update_delete_cart_item(
            cart_obj=cart_obj, cart_item_obj=cart_item_obj, product_obj=product_obj, product_id=product_obj, quantity=quantity)

        assert CartItem.objects.count() == 0
        assert product_obj.on_stock == initial_product_on_stock + (initial_cart_item_quantity - quantity)















