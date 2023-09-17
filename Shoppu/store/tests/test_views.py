import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Category

User = get_user_model()


@pytest.fixture
def create_category():
    category_obj = Category.objects.create(title='123', description='123')
    return category_obj


def create_authenticated_user(username, password):
    user = User.objects.create_user(username=username, password=password)
    client = APIClient()
    client.login(username=username, password=password)
    return user, client


def create_admin_user(username, password, email):
    admin_user = User.objects.create_superuser(
        username=username, password=password, email=email)
    client = APIClient()
    client.login(username=username, password=password, email=email)
    return admin_user, client


@pytest.mark.django_db
class TestCategoryViewsPermissions:
    def test_category_view_return_categories_for_anonymous_user(self, create_category):
        client = APIClient()
        url_pattern = 'get_create_category'
        response = client.get(reverse(url_pattern))

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1

    def test_if_anonymous_user_create_category_return_403(self):
        client = APIClient()
        url_pattern = 'get_create_category'
        data = {
            'title': '123',
            'description': '123'
        }

        response = client.post(reverse(url_pattern), data=data, format='json')
        assert Category.objects.count() == 0
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_category_view_return_categories_for_authenticated_user(self, create_category):
        user, client = create_authenticated_user(username='123', password='123')
        url_pattern = 'get_create_category'
        response = client.get(reverse(url_pattern))

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1

    def test_if_authenticated_user_create_category_return_403(self):
        user, client = create_authenticated_user(username='123', password='123')
        url_pattern = 'get_create_category'
        data = {
            'title': '123',
            'description': '123'
        }
        response = client.post(reverse(url_pattern), data=data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 0

    def test_category_view_return_categories_for_admin_user(self, create_category):
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'get_create_category'
        response = client.get(reverse(url_pattern))

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1

    def test_category_view_create_category_for_admin_user(self):
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'get_create_category'
        data = {
            'title': '123',
            'description': '123'
        }

        response = client.post(reverse(url_pattern), data=data, format='json')
        assert Category.objects.count() == 1
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestCategoryDetailViewPermission:
    def test_if_anonymous_user_update_category_return_403(self, create_category):
        category_obj = create_category
        client = APIClient()
        url_pattern = 'update_delete_category'
        data = {
            'title': '1234',
            'description': '1234'
        }

        response = client.put(reverse(url_pattern, kwargs={'category_id': category_obj.id}), data=data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_id_anonymous_user_delete_category_return_403(self, create_category):
        category_obj = create_category
        client = APIClient()
        url_pattern = 'update_delete_category'
        response = client.delete(reverse(url_pattern, kwargs={'category_id': category_obj.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_if_authenticated_user_update_category_return_403(self, create_category):
        category_obj = create_category
        user, client = create_authenticated_user(username='123', password='123')
        url_pattern = 'update_delete_category'
        data = {
            'title': '1234',
            'description': '1234'
        }
        response = client.put(reverse(url_pattern, kwargs={'category_id': category_obj.id}), data=data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_if_authenticated_user_delete_category_return_403(self, create_category):
        category_obj = create_category
        user, client = create_authenticated_user(username='123', password='123')
        url_pattern = 'update_delete_category'
        response = client.put(reverse(url_pattern, kwargs={'category_id': category_obj.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.count() == 1

    def test_if_admin_user_update_category_return_200(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'update_delete_category'
        data = {
            'title': '1234',
            'description': '1234'
        }
        response = client.put(reverse(url_pattern, kwargs={'category_id': category_obj.id}), data=data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert Category.objects.count() == 1

    def test_if_admin_user_delete_category_return_204(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'update_delete_category'
        response = client.delete(reverse(url_pattern, kwargs={'category_id': category_obj.id}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Category.objects.count() == 0


@pytest.mark.django_db
class TestCategoryViewInvalidData:
    def test_create_category_with_no_title_return_400(self):
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'get_create_category'
        data = {
            'title': '',
            'description': '1234'
        }
        response = client.post(reverse(url_pattern), data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 0

    def test_create_category_with_no_description_return_400(self):
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'get_create_category'
        data = {
            'title': '1234',
            'description': ''
        }
        response = client.post(reverse(url_pattern), data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 0


@pytest.mark.django_db
class TestCategoryDetailViewInvalidData:
    def test_update_category_with_no_title_return_400(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'update_delete_category'
        data = {
            'title': '',
            'description': '1234'
        }
        response = client.put(reverse(url_pattern, kwargs={'category_id': category_obj.id}), data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 1

    def test_update_category_with_no_description_return_400(self, create_category):
        category_obj = create_category
        user, client = create_admin_user(username='123', password='123', email='123@gmail.com')
        url_pattern = 'update_delete_category'
        data = {
            'title': '1234',
            'description': ''
        }
        response = client.put(reverse(url_pattern, kwargs={'category_id': category_obj.id}), data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.count() == 1




