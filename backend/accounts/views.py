from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from .serializers import (
    LoginSerializer,
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

        user = User.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            is_seller=serializer.validated_data.get("is_seller", True),
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
        if not user or not user.check_password(password):
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
