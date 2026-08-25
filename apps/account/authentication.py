from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied


def enforce_csrf(request):
    check = CSRFCheck(lambda request: None)

    check.process_request(request)

    reason = check.process_view(
        request,
        None,
        (),
        {}
    )

    if reason:
        raise PermissionDenied(
            f"CSRF failed: {reason}"
        )

class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):

        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get(
                settings.SIMPLE_JWT_ACCESS_COOKIE
            )
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        user = self.get_user(validated_token)

        return user, validated_token