from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, Department

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """Сериализатор организации."""
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    """Сериализатор подразделения."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'organization', 'organization_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'department', 'department_name',
            'organization', 'organization_name', 'phone',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации (создания пользователя)."""
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'department',
            'organization', 'phone'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Пароли не совпадают")
        
        # Проверка допустимых ролей
        if 'role' in data and data['role'] not in dict(User.RoleChoices.choices):
            raise serializers.ValidationError(f"Недопустимая роль. Допустимые: {', '.join(dict(User.RoleChoices.choices).keys())}")
        
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.RoleChoices.EMPLOYEE),
            department=validated_data.get('department'),
            organization=validated_data.get('organization'),
            phone=validated_data.get('phone', ''),
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пользователя."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'department', 'organization'
        ]
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Новые пароли не совпадают")
        return data
