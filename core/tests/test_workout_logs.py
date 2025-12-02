from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from core.models.user import User
from core.models.workout_log import WorkoutLog
from django.utils import timezone


class WorkoutLogAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='u1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(email='u2@example.com', password='pass1234')

    def test_create_log_requires_auth(self):
        payload = {'workoutSlug': 'run-5k', 'caloriesBurned': 250, 'durationMinutes': 35}
        res = self.client.post('/workouts/log/', payload, format='json')
        self.assertEqual(res.status_code, 401)  # unauthorized

    def test_create_and_retrieve_logs(self):
        self.client.force_authenticate(self.user)

        payload = {
            'workoutSlug': 'run-5k',
            'caloriesBurned': 250.5,
            'durationMinutes': 35,
        }
        res = self.client.post('/workouts/log/', payload, format='json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn('id', data)
        self.assertEqual(float(data['calories_burned']), 250.5)
        self.assertEqual(float(data['duration_minutes']), 35.0)

        # create one for second user
        self.client.force_authenticate(self.user2)
        payload2 = {'workoutSlug': 'yoga', 'caloriesBurned': 100, 'durationMinutes': 45}
        self.client.post('/workouts/log/', payload2, format='json')

        # list logs for user2 (only 1)
        res2 = self.client.get('/workouts/logs/')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(len(res2.json()), 1)

        # list logs for user1
        self.client.force_authenticate(self.user)
        res1 = self.client.get('/workouts/logs/')
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(len(res1.json()), 1)

    def test_validation_errors(self):
        self.client.force_authenticate(self.user)
        payload = {'workoutSlug': 'test', 'caloriesBurned': -5, 'durationMinutes': 0}
        res = self.client.post('/workouts/log/', payload, format='json')
        self.assertEqual(res.status_code, 400)
        body = res.json()
        self.assertIn('calories_burned', body)
        self.assertIn('duration_minutes', body)
