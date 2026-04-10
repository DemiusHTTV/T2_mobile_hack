from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from schedule.models import Shift
from users.models import Organization, Department

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели пользователя."""

    def setUp(self):
        self.organization = Organization.objects.create(name="Test Org")
        self.department = Department.objects.create(
            name="Test Dept",
            organization=self.organization
        )

    def test_user_creation(self):
        """Тест создания пользователя."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role=User.RoleChoices.EMPLOYEE,
            department=self.department,
            organization=self.organization
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, User.RoleChoices.EMPLOYEE)
        self.assertTrue(user.is_active)

    def test_user_role_properties(self):
        """Тест свойств ролей."""
        admin = User.objects.create_user(
            username="admin",
            password="admin123",
            role=User.RoleChoices.ADMIN
        )
        head = User.objects.create_user(
            username="head",
            password="head123",
            role=User.RoleChoices.HEAD
        )
        employee = User.objects.create_user(
            username="employee",
            password="emp123",
            role=User.RoleChoices.EMPLOYEE
        )

        self.assertTrue(admin.is_admin)
        self.assertTrue(head.is_head)
        self.assertTrue(employee.is_employee)


class ShiftModelTest(TestCase):
    """Тесты модели смен."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_shift_creation(self):
        """Тест создания смены."""
        tomorrow = timezone.localdate() + timedelta(days=1)
        shift = Shift.objects.create(
            employee=self.user,
            date=tomorrow,
            start_time="09:00:00",
            end_time="17:00:00"
        )
        self.assertEqual(shift.status, Shift.Status.PLAN)
        self.assertEqual(shift.employee, self.user)

    def test_shift_overlap_validation(self):
        """Тест валидации пересекающихся смен."""
        tomorrow = timezone.localdate() + timedelta(days=1)
        Shift.objects.create(
            employee=self.user,
            date=tomorrow,
            start_time="09:00:00",
            end_time="17:00:00"
        )
        
        overlapping_shift = Shift(
            employee=self.user,
            date=tomorrow,
            start_time="15:00:00",
            end_time="20:00:00"
        )
        
        with self.assertRaises(Exception):  # ValidationError
            overlapping_shift.full_clean()

    def test_past_date_validation(self):
        """Тест валидации прошедшей даты."""
        yesterday = timezone.localdate() - timedelta(days=1)
        shift = Shift(
            employee=self.user,
            date=yesterday,
            start_time="09:00:00",
            end_time="17:00:00"
        )
        
        with self.assertRaises(Exception):  # ValidationError
            shift.full_clean()


class AuthAPITest(APITestCase):
    """Тесты API аутентификации."""

    def test_user_registration(self):
        """Тест регистрации пользователя."""
        url = '/api/users/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login(self):
        """Тест входа."""
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        url = '/api/users/login/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_invalid_credentials(self):
        """Тест неверных учетных данных."""
        url = '/api/users/login/'
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ShiftAPITest(TestCase):
    """Тесты API смен."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Логинимся через сессию
        self.client.login(username='testuser', password='testpass123')

    def test_create_shift(self):
        """Тест создания смены через API."""
        tomorrow = timezone.localdate() + timedelta(days=1)
        url = '/api/schedule/shifts/'
        import json
        data = {
            'date': tomorrow.isoformat(),
            'start_time': '09:00',
            'end_time': '17:00'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Shift.objects.count(), 1)

    def test_get_own_shifts(self):
        """Тест получения своих смен."""
        tomorrow = timezone.localdate() + timedelta(days=1)
        Shift.objects.create(
            employee=self.user,
            date=tomorrow,
            start_time="09:00:00",
            end_time="17:00:00"
        )
        url = '/api/schedule/shifts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        import json
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)

    def test_unauthorized_access(self):
        """Тест неавторизованного доступа."""
        self.client.logout()
        url = '/api/schedule/shifts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
