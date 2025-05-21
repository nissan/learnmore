from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/', views.chat_view, name='chat_view'),
    path('course/<int:course_id>/session/<int:session_id>/', views.chat_view, name='chat_view_session'),
    path('session/<int:session_id>/send/', views.send_message, name='send_message'),
    path('course/<int:course_id>/new-session/', views.create_session, name='create_session'),
    path('session/<int:session_id>/rename/', views.rename_session, name='rename_session'),
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('settings/', views.openai_settings, name='openai_settings'),
    path('course/<int:course_id>/settings/', views.course_ai_settings, name='course_ai_settings'),
    path('module/<int:module_id>/generate-questions/', views.generate_quiz_question_view, name='generate_quiz_question'),
    path('module/<int:module_id>/add-generated-question/', views.add_generated_question, name='add_generated_question'),
] 