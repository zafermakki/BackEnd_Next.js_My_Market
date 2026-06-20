import random
import string
from datetime import timedelta
from django.db import transaction
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.timezone import now

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, PendingUser



VERIFICATION_CODE_TTL = timedelta(minutes=1)


def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(email, code, subject):
    message = f"Your verification code is: {code}\nPlease enter it within 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def issue_verification_code(obj):
    code = generate_verification_code()
    obj.verification_code = code
    obj.code_expiration = now() + VERIFICATION_CODE_TTL
    obj.save(update_fields=["verification_code", "code_expiration"])
    return code


class PublicAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []


class ResendVerificationEmailView(PublicAPIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"message": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response(
                {"message": "This email is not registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if pending_user.code_expiration and pending_user.code_expiration > now():
            return Response(
                {"message": "Please wait before requesting a new code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        code = issue_verification_code(pending_user)
        send_verification_email(
            email=pending_user.email,
            code=code,
            subject="Your verification code"
        )

        return Response(
            {"message": "The verification code has been sent again. Please check your email."},
            status=status.HTTP_200_OK
        )


class VerifyCodeView(PublicAPIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"message": "Email and code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response(
                {"message": "This email is not registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not pending_user.is_code_valid(code):
            return Response(
                {"message": "The verification code is not valid or expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user = User.objects.create(
                username=pending_user.username,
                email=pending_user.email,
                password=pending_user.password,
                is_active=True,
                is_email_verified=True,
            )
            pending_user.delete()

        return Response(
            {"message": "The account was successfully activated."},
            status=status.HTTP_200_OK
        )


class RequestPasswordResetView(PublicAPIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        if not email:
            return Response(
                {"message": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not new_password or len(new_password) < 8:
            return Response(
                {"message": "The password should be 8 characters or more."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "This email is not registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.code_expiration = now() + VERIFICATION_CODE_TTL
        user.temp_password = make_password(new_password)
        user.save(update_fields=["verification_code", "code_expiration", "temp_password"])

        send_verification_email(
            email=user.email,
            code=verification_code,
            subject="Password reset"
        )

        return Response(
            {"message": "Verification code has been sent."},
            status=status.HTTP_200_OK
        )


class VerifyAndResetPasswordView(PublicAPIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"message": "Email and code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "This email is not registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if (
            not user.verification_code
            or not user.code_expiration
            or user.verification_code != code
            or user.code_expiration < now()
        ):
            return Response(
                {"message": "The verification code is not valid or expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.temp_password:
            return Response(
                {"message": "There is no new password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.password = user.temp_password
        user.temp_password = None
        user.verification_code = None
        user.code_expiration = None
        user.save(update_fields=["password", "temp_password", "verification_code", "code_expiration"])

        return Response(
            {"message": "The password has been successfully updated."},
            status=status.HTTP_200_OK
        )


class ClientRegisterView(PublicAPIView):
    def post(self, request):

        PendingUser.objects.filter(
            created_at__lt=now() - timedelta(days=1)
        ).delete()

        data = request.data
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        if not email or not username or not password:
            return Response(
                {"message": "Username, email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 8:
            return Response(
                {"message": "The password must be 8 characters or more."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "This email is already registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        pending_user, created = PendingUser.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "password": make_password(password),
            }
        )

        if not created:
            if pending_user.code_expiration and pending_user.code_expiration > now():
                return Response(
                    {"message": "Please wait before requesting a new code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            pending_user.username = username
            pending_user.password = make_password(password)
            pending_user.save(update_fields=["username", "password"])

        code = issue_verification_code(pending_user)
        send_verification_email(
            email=pending_user.email,
            code=code,
            subject="Your verification code"
        )

        return Response(
            {"message": "A verification code has been sent. Please enter it within 5 minutes."},
            status=status.HTTP_200_OK
        )


class ClientLoginView(PublicAPIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request=request, username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": str(user.id),
                "email": user.email,
                "username": user.username,
            },
            status=status.HTTP_200_OK
        )


class ClientLogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"message": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"message": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )