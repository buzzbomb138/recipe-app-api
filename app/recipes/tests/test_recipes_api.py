from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipes, Ingredients, Tags
from recipes.serializers import RecipesSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipes:recipes-list')


def detail_url(recipe_id):
    """return recipe detail URL"""
    return reverse('recipes:recipes-detail', args=[recipe_id])


def sample_tag(user, name='main course'):
    """create and return a sample tag"""
    return Tags.objects.create(user=user, name=name)


def sample_ingredient(user, name='chocolate'):
    """create and return a sample ingredient"""
    return Ingredients.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    """create and return a sample recipe"""
    defaults = {'title': 'sample recipe', 'time_minutes': 10, 'price': 5.00}
    return Recipes.objects.create(user=user, **defaults)


class PublicRecipesAPITests(TestCase):
    """test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test that unauthentication is required"""
        resp = self.client.get(RECIPES_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesAPITests(TestCase):
    """test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('asdf@asdf.com', 'asdfasdf')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        resp = self.client.get(RECIPES_URL)
        recipes = Recipes.objects.all().order_by('-id')
        serializer = RecipesSerializer(recipes, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user(
            'asdfasdf@dsfgasf.com', 'asdkfjndksf')
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        resp = self.client.get(RECIPES_URL)
        recipes = Recipes.objects.filter(user=self.user)
        serializer = RecipesSerializer(recipes, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data, serializer.data)

    def test_view_recipe_detail(self):
        """test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        resp = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(resp.data, serializer.data)
