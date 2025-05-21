from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.CourseListView.as_view(), name='course_catalog'),
    path('api/catalog/', views.CourseListAPIView.as_view(), name='course_catalog_api'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
] 