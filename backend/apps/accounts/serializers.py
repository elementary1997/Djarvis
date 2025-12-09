"""
Serializers для User модели и аутентификации.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer для User model."""
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'bio',
            'avatar',
            'total_exercises_completed',
            'total_points',
            'current_streak',
            'longest_streak',
            'theme',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'total_exercises_completed',
            'total_points',
            'current_streak',
            'longest_streak',
            'created_at',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer для регистрации пользователей."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        """ Проверяет совпадение паролей."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        """Создает нового пользователя."""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Расширенный serializer для профиля пользователя."""
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'bio',
            'avatar',
            'total_exercises_completed',
            'total_points',
            'current_streak',
            'longest_streak',
            'last_activity_date',
            'theme',
            'email_notifications',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'email',
            'total_exercises_completed',
            'total_points',
            'current_streak',
            'longest_streak',
            'last_activity_date',
            'created_at',
            'updated_at',
        ]
