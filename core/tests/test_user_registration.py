from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from core.serializers.user import UserCreateSerializer


class UserRegistrationTests(APITestCase):
    def test_serializer_minimal_payload_creates_user(self):
        payload = {
            'email': 'regtest1@example.com',
            'name': 'Reg Test',
            'password': 'Reg12345',
        }
        serializer = UserCreateSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_api_register_endpoint_allows_anonymous_post(self):
        payload = {
            'email': 'rege2test@example.com',
            'name': 'Reg Test 2',
            'password': 'Reg12345',
        }
        response = self.client.post('/api/usuarios/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        # Password should not be returned
        self.assertNotIn('password', response.data)
        # User created in db
        user = User.objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_list_requires_authentication(self):
        response = self.client.get('/api/usuarios/')
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_register_then_login_and_me(self):
        # Register
        payload = {
            'email': 'regfulltest@example.com',
            'name': 'Reg Full Test',
            'password': 'RegStrong123!',
        }
        response = self.client.post('/api/usuarios/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertNotIn('password', response.data)

        # Login via token endpoint; simplejwt uses 'username' (which maps to email in custom USER model)
        token_resp = self.client.post('/api/token/', {'email': payload['email'], 'password': payload['password']}, format='json')
        self.assertEqual(token_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_resp.data)
        access = token_resp.data['access']

        # Use the access token to fetch /api/usuarios/me
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        me_resp = self.client.get('/api/usuarios/me/')
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK, me_resp.data)
        self.assertEqual(me_resp.data['email'], payload['email'])
