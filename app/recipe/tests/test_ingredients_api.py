"""
Test for ingredients_api
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Ingredient,
    Recipe,
)
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredients_id):
    """Return detail URL for ingredient"""
    return reverse('recipe:ingredient-detail', args=[ingredients_id])


def create_user(email='user@example.com', password='passtest123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTest(TestCase):
    """Test the publicly available or unauthenticated ingredients apis"""
    def setUp(self):
        """Test unauthenticated APIs requests."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """Test the authorized user ingredients."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        # self.assertEqual(len(res), 2)

    def test_ingredients_limited_to_user(self):
        """
        Test list of ingredients is limited to auth user.
        """
        user2 = create_user(
            email='user2@example.com',
            password='testpass1242342'
        )
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Paper')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient object"""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Ingredient.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_ingredients_assigned_to_recipe(self):
        """Test filtering ingredients by those assigned to recipe"""
        in1 = Ingredient.objects.create(
            user=self.user,
            name='Apples'
        )
        in2 = Ingredient.objects.create(
            user=self.user,
            name='Turkey'
        )
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('13.32'),
            user=self.user
        )
        recipe.ingredients.add(in1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients return a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('54.2'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('34.2'),
            user=self.user
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
