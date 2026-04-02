from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .managers import UserManager
from .utils import normalize_email_address


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, db_index=True)
    is_seller = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    balance_pending = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_available = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
            )
        ]

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        normalized_email = normalize_email_address(self.email)
        if self.email != normalized_email:
            self.email = normalized_email
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                updated_fields = set(update_fields)
                updated_fields.add("email")
                kwargs["update_fields"] = updated_fields
        super().save(*args, **kwargs)


class PayoutRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"

    id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payout_requests",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payout_requests"

    def __str__(self) -> str:
        return f"PayoutRequest #{self.pk}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    nickname = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Public seller nickname",
    )

    class Meta:
        db_table = "user_profiles"

    def __str__(self) -> str:
        return self.nickname or self.user.email
