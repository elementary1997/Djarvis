"""
Views for exercises.
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Exercise, ExerciseAttempt
from .serializers import (
    ExerciseListSerializer,
    ExerciseDetailSerializer,
    ExerciseAttemptSerializer,
    HintRequestSerializer
)


class ExerciseListView(generics.ListAPIView):
    """
    List exercises for a lesson.
    
    GET /api/exercises/
    """
    serializer_class = ExerciseListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson', 'difficulty']
    
    def get_queryset(self):
        return Exercise.objects.filter(is_published=True).order_by('lesson', 'order')


class ExerciseDetailView(generics.RetrieveAPIView):
    """
    Get exercise detail.
    
    GET /api/exercises/{id}/
    """
    queryset = Exercise.objects.filter(is_published=True)
    serializer_class = ExerciseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExerciseAttemptListView(generics.ListAPIView):
    """
    List user's attempts for an exercise.
    
    GET /api/exercises/{exercise_id}/attempts/
    """
    serializer_class = ExerciseAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        exercise_id = self.kwargs.get('exercise_id')
        return ExerciseAttempt.objects.filter(
            exercise_id=exercise_id,
            user=self.request.user
        ).order_by('-created_at')


class GetHintView(APIView):
    """
    Get a hint for an exercise.
    
    POST /api/exercises/{exercise_id}/hint/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, exercise_id):
        serializer = HintRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        hint_index = serializer.validated_data['hint_index']
        
        try:
            exercise = Exercise.objects.get(id=exercise_id, is_published=True)
        except Exercise.DoesNotExist:
            return Response(
                {"error": "Exercise not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        hints = exercise.hints
        if hint_index >= len(hints):
            return Response(
                {"error": "Hint index out of range"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "hint": hints[hint_index],
            "hint_index": hint_index,
            "total_hints": len(hints)
        }, status=status.HTTP_200_OK)
