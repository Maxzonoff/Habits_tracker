from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserProfileSerializer, UserRegisterSerializer

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    POST /users/register/
    """

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "token": token.key,
                "message": "Регистрация прошла успешно!",
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(ObtainAuthToken):
    """
    Авторизация (получение токена).
    POST /users/login/
    Тело запроса: {"username": "...", "password": "..."}
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
            }
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и редактирование профиля.
    GET /users/profile/    — посмотреть
    PUT/PATCH /users/profile/ — изменить
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Возвращаем текущего пользователя.
        """
        return self.request.user
