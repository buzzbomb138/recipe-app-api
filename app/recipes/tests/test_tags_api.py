from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipes.serializers import TagSerializer


TAGS_URL = reverse('recipes:tag-list')


class PublicTagsAPITest(TestCase):
    """test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required for retrieving tags"""

        resp = self.client.get(TAGS_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com', 'test123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """test retrieving tags"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='dessert')
        resp = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@londondappdev.com',
            'pass123'
        )
        Tag.objects.create(user=user2, name='fruity')
        tag = Tag.objects.create(user=self.user, name='salty')

        resp = self.client.get(TAGS_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """test creating a new tag"""
        payload = {'name': 'test'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """test creating a new tag with invalid payload"""
        payload = {'name': ''}
        resp = self.client.post(TAGS_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
