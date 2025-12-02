from datetime import date, timedelta, time

from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from core.models.meal import Meal, IngredientEntry

from unittest.mock import patch


class MealTests(APITestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(email='mealtest@example.com', password='pass1234')
        self.client.force_authenticate(user=self.user)

    def test_search_food_returns_list(self):
        # create FoodItems in DB
        from core.models.fooditem import FoodItem

        fi1 = FoodItem.objects.create(name='Apple', calories=52.0, protein=0.3, carbs=14.0, fat=0.2)
        fi2 = FoodItem.objects.create(name='Banana', calories=89.0, protein=1.1, carbs=23.0, fat=0.3)

        resp = self.client.get('/meals/search-food/?q=app')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertTrue(any(item.get('name') == fi1.name for item in resp.data))

    def test_search_food_filters_to_brazil_by_default(self):
        # create items: one Brazil, one Portugal (pt), one US, one unknown
        from core.models.fooditem import FoodItem

        FoodItem.objects.create(name='Banana BR', calories=89.0, protein=1.1, carbs=23.0, fat=0.3, country='Brasil', languages='pt')
        FoodItem.objects.create(name='Banana PT', calories=88.0, protein=1.0, carbs=22.0, fat=0.2, country='Portugal', languages='pt')
        FoodItem.objects.create(name='Banana US', calories=90.0, protein=1.0, carbs=24.0, fat=0.4, country='United States', languages='en')
        FoodItem.objects.create(name='Banana X', calories=95.0, protein=1.2, carbs=25.0, fat=0.5, country='', languages='')

        resp = self.client.get('/meals/search-food/?q=banana')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [item.get('id') for item in resp.data]
        # Should include Brazil and Portuguese-language item
        self.assertTrue(any(item.get('name') == 'Banana BR' for item in resp.data))
        self.assertTrue(any(item.get('name') == 'Banana PT' for item in resp.data))
        # Should NOT include US or unknown
        self.assertFalse(any(item.get('name') == 'Banana US' for item in resp.data))
        self.assertFalse(any(item.get('name') == 'Banana X' for item in resp.data))

    def test_search_food_country_param_variants(self):
        # Product with Brazil in countries and product with US
        products = [
            {'code': '10', 'product_name': 'Açúcar BR', 'brands': 'ACBrand', 'countries': 'Brasil', 'languages': ['pt'], 'nutriments': {'energy-kcal_100g': 400}},
            {'code': '11', 'product_name': 'Sugar US', 'brands': 'USBrand', 'countries': 'United States', 'languages': ['en'], 'nutriments': {'energy-kcal_100g': 390}},
        ]
        from core.models.fooditem import FoodItem
        FoodItem.objects.create(name='Açúcar BR', calories=400.0, country='Brasil', languages='pt')
        FoodItem.objects.create(name='Sugar US', calories=390.0, country='United States', languages='en')

        # country param variants should treat as Brazil
        for country_param in ('BR', 'br', 'BRA', 'Brazil', 'Brasil'):
            resp = self.client.get(f'/meals/search-food/?q=açúcar&country={country_param}')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            names = [item.get('name') for item in resp.data]
            self.assertIn('Açúcar BR', names)
            self.assertNotIn('Sugar US', names)

    def test_create_meal_creates_entries_and_links_user(self):
        # Create two food items in DB with predictable nutrients
        from core.models.fooditem import FoodItem

        fi1 = FoodItem.objects.create(name='Apple', calories=50.0, protein=1.0, carbs=12.0, fat=0.5)
        fi2 = FoodItem.objects.create(name='Banana', calories=50.0, protein=1.0, carbs=12.0, fat=0.5)

        payload = {
            'title': 'Breakfast',
            'date': str(timezone.localdate()),
            'time': '08:30:00',
            'ingredients': [
                {'food_name': str(fi1.id), 'weight_grams': 100},
                {'food_name': str(fi2.id), 'weight_grams': 100},
            ],
        }

        resp = self.client.post('/meals/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        # check DB rows
        meals = Meal.objects.filter(user=self.user)
        self.assertEqual(meals.count(), 1)
        meal = meals.first()
        self.assertEqual(meal.title, 'Breakfast')

        ingredients = IngredientEntry.objects.filter(meal=meal)
        self.assertEqual(ingredients.count(), 2)

        self.assertAlmostEqual(meal.total_calories, 100.0)
        self.assertAlmostEqual(meal.total_protein, 2.0)

    def test_list_by_date_and_delete(self):
        # create a meal for this user and another user
        today = timezone.localdate()
        meal1 = Meal.objects.create(user=self.user, title='M1', date=today, time=time(9, 0))

        other = User.objects.create_user(email='other@example.com', password='pass1234')
        Meal.objects.create(user=other, title='OtherMeal', date=today, time=time(10, 0))

        # list by date should only return user's meals
        resp = self.client.get(f'/meals/?date={today.isoformat()}')
        # tests support paginated responses; normalize to results list
        data = resp.data.get('results') if isinstance(resp.data, dict) else resp.data
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Should only contain meal1
        self.assertTrue(any(m.get('title') == meal1.title for m in data))

        # delete meal
        resp = self.client.delete(f'/meals/{meal1.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # delete other's meal should not be allowed
        self.client.force_authenticate(user=other)
        resp = self.client.delete(f'/meals/{meal1.id}/')
        # meal already deleted, expect 404
        self.assertIn(resp.status_code, (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN))

    def test_weekly_summary(self):
        # create meals for three different days in the current week
        today = timezone.localdate()
        monday = today - timedelta(days=today.weekday())

        Meal.objects.create(user=self.user, title='MonMeal', date=monday, time=time(8, 0), total_calories=100, total_protein=5, total_carbs=10, total_fat=2)
        Meal.objects.create(user=self.user, title='WedMeal', date=monday + timedelta(days=2), time=time(12, 0), total_calories=200, total_protein=10, total_carbs=20, total_fat=5)
        Meal.objects.create(user=self.user, title='SunMeal', date=monday + timedelta(days=6), time=time(19, 0), total_calories=50, total_protein=2, total_carbs=5, total_fat=1)

        resp = self.client.get('/meals/weekly-summary/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('days', resp.data)
        self.assertIn('week_totals', resp.data)
        # Check week_totals sums
        totals = resp.data['week_totals']
        self.assertAlmostEqual(totals['calories'], 350)
