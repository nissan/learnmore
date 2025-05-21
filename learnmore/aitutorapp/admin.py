from django.contrib import admin
from .models import OpenAISettings, ChatSession, ChatMessage, CourseAISettings

@admin.register(OpenAISettings)
class OpenAISettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'temperature', 'max_tokens', 'updated_at')
    search_fields = ('model',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CourseAISettings)
class CourseAISettingsAdmin(admin.ModelAdmin):
    list_display = ('course', 'is_enabled_for_students', 'is_enabled_for_instructors', 'updated_at')
    list_filter = ('is_enabled_for_students', 'is_enabled_for_instructors')
    search_fields = ('course__title',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'course', 'created_at', 'updated_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'user__username', 'course__title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'content_preview', 'timestamp')
    list_filter = ('role', 'timestamp', 'session__course')
    search_fields = ('content', 'session__title')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
