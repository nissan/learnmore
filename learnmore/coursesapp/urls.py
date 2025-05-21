from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, create_course_with_modules
from . import views  # Import views to fix NameError

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('catalog/', views.CourseListView.as_view(), name='course_catalog'),
    path('api/catalog/', views.CourseListAPIView.as_view(), name='course_catalog_api'),
    path('create/', create_course_with_modules, name='course_create'),
    path('qr/', views.generate_qr_code, name='generate_qr_code'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('quiz/<int:quiz_id>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('enroll/<slug:course_slug>/', views.enroll_course, name='enroll_course'),
    path('<slug:course_slug>/module/<int:module_id>/add-quiz/', views.add_quiz_to_module, name='add_quiz_to_module'),
    path('<slug:course_slug>/edit-modules/', views.edit_modules, name='edit_modules'),
    path('', include(router.urls)),
]