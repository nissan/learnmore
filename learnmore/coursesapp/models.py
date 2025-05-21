from django.db import models
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    instructor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='courses')
    categories = models.ManyToManyField(Category, related_name='courses')
    difficulty = models.PositiveIntegerField(default=100)
    duration = models.CharField(max_length=50, help_text='e.g. 8 weeks, 10 hours')
    is_public = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Quiz(models.Model):
    module = models.ForeignKey(Module, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.module.title})"

class Enrollment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'course']  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

class QuizAttempt(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score})"
