from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from coursesapp.models import Course, Enrollment, Module, Quiz, QuizAttempt
from django.db.models import Avg

# Create your views here.

@login_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    course_stats = []
    for course in courses:
        enrolled_count = Enrollment.objects.filter(course=course, is_active=True).count()
        modules = Module.objects.filter(course=course)
        # Recent student activity: last 5 enrollments
        recent_enrollments = Enrollment.objects.filter(course=course, is_active=True).order_by('-enrolled_at')[:5]
        # Quiz stats: number of quizzes and average score
        quizzes = Quiz.objects.filter(module__course=course)
        quiz_count = quizzes.count()
        avg_score = QuizAttempt.objects.filter(quiz__in=quizzes).aggregate(avg=Avg('score'))['avg']
        course_stats.append({
            'course': course,
            'enrolled_count': enrolled_count,
            'modules': modules,
            'recent_enrollments': recent_enrollments,
            'quiz_count': quiz_count,
            'avg_score': avg_score,
            'quizzes': quizzes,
        })
    return render(request, 'instructorapp/dashboard.html', {
        'course_stats': course_stats,
    })
