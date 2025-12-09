"""
Views для аутентификации и управления пользователями.
"""
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """API endpoint для регистрации новых пользователей."""
    
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                'user': UserSerializer(user).data,
                'message': 'User registered successfully. Please login.',
            },
            status=status.HTTP_201_CREATED
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint для просмотра и обновления профиля."""
    
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Возвращает текущего авторизованного пользователя."""
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint для просмотра пользователей (только чтение)."""
    
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['total_points', 'created_at']
    ordering = ['-total_points']
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Возвращает топ пользователей по очкам."""
        top_users = self.get_queryset().order_by('-total_points')[:100]
        serializer = self.get_serializer(top_users, many=True)
        return Response(serializer.data)
