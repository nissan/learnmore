from django.urls import path
from .views import LandingPageView
from . import views

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('dashboard/', views.dashboard, name='core_dashboard'),
] 