"""
Views for progress tracking.
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Avg, Sum

from .models import ModuleProgress, LessonProgress, DailyStreak
from .serializers import (
    ModuleProgressSerializer,
    LessonProgressSerializer,
    DailyStreakSerializer,
    MarkLessonCompleteSerializer
)
from apps.courses.models import Module, Lesson
from apps.exercises.models import ExerciseAttempt


class UserProgressOverviewView(APIView):
    """
    Get overall user progress statistics.
    
    GET /api/progress/overview/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Module progress
        total_modules = Module.objects.filter(is_published=True).count()
        completed_modules = ModuleProgress.objects.filter(
            user=user,
            is_completed=True
        ).count()
        in_progress_modules = ModuleProgress.objects.filter(
            user=user,
            is_started=True,
            is_completed=False
        ).count()
        
        # Lesson progress
        total_lessons = Lesson.objects.filter(
            module__is_published=True,
            is_published=True
        ).count()
        completed_lessons = LessonProgress.objects.filter(
            user=user,
            is_completed=True
        ).count()
        
        # Exercise stats
        total_exercises_attempted = ExerciseAttempt.objects.filter(
            user=user
        ).values('exercise').distinct().count()
        
        exercises_passed = ExerciseAttempt.objects.filter(
            user=user,
            is_passed=True
        ).values('exercise').distinct().count()
        
        # Daily streak
        streak, _ = DailyStreak.objects.get_or_create(user=user)
        
        # Time statistics
        total_time_spent = LessonProgress.objects.filter(
            user=user
        ).aggregate(total=Sum('time_spent'))['total'] or 0
        
        return Response({
            'modules': {
                'total': total_modules,
                'completed': completed_modules,
                'in_progress': in_progress_modules,
                'completion_rate': (completed_modules / total_modules * 100) if total_modules > 0 else 0
            },
            'lessons': {
                'total': total_lessons,
                'completed': completed_lessons,
                'completion_rate': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            },
            'exercises': {
                'attempted': total_exercises_attempted,
                'passed': exercises_passed,
                'success_rate': (exercises_passed / total_exercises_attempted * 100) if total_exercises_attempted > 0 else 0
            },
            'streak': {
                'current': streak.current_streak,
                'longest': streak.longest_streak,
                'last_activity': streak.last_activity_date
            },
            'time_spent_minutes': total_time_spent // 60,
            'user_level': user.level,
            'user_xp': user.total_xp
        }, status=status.HTTP_200_OK)


class ModuleProgressListView(generics.ListAPIView):
    """
    List user's module progress.
    
    GET /api/progress/modules/
    """
    serializer_class = ModuleProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ModuleProgress.objects.filter(
            user=self.request.user
        ).select_related('module')


class LessonProgressListView(generics.ListAPIView):
    """
    List user's lesson progress.
    
    GET /api/progress/lessons/
    """
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        module_id = self.request.query_params.get('module_id')
        queryset = LessonProgress.objects.filter(
            user=self.request.user
        ).select_related('lesson')
        
        if module_id:
            queryset = queryset.filter(lesson__module_id=module_id)
        
        return queryset


class MarkLessonCompleteView(APIView):
    """
    Mark a lesson as completed.
    
    POST /api/progress/lessons/complete/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = MarkLessonCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        lesson_id = serializer.validated_data['lesson_id']
        time_spent = serializer.validated_data.get('time_spent', 0)
        
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create lesson progress
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        if time_spent > 0:
            progress.time_spent += time_spent
        
        # Mark as completed
        progress.mark_completed()
        
        # Update streak
        streak, _ = DailyStreak.objects.get_or_create(user=request.user)
        streak.update_streak()
        
        return Response(
            LessonProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )


class DailyStreakView(generics.RetrieveAPIView):
    """
    Get user's daily streak.
    
    GET /api/progress/streak/
    """
    serializer_class = DailyStreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        streak, _ = DailyStreak.objects.get_or_create(user=self.request.user)
        return streak


class LeaderboardView(APIView):
    """
    Get leaderboard of top users.
    
    GET /api/progress/leaderboard/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from apps.accounts.models import User
        from apps.accounts.serializers import UserProfileSerializer
        
        # Top users by XP
        top_users = User.objects.filter(
            is_active=True
        ).order_by('-total_xp', '-level')[:10]
        
        leaderboard = []
        for rank, user in enumerate(top_users, start=1):
            completed_exercises = ExerciseAttempt.objects.filter(
                user=user,
                is_passed=True
            ).values('exercise').distinct().count()
            
            leaderboard.append({
                'rank': rank,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'avatar': user.avatar.url if user.avatar else None,
                    'level': user.level,
                    'total_xp': user.total_xp
                },
                'completed_exercises': completed_exercises
            })
        
        # Current user's rank
        user_rank = User.objects.filter(
            is_active=True,
            total_xp__gt=request.user.total_xp
        ).count() + 1
        
        return Response({
            'leaderboard': leaderboard,
            'user_rank': user_rank
        }, status=status.HTTP_200_OK)
