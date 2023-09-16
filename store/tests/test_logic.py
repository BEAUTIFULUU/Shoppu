import pytest
import uuid
from django.contrib.auth import get_user_model
from django.http import Http404
from store.models import Category, Product, Promotion
from store.logic import get_list_categories, get_category_details, get_list_products, get_product_details, \
    get_list_promotions, get_promotion_details
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
