from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        # 1. On regarde d'abord si un token Bearer est fourni
        header = self.get_header(request)

        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            # 2. Sinon on cherche le JWT dans le cookie
            raw_token = request.COOKIES.get(
                settings.SIMPLE_JWT_ACCESS_COOKIE
            )

        # Aucun token trouvé
        if raw_token is None:
            return None

        # Vérifie signature + expiration du JWT
        validated_token = self.get_validated_token(raw_token)

        # Retrouve l'utilisateur correspondant
        user = self.get_user(validated_token)

        return user, validated_token