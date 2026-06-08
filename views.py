"""
Auth views: Register and Login.
"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import LoginSerializer, RegisterSerializer

User = get_user_model()


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/
    Creates a new user and returns 201 with the username and role.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Returns a JWT access token and the user's role on valid credentials.
    Returns 401 on invalid credentials.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = AccessToken.for_user(user)
        return Response(
            {'access': str(token), 'role': user.role},
            status=status.HTTP_200_OK,
        )
