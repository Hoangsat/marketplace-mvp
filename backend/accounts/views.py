from django.db import transaction
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from catalog.models import Product, filter_publicly_available_products
from common.permissions import IsAuthenticatedSeller

from .models import PayoutRequest, User, UserProfile
from .serializers import (
    LoginSerializer,
    PayoutRequestCreateSerializer,
    PayoutRequestSerializer,
    PublicSellerProfileSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            detail = next(iter(serializer.errors.values()))[0]
            return Response({"detail": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                is_seller=serializer.validated_data.get("is_seller", True),
            )
            UserProfile.objects.create(
                user=user,
                nickname=serializer.validated_data["nickname"],
            )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            detail = next(iter(serializer.errors.values()))[0]
            return Response({"detail": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()
        if not user or not user.is_active or not user.check_password(password):
            return Response(
                {"detail": "Incorrect email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = str(AccessToken.for_user(user))
        return Response(
            {"access_token": token, "token_type": "bearer"},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            detail = next(iter(serializer.errors.values()))[0]
            return Response({"detail": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        request.user.is_seller = serializer.validated_data["is_seller"]
        request.user.save(update_fields=["is_seller"])
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class PayoutRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedSeller]
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = PayoutRequestCreateSerializer(data=request.data)
        if not serializer.is_valid():
            detail = next(iter(serializer.errors.values()))[0]
            return Response({"detail": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        amount = serializer.validated_data["amount"]
        with transaction.atomic():
            seller = User.objects.select_for_update().filter(id=request.user.id).first()
            if seller.balance_available < amount:
                return Response(
                    {"detail": "Insufficient available balance"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            seller.balance_available -= amount
            seller.save(update_fields=["balance_available"])
            payout_request = PayoutRequest.objects.create(
                seller=seller,
                amount=amount,
            )

        return Response(
            PayoutRequestSerializer(payout_request).data,
            status=status.HTTP_201_CREATED,
        )


class PublicSellerProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, nickname):
        profile = UserProfile.objects.select_related("user").filter(
            nickname=nickname,
            user__is_seller=True,
        ).first()
        if not profile:
            return Response(
                {"detail": "Seller not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        products = filter_publicly_available_products(
            Product.objects.select_related(
                "category",
                "platform",
                "platform__category",
                "offer_type",
                "seller",
                "seller__profile",
            )
        ).filter(
            seller_id=profile.user_id,
            stock__gt=0,
        )
        data = PublicSellerProfileSerializer(
            {
                "nickname": profile.nickname,
                "products": products,
            },
            context={"request": request},
        ).data
        return Response(data, status=status.HTTP_200_OK)
