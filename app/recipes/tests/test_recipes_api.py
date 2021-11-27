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
        self.user = get_user_model().objects.create_user(
            'asdf@asdf.com',
            'asdfasdf'
        )
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

    def test_create_basic_recipe(self):
        """test creating recipe"""
        payload = {'title': 'cheesecake', 'time_minutes': 30, 'price': 5.00}
        resp = self.client.post(RECIPES_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipes.objects.get(id=resp.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='vegan')
        tag2 = sample_tag(user=self.user, name='dessert')
        payload = {'title': 'avocado lime cheesecake', 'tags': [
            tag1.id, tag2.id], 'time_minutes': 60, 'price': 20.00}
        resp = self.client.post(RECIPES_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipes.objects.get(id=resp.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """test creating a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='prawns')
        ingredient2 = sample_ingredient(user=self.user, name='ginger')
        payload = {'title': 'thai prawn red curry', 'ingredients': [
            ingredient1.id, ingredient2.id], 'time_minutes': 20, 'price': 7.00}
        resp = self.client.post(RECIPES_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipes.objects.get(id=resp.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='curry')
        payload = {'title': 'chicken tika', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {'title': 'spaghetti carbonara',
                   'time_minutes': 25, 'price': 5.00}
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
