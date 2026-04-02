import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from catalog.serializers import ProductSerializer

from .models import PayoutRequest, User, UserProfile
from .utils import normalize_email_address


NICKNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class NormalizedEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        return super().to_internal_value(normalize_email_address(data))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "is_seller")


class RegisterSerializer(serializers.Serializer):
    email = NormalizedEmailField()
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=True,
        min_length=3,
        max_length=30,
        error_messages={
            "required": "Nickname is required",
            "blank": "Nickname is required",
            "min_length": "Nickname must be between 3 and 30 characters",
            "max_length": "Nickname must be between 3 and 30 characters",
        },
    )
    is_seller = serializers.BooleanField(required=False, default=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_nickname(self, value):
        nickname = value.strip()
        if not nickname:
            raise serializers.ValidationError("Nickname is required")
        if not NICKNAME_PATTERN.fullmatch(nickname):
            raise serializers.ValidationError(
                "Nickname may only contain letters, numbers, underscores, hyphens, and dots"
            )
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("Nickname is already taken")
        return nickname

    def validate(self, attrs):
        user = User(email=attrs["email"])
        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages})
        return attrs


class LoginSerializer(serializers.Serializer):
    username = NormalizedEmailField()
    password = serializers.CharField(write_only=True)


class UserUpdateSerializer(serializers.Serializer):
    is_seller = serializers.BooleanField()


class PayoutRequestCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class PayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = ("id", "amount", "status", "created_at")


class PublicSellerProfileSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    products = ProductSerializer(many=True)
