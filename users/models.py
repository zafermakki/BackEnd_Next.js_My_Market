import uuid
from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    username = models.CharField(
        max_length=250,
        # unique=True,
        validators=[UnicodeUsernameValidator()]
    )

    email = models.EmailField(
        max_length=250,
        unique=True
    )

    is_email_verified = models.BooleanField(default=False)

    verification_code = models.CharField(
        max_length=6,
        null=True,
        blank=True
    )

    code_expiration = models.DateTimeField(
        null=True,
        blank=True
    )

    temp_password = models.CharField(
        max_length=128,
        null=True,
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # REQUIRED_FIELDS = ['email']
    # USERNAME_FIELD = 'username'

    class Meta:
        db_table = "users"


class PendingUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    username = models.CharField(max_length=150)

    email = models.EmailField(
        max_length=250,
        unique=True
    )

    password = models.CharField(max_length=128)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    verification_code = models.CharField(
        max_length=6,
        null=True,
        blank=True
    )

    code_expiration = models.DateTimeField(
        null=True,
        blank=True
    )

    def is_expired(self):
        return now() > self.created_at + timedelta(minutes=5)

    def is_code_valid(self, code):
        return (
            self.verification_code
            and self.code_expiration
            and self.verification_code == code
            and now() < self.code_expiration
        )