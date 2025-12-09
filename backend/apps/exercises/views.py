"""
Views for exercises app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Exercise, Hint, Submission, HintUsage
from .serializers import (
    ExerciseSerializer, ExerciseListSerializer,
    HintSerializer, SubmissionSerializer,
    SubmissionCreateSerializer, HintUsageSerializer,
)
from apps.sandbox.tasks import execute_ansible_code


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Exercise model."""
    
    queryset = Exercise.objects.filter(is_published=True).prefetch_related('hints')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExerciseListSerializer
        return ExerciseSerializer
    
    def get_queryset(self):
        """Filter exercises by lesson if lesson_slug is provided."""
        queryset = super().get_queryset()
        lesson_slug = self.request.query_params.get('lesson_slug')
        
        if lesson_slug:
            queryset = queryset.filter(lesson__slug=lesson_slug)
        
        return queryset
    
    @extend_schema(
        summary="List exercises",
        description="Get list of all published exercises, optionally filtered by lesson.",
        parameters=[
            OpenApiParameter(
                name='lesson_slug',
                description='Filter exercises by lesson slug',
                required=False,
                type=str
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get exercise details",
        description="Get detailed information about a specific exercise.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Submit exercise solution",
        description="Submit code for exercise evaluation.",
        request=SubmissionCreateSerializer,
        responses={201: SubmissionSerializer},
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, slug=None):
        """Submit exercise solution."""
        exercise = self.get_object()
        
        # Create submission
        serializer = SubmissionCreateSerializer(
            data={'exercise': exercise.id, 'code': request.data.get('code')},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()
        
        # Execute code asynchronously
        execute_ansible_code.delay(submission.id)
        
        return Response(
            SubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Reveal hint",
        description="Reveal a specific hint for the exercise.",
        responses={200: HintSerializer},
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='hints/(?P<hint_order>[0-9]+)/reveal'
    )
    def reveal_hint(self, request, slug=None, hint_order=None):
        """Reveal a hint for the exercise."""
        exercise = self.get_object()
        
        # Get hint
        hint = get_object_or_404(
            Hint,
            exercise=exercise,
            order=hint_order
        )
        
        # Create hint usage record
        hint_usage, created = HintUsage.objects.get_or_create(
            user=request.user,
            hint=hint
        )
        
        serializer = HintSerializer(hint, context={'request': request})
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Submission model."""
    
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return submissions for current user."""
        queryset = Submission.objects.filter(
            user=self.request.user
        ).select_related('exercise', 'exercise__lesson')
        
        # Filter by exercise if provided
        exercise_id = self.request.query_params.get('exercise_id')
        if exercise_id:
            queryset = queryset.filter(exercise_id=exercise_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-submitted_at')
    
    @extend_schema(
        summary="List user submissions",
        description="Get list of authenticated user's submissions.",
        parameters=[
            OpenApiParameter(
                name='exercise_id',
                description='Filter by exercise ID',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='status',
                description='Filter by submission status',
                required=False,
                type=str
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
