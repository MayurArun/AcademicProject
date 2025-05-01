from django.urls import path
from . import views

app_name = 'classes' 

urlpatterns = [
    # Existing URLs
    path('create_class/', views.create_class, name='create_class'),
    path('join_class/', views.join_class, name='join_class'),
    path('class_dashboard/<str:class_code>/', views.class_dashboard, name='class_dashboard'),
    path('remove_student/<int:membership_id>/', views.remove_student, name='remove_student'),
    path('delete_class/<str:class_code>/', views.delete_class, name='delete_class'),

    # Assignment URLs
    path('create_assignment/<str:class_code>/', views.create_assignment, name='create_assignment'),
    path('submit_assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('view_assignments/<str:class_code>/', views.view_assignments, name='view_assignments'),
    path('view_submissions/<int:assignment_id>/', views.view_submissions, name='view_submissions'),
    path('view_student_submissions/<int:assignment_id>/', views.view_student_submissions, name='view_student_submissions'),
    path('grade_submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),

    # Discussion URLs
    path('post_message/<str:class_code>/', views.post_message, name='post_message'),
    path('reply_message/<int:post_id>/', views.reply_message, name='reply_message'),
    path('delete_message/<int:message_id>/<str:message_type>/', views.delete_message, name='delete_message'),
    
    

    # Quiz URLs
    path('create_quiz/<str:class_code>/', views.create_quiz, name='create_quiz'),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('view_quiz_grades/<int:quiz_id>/', views.view_quiz_grades, name='view_quiz_grades'),
    path('view_quizzes/<str:class_code>/', views.view_quizzes, name='view_quizzes'),
    path('delete_quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),

    path('get_notifications/', views.get_notifications, name='get_notifications'),
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),

    path('notifications/mark_read/<int:notification_id>/', views.mark_notification_as_read,name='mark_notification_as_read'),
]

