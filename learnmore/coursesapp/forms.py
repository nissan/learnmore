from django import forms
from django.forms import inlineformset_factory
from .models import Course, Module, Quiz, Category

class CourseForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Course
        fields = ['title', 'description', 'categories', 'difficulty', 'duration', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 3}),
        }

ModuleFormSet = inlineformset_factory(
    Course, Module,
    fields=['title', 'description', 'order'],
    extra=3,  # Show 3 blank module forms by default
    can_delete=True
) 