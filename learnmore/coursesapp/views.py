from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from rest_framework import generics, viewsets
from .models import Course, Quiz, Enrollment, Module, QuizAttempt
from .forms import CourseForm, ModuleForm, QuizForm, ModuleFormSet
from django.db import transaction
from django.forms import modelformset_factory
import qrcode
from django.http import HttpResponse
from io import BytesIO

class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class CourseListView(ListView):
    model = Course
    template_name = 'coursesapp/course_catalog.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            # Instructors see all their courses
            return Course.objects.filter(instructor=self.request.user).order_by('-created_at')
        # Students see only published courses
        return Course.objects.filter(is_public=True, is_published=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_instructor'] = self.request.user.is_staff
        return context

@login_required
def create_course_with_modules(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        module_formset = ModuleFormSet(request.POST, prefix='modules')
        if course_form.is_valid() and module_formset.is_valid():
            with transaction.atomic():
                course = course_form.save(commit=False)
                course.instructor = request.user
                course.slug = slugify(course_form.cleaned_data['title'])
                course.save()
                course_form.save_m2m()
                modules = module_formset.save(commit=False)
                for module in modules:
                    module.course = course
                    module.save()
            messages.success(request, 'Course and modules created!')
            return redirect('course_catalog')
    else:
        course_form = CourseForm()
        module_formset = ModuleFormSet(prefix='modules')
    return render(request, 'coursesapp/course_form.html', {
        'form': course_form,
        'module_formset': module_formset,
    })

@login_required
def add_module_to_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, 'Module added successfully!')
            return redirect('course_detail', slug=course_slug)
    else:
        form = ModuleForm()
    
    return render(request, 'coursesapp/module_form.html', {
        'form': form,
        'course': course
    })

@login_required
def add_quiz_to_module(request, course_slug, module_id):
    module = get_object_or_404(Module, id=module_id, course__slug=course_slug, course__instructor=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.module = module
            quiz.save()
            messages.success(request, 'Quiz added successfully!')
            return redirect('course_detail', slug=course_slug)
    else:
        form = QuizForm()
    
    return render(request, 'coursesapp/quiz_form.html', {
        'form': form,
        'module': module,
        'course': module.course
    })

@login_required
def toggle_course_publish(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    course.is_published = not course.is_published
    course.save()
    status = 'published' if course.is_published else 'unpublished'
    messages.success(request, f'Course {status} successfully!')
    return redirect('course_detail', slug=course_slug)

class CourseDetailView(DetailView):
    model = Course
    template_name = 'coursesapp/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        context['is_instructor'] = user.is_authenticated and (course.instructor == user)
        if user.is_authenticated:
            context['is_enrolled'] = (
                course.instructor == user or
                Enrollment.objects.filter(user=user, course=course, is_active=True).exists()
            )
        else:
            context['is_enrolled'] = False
        # Add QR code URL for this course
        course_url = self.request.build_absolute_uri(self.request.path)
        context['course_qr_url'] = reverse('generate_qr_code') + f'?url={course_url}'
        return context

class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'coursesapp/quiz_detail.html'
    context_object_name = 'quiz'
    pk_url_kwarg = 'quiz_id'

    def get(self, request, *args, **kwargs):
        quiz = self.get_object()
        # Check if user is enrolled in the course
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access quiz content.')
            return redirect('account_login')
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=quiz.module.course,
            is_active=True
        ).exists()
        if not is_enrolled:
            messages.warning(request, 'You must be enrolled in this course to access quiz content.')
            return redirect('course_detail', slug=quiz.module.course.slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object
        quiz_url = self.request.build_absolute_uri(self.request.path)
        context['quiz_qr_url'] = reverse('generate_qr_code') + f'?url={quiz_url}'
        return context

@login_required
def enroll_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        if not enrollment.is_active:
            enrollment.is_active = True
            enrollment.save()
            messages.success(request, f'Welcome back to {course.title}!')
        else:
            messages.info(request, f'You are already enrolled in {course.title}.')
    
    return redirect('course_detail', slug=course_slug)

# DRF API view
from .serializers import CourseSerializer
class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.filter(is_public=True)
    serializer_class = CourseSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

@login_required
def edit_modules(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    ModuleFormSet = modelformset_factory(Module, form=ModuleForm, extra=0, can_delete=True)
    queryset = Module.objects.filter(course=course)
    if request.method == 'POST':
        formset = ModuleFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            modules = formset.save(commit=False)
            for module in modules:
                module.course = course
                module.save()
            for obj in formset.deleted_objects:
                obj.delete()
            formset.save_m2m()
            messages.success(request, 'Modules updated successfully!')
            return redirect('course_detail', slug=course_slug)
    else:
        formset = ModuleFormSet(queryset=queryset)
    return render(request, 'coursesapp/edit_modules.html', {
        'formset': formset,
        'course': course
    })

def generate_qr_code(request):
    """Generate QR code for a given URL."""
    url = request.GET.get('url')
    if not url:
        return HttpResponse('URL parameter is required', status=400)
    try:
        # Create QR code
        img = qrcode.make(url)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Set response headers
        response = HttpResponse(buffer, content_type='image/png')
        response['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
        response['Content-Disposition'] = 'inline; filename="qr_code.png"'
        return response
    except Exception as e:
        return HttpResponse(f'Error generating QR code: {str(e)}', status=500)

@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = request.user

    if request.method == 'POST':
        # TODO: Replace with real grading logic
        score = float(request.POST.get('score', 0))
        QuizAttempt.objects.create(user=user, quiz=quiz, score=score)
        messages.success(request, f'Quiz submitted! Your score: {score}')
        return redirect('quiz_detail', quiz_id=quiz.id)

    return render(request, 'coursesapp/submit_quiz.html', {'quiz': quiz})
