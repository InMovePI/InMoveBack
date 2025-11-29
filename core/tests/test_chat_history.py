from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User, ChatMessage
from unittest.mock import patch


class ChatHistoryTests(APITestCase):
    def setUp(self):
        self.email = 'historyuser@example.com'
        self.password = 'HistoryPass123!'
        self.user = User.objects.create_user(email=self.email, password=self.password,
                                            objetivo='tonificacao', meta_peso='80.00')

    def _login(self):
        token_resp = self.client.post('/api/token/', {'email': self.email, 'password': self.password}, format='json')
        access = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_post_chat_saves_messages_and_history_is_retrievable(self):
        self._login()

        # Provide a simple fake client that returns a fixed response
        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass
            def chat_completion(self, messages=None, max_tokens=None):
                class FakeResp:
                    def __init__(self, content):
                        self.choices = [type('C', (), {'message': {'content': content}})]
                # return predictable JSON
                return FakeResp('{"treino": "ok", "dieta": "ok"}')

        with patch('core.views.chat.InferenceClient', new=FakeClient):
            resp = self.client.post('/api/chat/', {'message': 'Teste historico'}, format='json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            session_id = resp.data.get('session_id')
            self.assertIsNotNone(session_id)

        # Ensure messages were saved
        saved = ChatMessage.objects.filter(user=self.user).order_by('created_at')
        # Should be 2 messages: user and assistant
        self.assertEqual(saved.count(), 2)
        self.assertEqual(saved[0].role, 'user')
        self.assertEqual(saved[0].content, 'Teste historico')
        self.assertEqual(saved[1].role, 'assistant')

        # GET history (sessions)
        history_resp = self.client.get('/api/chat/history/')
        self.assertEqual(history_resp.status_code, status.HTTP_200_OK)
        # Should contain one session
        self.assertEqual(len(history_resp.data), 1)
        session = history_resp.data[0]
        self.assertEqual(session['last_message']['role'], 'assistant')

        # GET messages for the session
        messages_resp = self.client.get(f'/api/chat/sessions/{session_id}/')
        self.assertEqual(messages_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(messages_resp.data), 2)
        self.assertEqual(messages_resp.data[0]['role'], 'user')
        self.assertEqual(messages_resp.data[0]['content'], 'Teste historico')

    def test_history_requires_authentication(self):
        # Without login should be 401
        resp = self.client.get('/api/chat/history/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_see_others_history(self):
        # Create second user and login as first
        other = User.objects.create_user(email='other@example.com', password='OtherPass1!')
        self._login()

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass
            def chat_completion(self, messages=None, max_tokens=None):
                class FakeResp:
                    def __init__(self, content):
                        self.choices = [type('C', (), {'message': {'content': content}})]
                return FakeResp('{"treino": "ok", "dieta": "ok"}')

        with patch('core.views.chat.InferenceClient', new=FakeClient):
            self.client.post('/api/chat/', {'message': 'Minha conversa'}, format='json')

        # Now login as the other user and check history
        token_resp = self.client.post('/api/token/', {'email': other.email, 'password': 'OtherPass1!'}, format='json')
        access = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        history_resp = self.client.get('/api/chat/history/')
        self.assertEqual(history_resp.status_code, status.HTTP_200_OK)
        # Other user should see no sessions
        self.assertEqual(len(history_resp.data), 0)
