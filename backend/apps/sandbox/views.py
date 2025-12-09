"""
Views for sandbox code execution.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django.utils import timezone
import uuid
import logging

from .models import SandboxSession
from .serializers import (
    SandboxSessionSerializer,
    ExecuteCodeSerializer,
    ExecutionResultSerializer
)
from .services import DockerExecutor, AnsibleValidator, TestRunner
from apps.exercises.models import Exercise, ExerciseAttempt

logger = logging.getLogger(__name__)


class SandboxThrottle(UserRateThrottle):
    """Custom throttle for sandbox execution."""
    rate = '10/minute'


class CreateSandboxView(APIView):
    """
    Create a new sandbox session.
    
    POST /api/sandbox/create/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Check if user already has an active session
        active_session = SandboxSession.objects.filter(
            user=user,
            status='running'
        ).first()
        
        if active_session and not active_session.is_expired:
            return Response(
                SandboxSessionSerializer(active_session).data,
                status=status.HTTP_200_OK
            )
        
        # Create new session
        session_name = str(uuid.uuid4())[:8]
        executor = DockerExecutor()
        
        try:
            container_id, container_name = executor.create_sandbox(
                user.id,
                session_name
            )
            
            session = SandboxSession.objects.create(
                user=user,
                container_id=container_id,
                container_name=container_name,
                status='running'
            )
            
            return Response(
                SandboxSessionSerializer(session).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            return Response(
                {"error": "Failed to create sandbox"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExecuteCodeView(APIView):
    """
    Execute Ansible code in sandbox.
    
    POST /api/sandbox/execute/
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SandboxThrottle]
    
    def post(self, request):
        serializer = ExecuteCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        exercise_id = serializer.validated_data.get('exercise_id')
        
        # Validate playbook
        validation_result = AnsibleValidator.validate_playbook(code)
        if not validation_result['valid']:
            return Response({
                "success": False,
                "errors": validation_result['errors'],
                "warnings": validation_result['warnings']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create sandbox session
        session = SandboxSession.objects.filter(
            user=request.user,
            status='running'
        ).first()
        
        if not session or session.is_expired:
            return Response(
                {"error": "No active sandbox session. Please create one first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute code
        executor = DockerExecutor()
        execution_result = executor.execute_playbook(
            session.container_name,
            code,
            timeout=300
        )
        
        # Run tests if exercise_id provided
        test_results = None
        is_passed = False
        
        if exercise_id:
            try:
                exercise = Exercise.objects.get(id=exercise_id, is_published=True)
                test_results = TestRunner.run_tests(
                    exercise.test_cases,
                    execution_result
                )
                is_passed = test_results['passed']
                
                # Save attempt
                ExerciseAttempt.objects.create(
                    exercise=exercise,
                    user=request.user,
                    code_submitted=code,
                    output=execution_result.get('stdout', ''),
                    error_message=execution_result.get('stderr', ''),
                    test_results=test_results,
                    is_passed=is_passed,
                    execution_time=execution_result.get('execution_time'),
                    attempt_number=1  # Will be auto-incremented
                )
                
                # Award XP if passed
                if is_passed:
                    request.user.add_xp(exercise.xp_reward)
                
            except Exercise.DoesNotExist:
                pass
        
        # Update session activity
        session.last_activity = timezone.now()
        session.save(update_fields=['last_activity'])
        
        response_data = {
            **execution_result,
            "test_results": test_results,
            "is_passed": is_passed,
            "warnings": validation_result.get('warnings', [])
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class DestroySandboxView(APIView):
    """
    Destroy sandbox session.
    
    POST /api/sandbox/destroy/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        session = SandboxSession.objects.filter(
            user=request.user,
            status='running'
        ).first()
        
        if not session:
            return Response(
                {"message": "No active session found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        executor = DockerExecutor()
        success = executor.stop_container(session.container_name)
        
        if success:
            session.status = 'stopped'
            session.save(update_fields=['status'])
            return Response(
                {"message": "Sandbox destroyed successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Failed to destroy sandbox"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
