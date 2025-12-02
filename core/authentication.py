from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
try:  # make this import optional so management commands don't fail when not using Passage
    from passageidentity import Passage, PassageError
    _HAS_PASSAGE = True
except Exception:  # pragma: no cover - environment dependent
    Passage = None
    PassageError = Exception
    _HAS_PASSAGE = False

# from passageidentity.openapi_client.models import UserInfo
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import User

PASSAGE_APP_ID = getattr(settings, 'PASSAGE_APP_ID', None)
PASSAGE_API_KEY = getattr(settings, 'PASSAGE_API_KEY', None)
psg = None
if _HAS_PASSAGE and PASSAGE_APP_ID and PASSAGE_API_KEY:
    try:
        psg = Passage(PASSAGE_APP_ID, PASSAGE_API_KEY)
    except Exception:
        # If Passage cannot be initialized, keep psg None and authentication will not use it.
        psg = None


class TokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'core.authentication.TokenAuthentication'
    name = 'tokenAuth'
    match_subclasses = True
    priority = -1

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix='Bearer',
        )


class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request) -> tuple[User, None]:
        if not request.headers.get('Authorization'):
            return None

        token = request.headers.get('Authorization').split()[1]
        # If passage is not configured, we cannot authenticate via token
        if psg is None:
            return None
        psg_user_id: str = self._get_user_id(token)
        user: User = self._get_or_create_user(psg_user_id)

        return (user, None)

    def _get_or_create_user(self, psg_user_id) -> User:
        try:
            user: User = User.objects.get(passage_id=psg_user_id)
        except ObjectDoesNotExist:
            psg_user = psg.user.get(psg_user_id)
            user: User = User.objects.create_user(
                passage_id=psg_user.id,
                email=psg_user.email,
            )

        return user

    def _get_user_id(self, token) -> str:
        try:
            psg_user_id: str = psg.auth.validate_jwt(token)
        except PassageError as e:
            # print(e)
            raise AuthenticationFailed(e.message) from e

        return psg_user_id
