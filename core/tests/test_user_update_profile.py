from rest_framework import status
from rest_framework.test import APITestCase
from core.models import User


class UserUpdateProfileTests(APITestCase):
    def setUp(self):
        self.email = 'updateprofile@example.com'
        self.password = 'UpdatePass123!'
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def _login(self):
        token_resp = self.client.post('/api/token/', {'email': self.email, 'password': self.password}, format='json')
        access = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_patch_update_objetivo_and_meta_peso(self):
        self._login()
        url = '/api/usuarios/me/'
        payload = {
            'objetivo': 'manutencao',
            'meta_peso': '75.50',
        }
        resp = self.client.patch(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        # Refresh user
        self.user.refresh_from_db()
        self.assertEqual(self.user.objetivo, 'manutencao')
        self.assertEqual(str(self.user.meta_peso), '75.50')
