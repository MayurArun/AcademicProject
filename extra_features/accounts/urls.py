from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.logout, name='logout'),
    path('get_all_accounts/', views.get_all_accounts, name='get_all_accounts'),
    path('delete_account/<int:account_id>/', views.delete_account, name='delete_account'),
    path('edit_account/<int:account_id>/', views.edit_account, name='edit_account'),
    # Add other URLs as needed
]