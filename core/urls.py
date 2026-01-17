from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/instructions/', views.instructions, name='instructions'),
    path('quiz/<int:quiz_id>/', views.quiz, name='quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/<int:quiz_id>/completion/', views.completion, name='completion'),
    path('quiz/<int:quiz_id>/results/', views.results, name='results'),
    path('quiz/<int:quiz_id>/check-time/', views.check_time, name='check_time'),
]

