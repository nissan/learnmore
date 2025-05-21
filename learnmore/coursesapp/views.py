from django.shortcuts import render
from django.views.generic import ListView, DetailView
from rest_framework import generics
from .models import Course

# HTML catalog view
class CourseListView(ListView):
    model = Course
    template_name = 'coursesapp/course_catalog.html'
    context_object_name = 'courses'
    queryset = Course.objects.filter(is_public=True).order_by('-created_at')

class CourseDetailView(DetailView):
    model = Course
    template_name = 'coursesapp/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

# DRF API view
from .serializers import CourseSerializer
class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.filter(is_public=True)
    serializer_class = CourseSerializer
