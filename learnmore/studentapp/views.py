from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from coursesapp.models import Course, Enrollment, QuizAttempt
from django.db import models

# Create your views here.

@login_required
def student_dashboard(request):
    # Get courses the student is enrolled in
    enrollments = Enrollment.objects.filter(user=request.user, is_active=True)
    
    # Get all courses for recommendations (exclude enrolled ones)
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    recommended_courses = Course.objects.filter(is_published=True, is_public=True).exclude(id__in=enrolled_course_ids)[:4]
    
    # Calculate overall progress
    total_enrolled = enrollments.count()
    completed_count = 0  # This would need a completed field in the enrollment model
    progress_percentage = 0
    if total_enrolled > 0:
        progress_percentage = int((completed_count / total_enrolled) * 100)
    
    # Calculate the progress circle offset
    # The circumference of the circle with radius 54 is 339.292
    # We need to calculate the dash offset based on the progress
    progress_offset = 339.292 * (1 - progress_percentage/100)
    
    # Get quiz stats
    quiz_attempts = QuizAttempt.objects.filter(user=request.user)
    quiz_average = quiz_attempts.values('score').aggregate(avg_score=models.Avg('score'))['avg_score'] or 0
    quiz_average = int(quiz_average * 100)  # Assuming score is stored as a decimal (0.0-1.0)
    
    # Get stats for the dashboard
    stats = {
        'courses_in_progress': total_enrolled - completed_count,
        'completed_courses': completed_count,
        'hours_spent': 24,  # This would need a time tracking feature
        'quiz_average': quiz_average
    }
    
    context = {
        'user': request.user,
        'enrollments': enrollments,
        'recommended_courses': recommended_courses,
        'progress_percentage': progress_percentage,
        'progress_offset': progress_offset,
        'stats': stats,
        # Would need a model for activities to populate this
        'recent_activities': []
    }
    
    return render(request, 'studentapp/dashboard.html', context)
