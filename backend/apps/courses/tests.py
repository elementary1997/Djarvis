"""
Tests for courses app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import Course, Module, Lesson, CourseEnrollment

User = get_user_model()


class CourseTestCase(TestCase):
    """Test Course model and endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Ansible Basics',
            slug='ansible-basics',
            description='Learn Ansible from scratch',
            short_description='Beginner Ansible course',
            difficulty='beginner',
            estimated_hours=10,
            is_published=True
        )
    
    def test_course_creation(self):
        """Test course creation."""
        self.assertEqual(self.course.title, 'Ansible Basics')
        self.assertEqual(self.course.slug, 'ansible-basics')
    
    def test_list_courses(self):
        """Test listing courses."""
        response = self.client.get('/api/courses/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_enroll_in_course(self):
        """Test course enrollment."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/courses/courses/{self.course.slug}/enroll/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseEnrollment.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )


class LessonCompletionTestCase(TestCase):
    """Test lesson completion functionality."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
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
            content='# Test Content',
            is_published=True
        )
        
        # Enroll user
        CourseEnrollment.objects.create(
            user=self.user,
            course=self.course
        )
    
    def test_complete_lesson(self):
        """Test marking lesson as complete."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/courses/lessons/{self.lesson.slug}/complete/',
            {'time_spent_minutes': 15}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
