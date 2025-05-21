from django import forms
from .models import ChatMessage, OpenAISettings, CourseAISettings

class ChatMessageForm(forms.ModelForm):
    """Form for sending a new message in the chat"""
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control chat-input',
                'rows': 1,
                'placeholder': 'Ask your tutor a question...',
                'autofocus': True
            })
        }

class OpenAISettingsForm(forms.ModelForm):
    """Form for updating OpenAI settings"""
    class Meta:
        model = OpenAISettings
        fields = ['api_key', 'model', 'temperature', 'max_tokens']
        widgets = {
            'api_key': forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'model': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
                ('gpt-4', 'GPT-4'),
                ('gpt-4-turbo', 'GPT-4 Turbo'),
            ]),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 1, 'step': 0.1}),
            'max_tokens': forms.NumberInput(attrs={'class': 'form-control', 'min': 100, 'max': 4000})
        }

class CourseAISettingsForm(forms.ModelForm):
    """Form for updating course-specific AI settings"""
    class Meta:
        model = CourseAISettings
        fields = ['is_enabled_for_students', 'is_enabled_for_instructors', 'system_prompt']
        widgets = {
            'is_enabled_for_students': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_enabled_for_instructors': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'system_prompt': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 
                                              'placeholder': 'Custom instructions for the AI tutor...'})
        }

class QuizQuestionGeneratorForm(forms.Form):
    """Form for generating quiz questions using AI"""
    question_type = forms.ChoiceField(
        choices=[
            ('multiple_choice', 'Multiple Choice'),
            ('true_false', 'True/False'),
            ('short_answer', 'Short Answer')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    topic = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 
                                    'placeholder': 'Enter the topic for the question'})
    )
    
    difficulty = forms.ChoiceField(
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    number_of_questions = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    ) 