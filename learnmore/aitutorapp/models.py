from django.db import models
from django.contrib.auth import get_user_model
from coursesapp.models import Course, Module

User = get_user_model()

class OpenAISettings(models.Model):
    """Store OpenAI API settings"""
    api_key = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=50, default="gpt-3.5-turbo")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "OpenAI Settings"
        verbose_name_plural = "OpenAI Settings"
    
    def __str__(self):
        return f"OpenAI Settings (Updated: {self.updated_at.strftime('%Y-%m-%d')})"

class CourseAISettings(models.Model):
    """Store AI tutor settings for a specific course"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='ai_settings')
    is_enabled_for_students = models.BooleanField(default=True, 
                                                help_text="Enable AI tutor for enrolled students")
    is_enabled_for_instructors = models.BooleanField(default=True,
                                                  help_text="Enable AI tutor for course instructors")
    system_prompt = models.TextField(blank=True, 
                                  help_text="Custom system prompt to guide the AI tutor behavior")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Course AI Settings"
        verbose_name_plural = "Course AI Settings"
    
    def __str__(self):
        return f"AI Settings for {self.course.title}"

class ChatSession(models.Model):
    """Store chat sessions between users and the AI tutor"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.course.title})"

class ChatMessage(models.Model):
    """Store individual chat messages"""
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
