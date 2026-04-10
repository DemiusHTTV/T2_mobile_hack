from django.urls import path
from .views import (
    RegisterAPIView, LoginAPIView, LogoutAPIView, MeAPIView,
    ChangePasswordAPIView, UserListAPIView, UserRetrieveAPIView,
    OrganizationListAPIView, OrganizationDetailAPIView,
    DepartmentListAPIView, DepartmentDetailAPIView,
    DepartmentEmployeesAPIView,
    RatingsAPIView,
)

urlpatterns = [
    # Auth
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('me/', MeAPIView.as_view(), name='me'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    
    # Users
    path('', UserListAPIView.as_view(), name='user-list'),
    path('<int:pk>/', UserRetrieveAPIView.as_view(), name='user-retrieve'),
    
    # Organizations
    path('organizations/', OrganizationListAPIView.as_view(), name='organization-list'),
    path('organizations/<int:pk>/', OrganizationDetailAPIView.as_view(), name='organization-detail'),
    
    # Departments
    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path('departments/<int:pk>/', DepartmentDetailAPIView.as_view(), name='department-detail'),
    path('departments/<int:department_id>/employees/', DepartmentEmployeesAPIView.as_view(), name='department-employees'),

    # Ratings
    path('ratings/', RatingsAPIView.as_view(), name='ratings'),
]
