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
    content = models.TextField(blank=True, help_text="HTML content for this module")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Quiz(models.Model):
    module = models.ForeignKey(Module, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70, help_text="Minimum percentage to pass")
    
    def __str__(self):
        return f"{self.title} ({self.module.title})"
        
    def get_total_points(self):
        return self.questions.aggregate(total=models.Sum('points'))['total'] or 0

class QuizQuestion(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    )
    
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question_text[:30]}... ({self.quiz.title})"

class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Incorrect'})"

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

class QuizQuestionResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(QuizOption, blank=True)
    text_response = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Response to {self.question} by {self.attempt.user.username}"
