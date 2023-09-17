import pytest
import uuid
from django.contrib.auth import get_user_model
from django.http import Http404
from django.urls import reverse
from store.models import Category
from store.logic import get_list_categories, get_category_details
from rest_framework.test import APIClient
from rest_framework import status

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
    return admin_user


@pytest.mark.django_db
class TestCategoryLogic:

    def test_get_list_categories(self, create_category):
        categories = get_list_categories()

        assert len(categories) == 1
        assert all(category.title == '123' and category.description == '123' for category in categories)

    def test_get_category_details(self, create_category):
        category_obj = create_category
        category_details = get_category_details(category_id=category_obj.id)

        assert category_details.id == category_obj.id
        assert category_details.title == '123'
        assert category_details.description == '123'

    def test_get_categories_details_invalid_data(self):
        with pytest.raises(Http404):
            get_category_details(category_id=99999)

    def test_get_categories_details_missing_data(self):
        with pytest.raises(Http404):
            get_category_details(category_id=None)





