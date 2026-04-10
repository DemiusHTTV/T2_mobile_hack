from functools import wraps
from rest_framework.exceptions import PermissionDenied


def role_required(*roles):
    """
    Декоратор для проверки ролей пользователя.
    Если роль пользователя не указана в списке разрешённых,
    выбрасывается исключение PermissionDenied.
    
    Пример использования:
        @role_required('admin', 'head')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Пользователь не аутентифицирован")
            
            if request.user.role not in roles:
                raise PermissionDenied(
                    f"Доступ запрещён. Требуется одна из ролей: {', '.join(roles)}"
                )
            
            return view_func(self, request, *args, **kwargs)
        return wrapped_view
    return decorator


class RolePermission:
    """
    Базовый класс для проверки прав на основе ролей.
    Наследуйте и переопределяйте allowed_roles в подклассах.
    """
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in self.allowed_roles


class AdminPermission(RolePermission):
    allowed_roles = ['admin']


class HeadPermission(RolePermission):
    allowed_roles = ['admin', 'head']


class EmployeePermission(RolePermission):
    allowed_roles = ['admin', 'head', 'employee']
