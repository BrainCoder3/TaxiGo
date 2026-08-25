from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import enforce_csrf

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
)
from .tokens import email_verification_token
from django.middleware.csrf import get_token

# Create your views here.




COOKIE_KWARGS = {
    "httponly": True,
    "secure": not settings.DEBUG,
    "samesite": "Lax",
}


class CSRFTokenView(APIView):
    permission_classes =[AllowAny]

    def get(self,request):
        token = get_token(request)

        return Response({
            "csrfToken":token
        })


def set_auth_cookies(response, refresh):
    response.set_cookie(
        settings.SIMPLE_JWT_ACCESS_COOKIE,
        str(refresh.access_token),
        max_age=int(
            settings.SIMPLE_JWT[
                "ACCESS_TOKEN_LIFETIME"
            ].total_seconds()
        ),
        **COOKIE_KWARGS,
    )

    response.set_cookie(
        settings.SIMPLE_JWT_REFRESH_COOKIE,
        str(refresh),
        max_age=int(
            settings.SIMPLE_JWT[
                "REFRESH_TOKEN_LIFETIME"
            ].total_seconds()
        ),
        **COOKIE_KWARGS,
    )


class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        enforce_csrf(request)
        serializer = UserRegistrationSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        send_verification_email(user)

        return Response(
            {
                "detail": (
                    "Compte created. "
                    "please check In your emails."
                ),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED
        )

    
class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        enforce_csrf(request)
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "detail":
                    "Username and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request=request,
            username=email,
            password=password
        )

        if user is None:
            return Response(
                {
                    "detail":
                    "invalid data"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        if user.email_verified_at is None:
            return Response(
                {
                    "detail":
                    "please check your email "
                    "before getting connected"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)

        response = Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK
        )

        set_auth_cookies(response, refresh)

        return response


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(serializer.data)



class RefreshView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        enforce_csrf(request)
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT_REFRESH_COOKIE
        )

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)

        except TokenError:
            return Response(
                {
                    "detail":
                    "Refresh token invalid or expired."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response(
            {"detail": "Token refreshed successfully"},
            status=status.HTTP_200_OK
        )

        set_auth_cookies(response, refresh)

        return response


class LogoutView(APIView):


    permission_classes = [IsAuthenticated]

    def post(self, request):

        enforce_csrf(request)
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT_REFRESH_COOKIE
        )

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()

            except TokenError:
                pass

        response = Response(
            status=status.HTTP_204_NO_CONTENT
        )

        response.delete_cookie(
            settings.SIMPLE_JWT_ACCESS_COOKIE
        )

        response.delete_cookie(
            settings.SIMPLE_JWT_REFRESH_COOKIE
        )

        return response



def send_verification_email(user):

    uidb64 = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = email_verification_token.make_token(user)

    verify_url = (
        f"{settings.BACKEND_BASE_URL}"
        f"/api/v1/auth/verify-email/{uidb64}/{token}/"
    )

    print("\n\n========== TAXIGO VERIFY URL ==========")
    print(verify_url)
    print("=======================================\n\n")

    send_mail(
        subject="Vérifiez votre adresse email",
        message=(
            f"Bonjour {user.username},\n\n"
            "Bienvenue sur TaxiGo.\n\n"
            "Cliquez sur le lien suivant pour vérifier "
            "votre adresse email :\n"
            f"{verify_url}\n\n"
            "Si vous n'avez pas créé ce compte, "
            "ignorez simplement cet email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    
class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):

        try:
            uid = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = User.objects.get(pk=uid)

        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            user = None

        if user is None:
            return Response(
                {
                    "detail":
                    "Invalid verification Link"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.email_verified_at is not None:
            return Response(
                {
                    "detail":
                    "This email is already verified"
                },
                status=status.HTTP_200_OK
            )

        if not email_verification_token.check_token(
            user,
            token
        ):
            return Response(
                {
                    "detail":
                    "Verification link is invalid or expired"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.email_verified_at = timezone.now()

        user.save(
            update_fields=["email_verified_at"]
        )

        return Response(
            {
                "detail":
                "Email verified successfully."
            },
            status=status.HTTP_200_OK
        )