from django.contrib import admin
from .models import Category, Course, Module, Quiz

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = [ModuleInline]
    list_display = ('title', 'instructor', 'is_public', 'created_at')
    search_fields = ('title', 'description')

class ModuleAdmin(admin.ModelAdmin):
    inlines = [QuizInline]
    list_display = ('title', 'course', 'order')
    search_fields = ('title',)
    list_filter = ('course',)

admin.site.register(Category)
admin.site.register(Course, CourseAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Quiz)
