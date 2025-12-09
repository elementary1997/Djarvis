"""
Serializers for sandbox execution.
"""
from rest_framework import serializers
from .models import SandboxSession


class SandboxSessionSerializer(serializers.ModelSerializer):
    """Serializer for sandbox sessions."""
    
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SandboxSession
        fields = [
            'id', 'container_id', 'container_name', 'status',
            'created_at', 'expires_at', 'last_activity', 'is_expired'
        ]
        read_only_fields = ['container_id', 'container_name', 'status']


class ExecuteCodeSerializer(serializers.Serializer):
    """Serializer for code execution requests."""
    
    code = serializers.CharField(
        required=True,
        help_text='Ansible playbook YAML content'
    )
    exercise_id = serializers.IntegerField(
        required=False,
        help_text='Optional exercise ID for automatic testing'
    )
    
    def validate_code(self, value):
        """Validate that code is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Code cannot be empty")
        return value


class ExecutionResultSerializer(serializers.Serializer):
    """Serializer for execution results."""
    
    success = serializers.BooleanField()
    exit_code = serializers.IntegerField(required=False)
    stdout = serializers.CharField(allow_blank=True)
    stderr = serializers.CharField(allow_blank=True)
    execution_time = serializers.FloatField(required=False)
    error = serializers.CharField(required=False, allow_blank=True)
    test_results = serializers.DictField(required=False)
    is_passed = serializers.BooleanField(required=False)
