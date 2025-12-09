"""
Tests for exercises app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.courses.models import Course, Module, Lesson
from .models import Exercise, Hint, Submission

User = get_user_model()


class ExerciseTestCase(TestCase):
    """Test Exercise model and endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        # Create test data
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test',
            short_description='Test',
            is_published=True
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            slug='test-module',
            is_published=True
        )
        
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Test Lesson',
            slug='test-lesson',
            content='# Test',
            is_published=True
        )
        
        self.exercise = Exercise.objects.create(
            lesson=self.lesson,
            title='Test Exercise',
            slug='test-exercise',
            description='Write a playbook',
            difficulty='easy',
            points=10,
            initial_code='---\n',
            is_published=True
        )
    
    def test_list_exercises(self):
        """Test listing exercises."""
        response = self.client.get('/api/exercises/exercises/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_submit_exercise(self):
        """Test exercise submission."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': '---\n- hosts: all\n  tasks:\n    - debug: msg="Hello"'
        }
        
        response = self.client.post(
            f'/api/exercises/exercises/{self.exercise.slug}/submit/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Submission.objects.filter(
                user=self.user,
                exercise=self.exercise
            ).exists()
        )


class HintRevealTestCase(TestCase):
    """Test hint revelation functionality."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        course = Course.objects.create(
            title='Test', slug='test', description='T',
            short_description='T', is_published=True
        )
        module = Module.objects.create(
            course=course, title='Test', slug='test', is_published=True
        )
        lesson = Lesson.objects.create(
            module=module, title='Test', slug='test',
            content='T', is_published=True
        )
        self.exercise = Exercise.objects.create(
            lesson=lesson, title='Test', slug='test',
            description='T', is_published=True
        )
        
        self.hint = Hint.objects.create(
            exercise=self.exercise,
            order=0,
            content='Check your syntax',
            points_penalty=2
        )
    
    def test_reveal_hint(self):
        """Test revealing a hint."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            f'/api/exercises/exercises/{self.exercise.slug}/hints/0/reveal/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
