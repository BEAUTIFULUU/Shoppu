import uuid
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Category, Product, Promotion, Cart, CartItem

User = get_user_model()


@pytest.fixture
def create_category():
    categories = Category.objects.create(title="123", description="123")
    return categories


@pytest.fixture
def create_product(create_category):
    category = create_category

    product_obj = Product.objects.create(
        title="123", description="123", unit_price=123, is_available=True, on_stock=123
    )

    product_obj.categories.add(category)
    return product_obj


@pytest.fixture
def create_promotion():
    promotions = Promotion.objects.create(
        title="123",
        description="123",
        start_date="2023-09-16",
        end_date="2023-09-18",
        discount_percentage=15,
    )
    return promotions


def create_authenticated_user(username, password):
    user = User.objects.create_user(username=username, password=password)
    client = APIClient()
    client.login(username=username, password=password)
    return user, client


def create_admin_user(username, password, email):
    admin_user = User.objects.create_superuser(
        username=username, password=password, email=email
    )
    client = APIClient()
    client.login(username=username, password=password, email=email)
    return admin_user, client


@pytest.fixture
def create_not_completed_cart():
    cart_id = uuid.uuid4()
    user, client = create_authenticated_user(username="123", password="123")
    cart_obj = Cart.objects.create(
        id=cart_id, created_at="30-09-2023", user=user, is_completed=False
    )
    return cart_obj, user


@pytest.fixture
def create_not_completed_cart_with_admin_user():
    cart_id = uuid.uuid4()
    user, client = create_admin_user(
        username="123", password="123", email="123@gmail.com"
    )
    cart_obj = Cart.objects.create(
        id=cart_id, created_at="30-09-2023", user=user, is_completed=False
    )
    return cart_obj, user


@pytest.fixture
def create_completed_cart():
    cart_id = uuid.uuid4()
    user, client = create_authenticated_user(username="123", password="123")
    cart_obj = Cart.objects.create(
        id=cart_id, created_at="30-09-2023", user=user, is_completed=True
    )
    return cart_obj, user


@pytest.fixture
def create_cart_item_fxt(create_not_completed_cart, create_product):
    cart_obj, user = create_not_completed_cart
    product_obj = create_product
    cart_item_obj = CartItem.objects.create(
        cart=cart_obj, product_id=product_obj.id, quantity=10
    )
    return cart_item_obj, user, cart_obj


@pytest.fixture
def create_cart_item_fxt_with_admin_user(
    create_not_completed_cart_with_admin_user, create_product
):
    cart_obj, user = create_not_completed_cart_with_admin_user
    product_obj = create_product
    cart_item_obj = CartItem.objects.create(
        cart=cart_obj, product_id=product_obj.id, quantity=10
    )
    return cart_item_obj, user, cart_obj


