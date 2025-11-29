from django.conf import settings
try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.models.chat import ChatMessage, ChatSession
from core.serializers.chat import ChatMessageSerializer
from core.serializers.session import ChatSessionSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.authentication import TokenAuthentication as PassageTokenAuthentication
import logging

logger = logging.getLogger(__name__)

class ChatAPIView(APIView):
    """
    Chatbot de personal trainer e nutricionista virtual.
    Funciona para usuários logados ou visitantes.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response({"error": "Mensagem vazia"}, status=400)

        # Pegando o usuário logado
        user = request.user if request.user.is_authenticated else None
        user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
        
        if user is None:
            try:
                jwt_auth = JWTAuthentication()
                jwt_result = jwt_auth.authenticate(request)
                if jwt_result:
                    user, token = jwt_result
                    logger.debug('Authenticated user via JWT in ChatAPIView: %s', getattr(user, 'email', None))
            except Exception:
                pass

        if user is None:
            try:
                passage_auth = PassageTokenAuthentication()
                passage_result = passage_auth.authenticate(request)
                if passage_result:
                    user, _ = passage_result
                    logger.debug('Authenticated user via Passage token in ChatAPIView: %s', getattr(user, 'email', None))
            except Exception:
                pass

        # Monta os dados do usuário se logado
        user_data = {}
        if user:
            user_data = {
                "Nome": getattr(user, "name", "Não informado"),
                "Peso": getattr(user, "peso_kg", "Não informado"),
                "Altura": getattr(user, "altura_cm", "Não informado"),
                "Objetivo": getattr(user, "objetivo", "Não informado"),
                "Meta_peso": getattr(user, "meta_peso", "Não informado"),
                "Dias_treino": getattr(user, "dias_treino", "Não informado"),
                "Grupo_foco": getattr(user, "grupo_foco", "Não informado"),
            }

        user_data_str = ", ".join(f"{k}: {v}" for k, v in user_data.items() if v and v != "Não informado")

        # Detectar intenção ANTES do prompt
        message_lower = user_message.lower()
        
        treino_keywords = ['treino', 'exercicio', 'exercício', 'musculação', 'academia', 'workout', 'malhar']
        dieta_keywords = ['dieta', 'alimentação', 'alimentacao', 'comida', 'comer', 'refeição', 'refeicao', 'nutricao', 'nutrição', 'cardápio']
        
        solicita_treino = any(keyword in message_lower for keyword in treino_keywords)
        solicita_dieta = any(keyword in message_lower for keyword in dieta_keywords)

        # Prompt SUPER SIMPLES
        if solicita_treino and not solicita_dieta:
            # SÓ TREINO
            system_prompt = f"""Você é personal trainer. Crie um plano de treino em português brasileiro.

Dados: {user_data_str}

Responda apenas no formato JSON:
{{"treino": "seu plano de treino aqui", "dieta": ""}}

Plano de treino:
- Segunda: Liste exercícios com séries e repetições
- Quarta: Liste exercícios com séries e repetições  
- Sexta: Liste exercícios com séries e repetições

Seja motivador e use os dados fornecidos."""

        elif solicita_dieta and not solicita_treino:
            # SÓ DIETA
            system_prompt = f"""Você é nutricionista. Crie um plano alimentar em português brasileiro.

Dados: {user_data_str}

Responda apenas no formato JSON:
{{"treino": "", "dieta": "seu plano alimentar aqui"}}

Plano alimentar:
- Café da manhã: alimentos e calorias
- Almoço: alimentos e calorias
- Jantar: alimentos e calorias
- Lanches: alimentos e calorias

Seja motivador e use os dados fornecidos."""

        elif solicita_treino and solicita_dieta:
            # AMBOS
            system_prompt = f"""Você é personal trainer e nutricionista. Crie treino E dieta em português brasileiro.

Dados: {user_data_str}

Responda apenas no formato JSON:
{{"treino": "plano de treino", "dieta": "plano alimentar"}}

Seja breve, motivador e use os dados fornecidos."""

        else:
            # CONVERSA
            system_prompt = f"""Você é FitAI, assistente fitness amigável.

Dados do usuário: {user_data_str if user_data_str else "Sem dados"}

Responda brevemente e com simpatia em português brasileiro.

Formato JSON:
{{"treino": "", "dieta": "sua resposta amigável aqui"}}

Seja simpática e pergunte como pode ajudar."""

        try:
            if InferenceClient is None:
                return Response(
                    {"error": "Hugging Face client não disponível."},
                    status=501
                )

            client = InferenceClient(
                model=settings.HF_MODEL,
                token=settings.HF_TOKEN
            )

            resposta = client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,  # Reduzido para evitar bugs
                temperature=0.4,  # Bem conservador
                top_p=0.7,
            )

            reply_text = resposta.choices[0].message["content"]

            # Salva mensagens no banco
            session = None
            if user:
                session_id = request.data.get('session_id')
                if session_id:
                    try:
                        s = ChatSession.objects.get(pk=session_id, user=user)
                        session = s
                    except ChatSession.DoesNotExist:
                        session = None
                
                if session is None:
                    title = (user_message[:60] + '...') if len(user_message) > 60 else user_message
                    session = ChatSession.objects.create(user=user, title=title)

                ChatMessage.objects.create(user=user, role="user", content=user_message, session=session)
                ChatMessage.objects.create(user=user, role="assistant", content=reply_text, session=session)

            # Tenta converter em JSON
            import json
            try:
                reply_json = json.loads(reply_text)
                data = reply_json
                if session:
                    data['session_id'] = session.id
                return Response(data)
            except json.JSONDecodeError:
                # Tenta extrair JSON
                import re
                json_match = re.search(r'\{.*?\}', reply_text, re.DOTALL)
                if json_match:
                    try:
                        reply_json = json.loads(json_match.group(0))
                        data = reply_json
                        if session:
                            data['session_id'] = session.id
                        return Response(data)
                    except:
                        pass
                
                # Fallback
                data = {"treino": "", "dieta": reply_text}
                if session:
                    data['session_id'] = session.id
                return Response(data)

        except Exception as e:
            logger.error(f"Error in ChatAPIView: {str(e)}")
            return Response({"error": str(e)}, status=500)


class ChatSessionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sessions = ChatSession.objects.filter(user=user).order_by('-updated_at')
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        title = request.data.get('title', 'Nova conversa')
        session = ChatSession.objects.create(user=user, title=title)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatSessionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(pk=session_id, user=request.user)
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, session_id):
        try:
            session = ChatSession.objects.get(pk=session_id, user=request.user)
            title = request.data.get('title')
            if title is not None:
                session.title = title
                session.save()
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, session_id):
        return self.patch(request, session_id)

    def delete(self, request, session_id):
        try:
            session = ChatSession.objects.get(pk=session_id, user=request.user)
            session.delete()
            return Response({'message': 'Session deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatSessionMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        user = request.user
        try:
            session = ChatSession.objects.get(pk=session_id, user=user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        messages = session.messages.order_by('created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)