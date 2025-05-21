from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
] 