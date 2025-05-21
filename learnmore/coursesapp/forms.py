from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Course, Module, Quiz, Category, QuizQuestion, QuizOption

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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describe what students will learn in this course'
            }),
            'difficulty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8 weeks, 10 hours'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'title': 'Choose a clear, descriptive title',
            'description': 'Include learning objectives and target audience',
            'difficulty': 'Set between 1 (beginner) and 100 (expert)',
            'is_published': 'When checked, this course will be visible to students',
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Module title'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Brief overview of this module'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor', 
                'rows': 10,
                'placeholder': 'Module content - supports HTML formatting'
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'instructions', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quiz title'}),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Instructions for students taking this quiz'
            }),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100})
        }

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question_text', 'question_type', 'points', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Enter your question here'
            }),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class QuizOptionForm(forms.ModelForm):
    class Meta:
        model = QuizOption
        fields = ['option_text', 'is_correct']
        widgets = {
            'option_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Answer option'
            }),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

ModuleFormSet = inlineformset_factory(
    Course, Module,
    form=ModuleForm,
    fields=['title', 'description', 'content', 'order'],
    extra=1,
    can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Module title'}),
        'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'content': forms.Textarea(attrs={'class': 'form-control rich-text-editor', 'rows': 5}),
        'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
    }
)

QuestionFormSet = inlineformset_factory(
    Quiz, QuizQuestion,
    form=QuizQuestionForm,
    fields=['question_text', 'question_type', 'points', 'order'],
    extra=1,
    can_delete=True
)

OptionFormSet = inlineformset_factory(
    QuizQuestion, QuizOption,
    form=QuizOptionForm,
    fields=['option_text', 'is_correct'],
    extra=4,
    can_delete=True,
    max_num=6
) 