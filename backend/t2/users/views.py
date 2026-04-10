from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import Organization, Department
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, OrganizationSerializer, DepartmentSerializer
)
from .permissions import RolePermission

User = get_user_model()


# ==================== AUTH VIEWS ====================

class RegisterAPIView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    POST /api/users/register/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Генерация JWT токенов
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    Вход в систему.
    POST /api/users/login/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Необходимо указать username и password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'error': 'Неверные учетные данные'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Аккаунт деактивирован'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Генерация JWT токенов
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Успешная авторизация'
        })


class LogoutAPIView(APIView):
    """
    Выход из системы.
    POST /api/users/logout/
    """
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Если настроена blacklist
            return Response({
                'message': 'Успешный выход'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'message': 'Успешный выход'
            }, status=status.HTTP_200_OK)


class MeAPIView(generics.RetrieveUpdateAPIView):
    """
    Получение и обновление данных текущего пользователя.
    GET/PUT /api/users/me/
    """
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordAPIView(APIView):
    """
    Смена пароля.
    POST /api/users/change-password/
    """
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Проверка старого пароля
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'error': 'Неверный старый пароль'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Установка нового пароля
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Пароль успешно изменён'
        }, status=status.HTTP_200_OK)


# ==================== USER MANAGEMENT (Admin/Head) ====================

class UserListAPIView(generics.ListAPIView):
    """
    Список всех пользователей (только для admin/head).
    GET /api/users/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin видит всех, Head видит только своё подразделение
        if user.is_admin:
            return User.objects.all()
        elif user.is_head:
            return User.objects.filter(department=user.department)
        else:
            return User.objects.none()
    
    def get_permissions(self):
        from .permissions import HeadPermission
        return [HeadPermission()]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение данных конкретного пользователя.
    GET /api/users/{id}/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        from .permissions import HeadPermission
        return [HeadPermission()]


# ==================== ORGANIZATION & DEPARTMENT ====================

class OrganizationListAPIView(generics.ListCreateAPIView):
    """
    Список и создание организаций (только admin).
    GET/POST /api/users/organizations/
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальная информация, редактирование, удаление организации.
    GET/PUT/DELETE /api/users/organizations/{id}/
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class DepartmentListAPIView(generics.ListCreateAPIView):
    """
    Список и создание подразделений.
    GET/POST /api/users/departments/
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальная информация, редактирование, удаление подразделения.
    GET/PUT/DELETE /api/users/departments/{id}/
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


# ==================== DEPARTMENT EMPLOYEES (Head view) ====================

class DepartmentEmployeesAPIView(generics.ListAPIView):
    """
    Список сотрудников подразделения (для руководителя).
    GET /api/users/departments/{department_id}/employees/
    """
    serializer_class = UserSerializer
    
    def get_queryset(self):
        department_id = self.kwargs['department_id']
        user = self.request.user
        
        # Head видит только своё подразделение
        if user.is_head and user.department_id == int(department_id):
            return User.objects.filter(department_id=department_id)
        elif user.is_admin:
            return User.objects.filter(department_id=department_id)
        else:
            return User.objects.none()
