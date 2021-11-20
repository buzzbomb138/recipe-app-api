from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredients
from recipes.serializers import IngredientsSerializer


INGREDIENTS_URL = reverse('recipes:ingredients-list')


class PublicIngredientsAPITests(TestCase):
    """test the publically available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def login_required(self):
        """test the login is required to access the endpoint"""
        resp = self.client.get(INGREDIENTS_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """test the private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londondappdev.com', 'testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """test retrieving a list of ingredients"""
        Ingredients.objects.create(user=self.user, name='salt')
        Ingredients.objects.create(user=self.user, name='sugar')
        resp = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientsSerializer(ingredients, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test that only ingredients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@adsf.com', 'testpass')
        Ingredients.objects.create(user=user2, name='cinnamon')
        ingredient = Ingredients.objects.create(
            user=self.user, name='vanilla')
        resp = self.client.get(INGREDIENTS_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], ingredient.name)