@pytest.mark.django_db
class TestCategoryViewPermissions:
    def test_category_view_return_categories_for_anonymous_user(self, create_category):
        client = APIClient()
        url = "get_create_category"
        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1

    def test_if_anonymous_user_create_category_return_403(self):
        client = APIClient()
        url = "get_create_category"
        data = {"title": "123", "description": "123"}

        response = client.post(reverse(url), data=data, format="json")
        assert Category.objects.count() == 0
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_category_view_return_categories_for_authenticated_user(
        self, create_category
    ):
        user, client = create_authenticated_user(username="123", password="123")
        url = "get_create_category"
        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1

    def test_if_authenticated_user_create_category_return_403(self):
        user, client = create_authenticated_user(username="123", password="123")
        url = "get_create_category"
        data = {"title": "123", "description": "123"}
        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 0

    def test_category_view_return_categories_for_admin_user_return_200(
        self, create_category
    ):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_category"
        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1

    def test_category_view_create_category_for_admin_user_return_201(self):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_category"
        data = {"title": "123", "description": "123"}

        response = client.post(reverse(url), data=data, format="json")
        assert Category.objects.count() == 1
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestCategoryDetailViewPermission:
    def test_if_anonymous_user_update_category_return_403(self, create_category):
        category_obj = create_category
        client = APIClient()
        url = "update_delete_category"
        data = {"title": "1234", "description": "1234"}

        response = client.put(
            reverse(url, kwargs={"category_id": category_obj.id}),
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_if_anonymous_user_delete_category_return_403(self, create_category):
        category_obj = create_category
        client = APIClient()
        url = "update_delete_category"
        response = client.delete(reverse(url, kwargs={"category_id": category_obj.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_if_authenticated_user_update_category_return_403(self, create_category):
        category_obj = create_category
        user, client = create_authenticated_user(username="123", password="123")
        url = "update_delete_category"
        data = {"title": "1234", "description": "1234"}
        response = client.put(
            reverse(url, kwargs={"category_id": category_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_if_authenticated_user_delete_category_return_403(self, create_category):
        category_obj = create_category
        user, client = create_authenticated_user(username="123", password="123")
        url = "update_delete_category"
        response = client.put(reverse(url, kwargs={"category_id": category_obj.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_if_admin_user_update_category_return_200(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_category"
        data = {"title": "1234", "description": "1234"}
        response = client.put(
            reverse(url, kwargs={"category_id": category_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1
        updated_category = Category.objects.get(id=category_obj.id)
        assert updated_category.title == data["title"]
        assert updated_category.description == data["description"]

    def test_if_admin_user_delete_category_return_204(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_category"
        response = client.delete(reverse(url, kwargs={"category_id": category_obj.id}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Category.objects.count() == 0


@pytest.mark.django_db
class TestCategoryViewInvalidData:
    def test_create_category_with_no_title_return_400(self):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_category"
        data = {"title": "", "description": "1234"}
        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 0

    def test_create_category_with_no_description_return_400(self):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_category"
        data = {"title": "1234", "description": ""}
        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 0


@pytest.mark.django_db
class TestCategoryDetailViewInvalidData:
    def test_update_category_with_no_title_return_400(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_category"
        data = {"title": "", "description": "1234"}
        response = client.put(
            reverse(url, kwargs={"category_id": category_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 1
        categories_after_request = Category.objects.get(id=category_obj.id)
        assert categories_after_request == category_obj

    def test_update_category_with_no_description_return_400(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_category"
        data = {"title": "1234", "description": ""}
        response = client.put(
            reverse(url, kwargs={"category_id": category_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 1
        category_after_request = Category.objects.get(id=category_obj.id)
        assert category_after_request == category_obj


@pytest.mark.django_db
class TestProductViewPermissions:
    def test_product_view_return_products_for_anonymous_user(self, create_product):
        client = APIClient()
        url = "get_create_product"
        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Product.objects.count() == 1

    def test_if_anonymous_user_create_product_return_403(self, create_category):
        categories = create_category
        client = APIClient()
        url = "get_create_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": 123,
            "is_available": True,
        }

        response = client.post(reverse(url), data=data, format="json")
        assert Product.objects.count() == 0
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_product_view_return_products_for_authenticated_user(self, create_product):
        user, client = create_authenticated_user(username="123", password="123")
        url = "get_create_product"
        response = client.get(reverse(url))

        assert Product.objects.count() == 1
        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_user_create_product_return_403(self, create_category):
        categories = create_category
        user, client = create_authenticated_user(username="123", password="123")
        url = "get_create_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": 123,
            "is_available": True,
        }

        response = client.post(reverse(url), data=data, format="json")
        assert Product.objects.count() == 0
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_product_view_return_products_for_admin_user(self, create_product):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_product"
        response = client.get(reverse(url))

        assert Product.objects.count() == 1
        assert response.status_code == status.HTTP_200_OK

    def test_admin_user_create_product_return_201(self, create_category):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        categories = create_category

        url = "get_create_product"

        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": 123,
            "is_available": True,
        }

        response = client.post(reverse(url), data=data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 1


@pytest.mark.django_db
class TestProductDetailViewPermissions:
    def test_if_anonymous_user_update_product_return_403(
        self, create_product, create_category
    ):
        product_obj = create_product
        categories = create_category
        client = APIClient()
        url = "update_delete_product"
        data = {
            "title": "321",
            "description": "321",
            "categories": [categories.id],
            "unit_price": 321,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )
        assert Product.objects.count() == 1
        assert response.status_code == status.HTTP_403_FORBIDDEN
        updated_product = Product.objects.get(id=product_obj.id)
        assert updated_product == product_obj

    def test_if_anonymous_user_delete_product_return_403(self, create_product):
        product_obj = create_product
        client = APIClient()
        url = "update_delete_product"
        response = client.delete(reverse(url, kwargs={"product_id": product_obj.id}))

        assert Product.objects.count() == 1
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_authenticated_user_update_product_return_403(
        self, create_product, create_category
    ):
        product_obj = create_product
        categories = create_category
        user, client = create_authenticated_user(username="123", password="123")
        url = "update_delete_product"
        data = {
            "title": "321",
            "description": "321",
            "categories": [categories.id],
            "unit_price": 321,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )
        assert Product.objects.count() == 1
        assert response.status_code == status.HTTP_403_FORBIDDEN
        updated_product = Product.objects.get(id=product_obj.id)
        assert updated_product == product_obj

    def test_if_authenticated_user_delete_product_return_403(self, create_product):
        product_obj = create_product
        user, client = create_authenticated_user(username="123", password="123")
        url = "update_delete_product"
        response = client.delete(reverse(url, kwargs={"product_id": product_obj.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Product.objects.count() == 1

    def test_if_admin_user_update_product_return_200(
        self, create_product, create_category, create_promotion
    ):
        product_obj = create_product
        categories = create_category
        promotions = create_promotion
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        data = {
            "title": "321",
            "description": "321",
            "categories": [categories.id],
            "unit_price": 321,
            "on_stock": 0,
            "is_available": False,
            "promotions": [promotions.id],
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Product.objects.count() == 1
        updated_product = Product.objects.get(id=product_obj.id)
        for field in ["title", "description", "unit_price", "on_stock", "is_available"]:
            assert getattr(updated_product, field) == data[field]
        assert list(updated_product.categories.all()) == [categories]
        assert list(updated_product.promotions.all()) == [promotions]

    def test_if_admin_user_delete_product_return_204(self, create_product):
        product_obj = create_product
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        response = client.delete(reverse(url, kwargs={"product_id": product_obj.id}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.count() == 0


@pytest.mark.django_db
class TestProductViewInvalidData:
    def test_create_product_with_no_title_return_400(self, create_category):
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_product"
        data = {
            "title": "",
            "description": "321",
            "categories": [categories.id],
            "unit_price": 321,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 0

    def test_create_product_with_no_description_return_400(self, create_category):
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_product"
        data = {
            "title": "123",
            "description": "",
            "categories": [categories.id],
            "unit_price": 321,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 0

    def test_create_product_with_no_categories_return_400(self):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [],
            "unit_price": 321,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 0

    def test_create_product_with_no_unit_price_return_400(self, create_category):
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": None,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 0

    def test_create_product_with_no_on_stock_return_400(self, create_category):
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": None,
            "is_available": False,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 0

    def test_create_product_with_no_is_available_return_400(self, create_category):
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": 0,
            "is_available": None,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 0


@pytest.mark.django_db
class TestProductDetailViewInvalidData:
    def test_update_product_with_no_title_return_400(
        self, create_category, create_product
    ):
        product_obj = create_product
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        data = {
            "title": "",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 1
        product_after_request = Product.objects.get(id=product_obj.id)
        assert product_after_request == product_obj

    def test_update_product_with_no_description_return_400(
        self, create_category, create_product
    ):
        product_obj = create_product
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        data = {
            "title": "123",
            "description": "",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 1
        product_after_request = Product.objects.get(id=product_obj.id)
        assert product_after_request == product_obj

    def test_update_product_with_no_categories_return_400(self, create_product):
        product_obj = create_product
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        data = {
            "title": "123",
            "description": "",
            "categories": [],
            "unit_price": 123,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 1
        product_after_request = Product.objects.get(id=product_obj.id)
        assert product_after_request == product_obj

    def test_update_product_with_no_unit_price_return_400(
        self, create_category, create_product
    ):
        product_obj = create_product
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": None,
            "on_stock": 0,
            "is_available": False,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 1
        product_after_request = Product.objects.get(id=product_obj.id)
        assert product_after_request == product_obj

    def test_update_product_with_no_on_stock_return_400(
        self, create_category, create_product
    ):
        product_obj = create_product
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": None,
            "is_available": False,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 1
        product_after_request = Product.objects.get(id=product_obj.id)
        assert product_after_request == product_obj

    def test_update_product_with_no_is_available_return_400(
        self, create_category, create_product
    ):
        product_obj = create_product
        categories = create_category
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_product"
        data = {
            "title": "123",
            "description": "123",
            "categories": [categories.id],
            "unit_price": 123,
            "on_stock": 0,
            "is_available": None,
        }

        response = client.put(
            reverse(url, kwargs={"product_id": product_obj.id}),
            data=data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 1
        product_after_request = Product.objects.get(id=product_obj.id)
        assert product_after_request == product_obj


@pytest.mark.django_db
class TestPromotionViewPermissions:
    def test_promotion_view_return_promotions_for_anonymous_user(
        self, create_promotion
    ):
        client = APIClient()
        url = "get_create_promotion"
        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Promotion.objects.count() == 1

    def test_if_anonymous_user_create_promotion_return_403(self):
        client = APIClient()
        url = "get_create_promotion"
        data = {
            "title": "123",
            "description": "123",
            "start_date": "2023-09-09",
            "end_date": "2023-09-10",
            "discount_percentage": 15,
        }

        response = client.post(reverse(url), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Promotion.objects.count() == 0

    def test_promotion_view_return_promotions_for_authenticated_user(
        self, create_promotion
    ):
        user, client = create_authenticated_user(username="123", password="123")
        url = "get_create_promotion"
        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Promotion.objects.count() == 1

    def test_if_authenticated_user_create_promotion_return_403(self):
        user, client = create_authenticated_user(username="123", password="123")
        url = "get_create_promotion"
        data = {
            "title": "123",
            "description": "123",
            "start_date": "2023-09-09",
            "end_date": "2023-09-10",
            "discount_percentage": 15,
        }

        response = client.post(reverse(url), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Promotion.objects.count() == 0

    def test_promotion_view_return_promotions_for_admin_user(self, create_promotion):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_promotion"
        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Promotion.objects.count() == 1

    def test_if_admin_user_create_promotion_return_201(self):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "get_create_promotion"
        data = {
            "title": "123",
            "description": "123",
            "start_date": "2023-09-09",
            "end_date": "2023-09-10",
            "discount_percentage": 15,
        }

        response = client.post(reverse(url), data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Promotion.objects.count() == 1


@pytest.mark.django_db
class TestPromotionDetailViewPermissions:
    def test_if_anonymous_user_update_promotion_return_403(self, create_promotion):
        promotion_obj = create_promotion
        client = APIClient()
        url = "update_delete_promotion"
        data = {
            "title": "321",
            "description": "321",
            "start_date": "2023-09-08",
            "end_date": "2023-09-11",
            "discount_percentage": 10,
        }

        response = client.put(
            reverse(url, kwargs={"promotion_id": promotion_obj.id}),
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Promotion.objects.count() == 1
        promotion_after_request = Promotion.objects.get(id=promotion_obj.id)
        assert promotion_obj == promotion_after_request

    def test_if_anonymous_user_delete_promotion_return_403(self, create_promotion):
        promotion_obj = create_promotion
        client = APIClient()
        url = "update_delete_promotion"
        response = client.delete(
            reverse(url, kwargs={"promotion_id": promotion_obj.id})
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Promotion.objects.count() == 1

    def test_authenticated_user_update_promotion_return_403(self, create_promotion):
        promotion_obj = create_promotion
        user, client = create_authenticated_user(username="123", password="123")
        url = "update_delete_promotion"
        data = {
            "title": "321",
            "description": "321",
            "start_date": "2023-09-08",
            "end_date": "2023-09-11",
            "discount_percentage": 10,
        }

        response = client.put(
            reverse(url, kwargs={"promotion_id": promotion_obj.id}),
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Promotion.objects.count() == 1
        promotion_after_request = Promotion.objects.get(id=promotion_obj.id)
        assert promotion_after_request == promotion_obj

    def test_if_authenticated_user_delete_promotion_return_403(self, create_promotion):
        promotions = create_promotion
        user, client = create_authenticated_user(username="123", password="123")
        url = "update_delete_promotion"
        response = client.delete(reverse(url, kwargs={"promotion_id": promotions.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Promotion.objects.count() == 1

    def test_if_admin_user_update_promotion_return_200(self, create_promotion):
        promotion_obj = create_promotion
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_promotion"
        data = {
            "title": "321",
            "description": "321",
            "start_date": "2023-09-08",
            "end_date": "2023-09-11",
            "discount_percentage": 10,
        }

        response = client.put(
            reverse(url, kwargs={"promotion_id": promotion_obj.id}),
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Promotion.objects.count() == 1
        updated_promotion = Promotion.objects.get(id=promotion_obj.id)
        for field in ["title", "description", "discount_percentage"]:
            assert getattr(updated_promotion, field) == data[field]
        assert str(updated_promotion.start_date) == data["start_date"]
        assert str(updated_promotion.end_date) == data["end_date"]

    def test_if_admin_user_delete_promotion_return_204(self, create_promotion):
        promotions = create_promotion
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_promotion"
        response = client.delete(reverse(url, kwargs={"promotion_id": promotions.id}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Promotion.objects.count() == 0


@pytest.mark.django_db
class TestPromotionViewInvalidData:
    def test_if_admin_user_create_promotion_with_no_title_return_400(self):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmai.com"
        )
        url = "get_create_promotion"
        data = {
            "title": "",
            "description": "321",
            "start_date": "2023-09-08",
            "end_date": "2023-09-11",
            "discount_percentage": 10,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Promotion.objects.count() == 0

    def test_if_admin_user_create_promotion_with_no_discount_percentage(self):
        user, client = create_admin_user(
            username="123", password="123", email="123@gmai.com"
        )
        url = "get_create_promotion"
        data = {
            "title": "123",
            "description": "321",
            "start_date": "2023-09-08",
            "end_date": "2023-09-11",
            "discount_percentage": None,
        }

        response = client.post(reverse(url), data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Promotion.objects.count() == 0


@pytest.mark.django_db
class TestPromotionDetailViewInvalidData:
    def test_if_admin_user_update_promotion_with_no_title(self, create_promotion):
        promotion_obj = create_promotion
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_promotion"
        data = {
            "title": "",
            "description": "321",
            "start_date": "2023-09-08",
            "end_date": "2023-09-11",
            "discount_percentage": 10,
        }

        response = client.put(
            reverse(url, kwargs={"promotion_id": promotion_obj.id}),
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Promotion.objects.count() == 1
        update_promotion = Promotion.objects.get(id=promotion_obj.id)
        assert promotion_obj == update_promotion

    def test_if_admin_user_update_promotion_with_no_discount_percentage_return_400(
        self, create_promotion
    ):
        promotion_obj = create_promotion
        user, client = create_admin_user(
            username="123", password="123", email="123@gmail.com"
        )
        url = "update_delete_promotion"
        data = {
            "title": "123",
            "description": "321",
            "start_date": "2023-09-08",
            "end_date": "2023-09-11",
            "discount_percentage": None,
        }

        response = client.put(
            reverse(url, kwargs={"promotion_id": promotion_obj.id}),
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Promotion.objects.count() == 1
        update_promotion = Promotion.objects.get(id=promotion_obj.id)
        assert promotion_obj == update_promotion


@pytest.mark.django_db
class TestCartHistoryViewPermissions:
    def test_cart_history_view_return_403_for_anonymous_user(
        self, create_completed_cart
    ):
        cart_obj, _ = create_completed_cart
        client = APIClient()
        url = "get_cart_history"

        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Cart.objects.count() == 1

    def test_cart_history_view_return_carts_for_authenticated_user(
        self, create_not_completed_cart
    ):
        cart_obj, user = create_not_completed_cart
        client = APIClient()
        client.force_authenticate(user=user)
        url = "get_cart_history"

        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Cart.objects.count() == 1

    def test_cart_history_view_return_carts_for_admin_user(
        self, create_not_completed_cart_with_admin_user
    ):
        cart_obj, user = create_not_completed_cart_with_admin_user
        client = APIClient()
        client.force_authenticate(user=user)
        url = "get_cart_history"

        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_200_OK
        assert Cart.objects.count() == 1


@pytest.mark.django_db
class TestCartViewPermissions:
    def test_cart_view_return_403_for_anonymous_user(self):
        client = APIClient()
        url = "manage_cart"

        response = client.get(reverse(url))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cart_view_return_cart_details_for_authenticated_user(
        self, create_not_completed_cart
    ):
        cart_obj, user = create_not_completed_cart
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"

        response = client.get(reverse(url))

        assert Cart.objects.count() == 1
        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_create_cart_item_return_200(
        self, create_not_completed_cart, create_product
    ):
        cart_obj, user = create_not_completed_cart
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        created_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert created_cart_item.product_id == data["product"]
        assert created_cart_item.quantity == data["quantity"]
        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_update_cart_item_return_200(
        self, create_product, create_cart_item_fxt
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 50}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert updated_cart_item.product_id == data["product"]
        assert updated_cart_item.quantity == data["quantity"]
        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_delete_cart_item_return_200(
        self, create_product, create_cart_item_fxt
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 0}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_200_OK

    def test_cart_view_return_cart_details_for_admin_user(
        self, create_not_completed_cart_with_admin_user
    ):
        cart_obj, user = create_not_completed_cart_with_admin_user
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"

        response = client.get(reverse(url))

        assert Cart.objects.count() == 1
        assert response.status_code == status.HTTP_200_OK

    def test_if_admin_user_create_cart_item_return_200(
        self, create_not_completed_cart_with_admin_user, create_product
    ):
        cart_obj, user = create_not_completed_cart_with_admin_user
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        created_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert created_cart_item.product_id == data["product"]
        assert created_cart_item.quantity == data["quantity"]
        assert response.status_code == status.HTTP_200_OK

    def test_if_admin_user_update_cart_item_return_200(
        self, create_product, create_cart_item_fxt_with_admin_user
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt_with_admin_user
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 100}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert updated_cart_item.product_id == data["product"]
        assert updated_cart_item.quantity == data["quantity"]
        assert response.status_code == status.HTTP_200_OK

    def test_if_admin_user_delete_cart_item_return_200(
        self, create_product, create_cart_item_fxt_with_admin_user
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt_with_admin_user
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 0}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCartViewInvalidData:
    def test_if_authenticated_user_create_cart_item_with_invalid_product_id_return_400(
        self, create_not_completed_cart
    ):
        cart_obj, user = create_not_completed_cart
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": 9999, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_create_cart_item_with_missing_product_id_return_400(
        self, create_not_completed_cart
    ):
        cart_obj, user = create_not_completed_cart
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": None, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_create_cart_item_with_negative_product_id_return_400(
        self, create_not_completed_cart
    ):
        cart_obj, user = create_not_completed_cart
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": -1, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_create_cart_item_with_invalid_quantity_return_400(
        self, create_not_completed_cart, create_product
    ):
        cart_obj, user = create_not_completed_cart
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 5001}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_create_cart_item_with_negative_quantity_return_400(
        self, create_not_completed_cart, create_product
    ):
        cart_obj, user = create_not_completed_cart
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": -1}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_create_cart_item_with_no_quantity_return_400(
        self, create_product, create_not_completed_cart
    ):
        cart_obj, user = create_not_completed_cart
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": None}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_create_cart_item_with_wrong_quantity_return_400(
        self, create_product, create_not_completed_cart
    ):
        cart_obj, user = create_not_completed_cart
        product_obj = create_product
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 124}

        response = client.put(reverse(url), data=data, format="json")

        assert CartItem.objects.count() == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_update_cart_item_with_missing_product_id(
        self, create_cart_item_fxt, create_product
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        initial_quantity = cart_item_obj.quantity
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": None, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert initial_quantity == updated_cart_item.quantity
        assert initial_on_stock == product_obj.on_stock
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_update_cart_item_with_invalid_product_id_return_400(
        self, create_cart_item_fxt, create_product
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        initial_quantity = cart_item_obj.quantity
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": 9999, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert initial_quantity == updated_cart_item.quantity
        assert initial_on_stock == product_obj.on_stock
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_update_cart_item_with_negative_product_id_return_400(
        self, create_cart_item_fxt, create_product
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        initial_quantity = cart_item_obj.quantity
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": -1, "quantity": 10}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert initial_quantity == updated_cart_item.quantity
        assert initial_on_stock == product_obj.on_stock
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_update_cart_item_with_missing_quantity_return_400(
        self, create_cart_item_fxt, create_product
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        initial_quantity = cart_item_obj.quantity
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": None}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert initial_quantity == updated_cart_item.quantity
        assert initial_on_stock == product_obj.on_stock
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_update_cart_item_with_invalid_quantity_return_400(
        self, create_cart_item_fxt, create_product
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        initial_quantity = cart_item_obj.quantity
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": 9999}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert initial_quantity == updated_cart_item.quantity
        assert initial_on_stock == product_obj.on_stock
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_authenticated_user_update_cart_item_with_negative_quantity_return_400(
        self, create_cart_item_fxt, create_product
    ):
        cart_item_obj, user, cart_obj = create_cart_item_fxt
        initial_quantity = cart_item_obj.quantity
        product_obj = create_product
        initial_on_stock = product_obj.on_stock
        client = APIClient()
        client.force_authenticate(user=user)
        url = "manage_cart"
        data = {"product": product_obj.id, "quantity": -1}

        response = client.put(reverse(url), data=data, format="json")

        updated_cart_item = CartItem.objects.get(cart_id=cart_obj.id)
        assert CartItem.objects.count() == 1
        assert initial_quantity == updated_cart_item.quantity
        assert initial_on_stock == product_obj.on_stock
        assert response.status_code == status.HTTP_400_BAD_REQUEST
