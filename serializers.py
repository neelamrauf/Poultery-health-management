"""
Serializers for user registration and login.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

VALID_ROLES = ('Farmer', 'Admin')


class RegisterSerializer(serializers.ModelSerializer):
    """Handles new user registration."""

    password = serializers.CharField(write_only=True, min_length=1)
    role = serializers.ChoiceField(choices=VALID_ROLES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Handles login credential input."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
