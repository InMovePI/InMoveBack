from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User
from unittest.mock import patch


class ChatUserFieldsTests(APITestCase):
    def setUp(self):
        self.email = 'chatuser@example.com'
        self.password = 'ChatPass123!'
        self.user = User.objects.create_user(email=self.email, password=self.password,
                                            objetivo='emagrecimento', meta_peso='72.50')

    def _login(self):
        token_resp = self.client.post('/api/token/', {'email': self.email, 'password': self.password}, format='json')
        access = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_chat_includes_user_fields_in_system_prompt(self):
        self._login()

        messages_captured = {}

        class FakeMessage:
            def __init__(self, content):
                self.content = content

        class FakeChoice:
            def __init__(self, content):
                self.message = {'content': content}

        class FakeResp:
            def __init__(self, content):
                self.choices = [type('C', (), {'message': {'content': content}})]

        def fake_chat_completion(self, messages=None, max_tokens=None):
            # capture the system message content
            system_msg = messages[0]['content']
            messages_captured['system'] = system_msg
            return FakeResp('{"treino": "ok", "dieta": "ok"}')

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass
            def chat_completion(self, messages=None, max_tokens=None):
                return fake_chat_completion(self, messages=messages, max_tokens=max_tokens)

        with patch('core.views.chat.InferenceClient', new=FakeClient):
            resp = self.client.post('/api/chat/', {'message': 'Teste'}, format='json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertIn('Objetivo', messages_captured['system'])
            self.assertIn('Meta de peso', messages_captured['system'])