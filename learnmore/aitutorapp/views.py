from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
import json

from .models import ChatSession, ChatMessage, OpenAISettings, CourseAISettings
from .forms import ChatMessageForm, OpenAISettingsForm, CourseAISettingsForm, QuizQuestionGeneratorForm
from .utils import process_message, generate_quiz_questions
from coursesapp.models import Course, Enrollment, Module, Quiz, QuizQuestion, QuizOption

@login_required
def chat_view(request, course_id, session_id=None):
    """
    Main view for the AI tutor chat interface.
    If session_id is provided, it loads that session.
    Otherwise, it creates a new session or loads the most recent one.
    """
    # Get the course
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is enrolled or is the instructor
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    # Get course AI settings
    course_ai_settings = get_object_or_404(CourseAISettings, course=course)
    
    # Check if the user is allowed to use the AI tutor
    if not is_instructor and not is_enrolled:
        messages.error(request, "You must be enrolled in this course to use the AI tutor.")
        return redirect('course_detail', course.slug)
    
    # Check if AI tutor is enabled for this user type
    if not is_instructor and not course_ai_settings.is_enabled_for_students:
        messages.warning(request, "The AI tutor is currently disabled for students in this course.")
        return redirect('course_detail', course.slug)
    
    if is_instructor and not course_ai_settings.is_enabled_for_instructors:
        messages.warning(request, "The AI tutor is currently disabled for instructors in this course.")
        return redirect('course_detail', course.slug)
    
    # Get or create a chat session
    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user, course=course)
    else:
        # Get the most recent session or create a new one
        session = ChatSession.objects.filter(user=request.user, course=course).order_by('-updated_at').first()
        if not session:
            session = ChatSession.objects.create(
                user=request.user,
                course=course,
                title=f"Chat about {course.title}"
            )
    
    # Get all messages for this session
    messages_list = ChatMessage.objects.filter(session=session).order_by('timestamp')
    
    # Get all sessions for this course
    sessions = ChatSession.objects.filter(user=request.user, course=course).order_by('-updated_at')
    
    # Create a form for sending new messages
    form = ChatMessageForm()
    
    context = {
        'course': course,
        'session': session,
        'messages': messages_list,
        'sessions': sessions,
        'form': form,
        'is_instructor': is_instructor,
    }
    
    return render(request, 'aitutorapp/chat.html', context)

@login_required
@require_POST
def send_message(request, session_id):
    """Handle sending a message to the AI tutor and getting a response"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    form = ChatMessageForm(request.POST)
    
    if form.is_valid():
        user_message = form.cleaned_data['content']
        
        # Process the message and get a response
        response = process_message(session_id, user_message)
        
        if response['status'] == 'success':
            # Return the AI's response
            return JsonResponse({
                'status': 'success',
                'message': response['message']
            })
        else:
            # Return the error
            return JsonResponse({
                'status': 'error',
                'message': response['message']
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid form submission'
    })

@login_required
@require_POST
def create_session(request, course_id):
    """Create a new chat session for the specified course"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the user is allowed to use the AI tutor
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    if not is_instructor and not is_enrolled:
        messages.error(request, "You must be enrolled in this course to use the AI tutor.")
        return redirect('course_detail', course.slug)
    
    # Create a new session
    session = ChatSession.objects.create(
        user=request.user,
        course=course,
        title=f"New Chat {ChatSession.objects.filter(user=request.user, course=course).count() + 1}"
    )
    
    # Create a system welcome message
    ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=f"Hello! I'm your AI tutor for {course.title}. How can I help you understand the course material today?"
    )
    
    # Redirect to the new session
    return redirect('chat_view', course_id=course_id, session_id=session.id)

@login_required
@require_POST
def rename_session(request, session_id):
    """Rename a chat session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    
    new_title = request.POST.get('title')
    if new_title:
        session.title = new_title
        session.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Title is required'})

@login_required
@require_POST
def delete_session(request, session_id):
    """Delete a chat session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    course_id = session.course.id
    session.delete()
    
    # Redirect to the course's chat page
    return redirect('chat_view', course_id=course_id)

@login_required
def openai_settings(request):
    """View for managing OpenAI API settings"""
    # Only allow staff/admin to access this page
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    settings, created = OpenAISettings.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        form = OpenAISettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "OpenAI settings updated successfully!")
            return redirect('openai_settings')
    else:
        form = OpenAISettingsForm(instance=settings)
    
    return render(request, 'aitutorapp/settings.html', {'form': form})

@login_required
def course_ai_settings(request, course_id):
    """View for managing course-specific AI settings"""
    course = get_object_or_404(Course, id=course_id)
    
    # Only allow the course instructor to access this page
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('course_detail', course.slug)
    
    settings, created = CourseAISettings.objects.get_or_create(course=course)
    
    if request.method == 'POST':
        form = CourseAISettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Course AI settings updated successfully!")
            return redirect('course_detail', course.slug)
    else:
        form = CourseAISettingsForm(instance=settings)
    
    context = {
        'form': form,
        'course': course
    }
    
    return render(request, 'aitutorapp/course_settings.html', context)

@login_required
def generate_quiz_question_view(request, module_id):
    """View for generating quiz questions using AI"""
    module = get_object_or_404(Module, id=module_id)
    course = module.course
    
    # Only allow the course instructor to access this page
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('course_detail', course.slug)
    
    # Check if AI tutor is enabled for instructors
    course_ai_settings = get_object_or_404(CourseAISettings, course=course)
    if not course_ai_settings.is_enabled_for_instructors:
        messages.warning(request, "The AI tutor is currently disabled for instructors in this course.")
        return redirect('edit_modules', course.slug)
    
    if request.method == 'POST':
        form = QuizQuestionGeneratorForm(request.POST)
        if form.is_valid():
            question_type = form.cleaned_data['question_type']
            topic = form.cleaned_data['topic']
            difficulty = form.cleaned_data['difficulty']
            number_of_questions = form.cleaned_data['number_of_questions']
            
            # Generate the questions
            result = generate_quiz_questions(
                course.id, 
                question_type, 
                topic, 
                difficulty, 
                number_of_questions
            )
            
            if result['status'] == 'success':
                return render(request, 'aitutorapp/generated_questions.html', {
                    'questions': result['questions'],
                    'module': module,
                    'course': course
                })
            else:
                messages.error(request, result['message'])
    else:
        form = QuizQuestionGeneratorForm()
    
    context = {
        'form': form,
        'module': module,
        'course': course
    }
    
    return render(request, 'aitutorapp/generate_questions.html', context)

@login_required
@require_POST
def add_generated_question(request, module_id):
    """Add a generated question to a module's quiz"""
    module = get_object_or_404(Module, id=module_id)
    course = module.course
    
    # Only allow the course instructor to access this page
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('course_detail', course.slug)
    
    # Get the question data from the form
    question_data = request.POST.get('question_data')
    quiz_id = request.POST.get('quiz_id')
    
    if not question_data:
        messages.error(request, "No question data provided.")
        return redirect('generate_quiz_question', module_id=module_id)
    
    try:
        # Parse the JSON data
        question_json = json.loads(question_data)
        
        # Get or create the quiz
        if quiz_id:
            quiz = get_object_or_404(Quiz, id=quiz_id, module=module)
        else:
            # Create a new quiz if quiz_id is not provided
            quiz_title = request.POST.get('quiz_title', f"Quiz for {module.title}")
            quiz = Quiz.objects.create(
                module=module,
                title=quiz_title,
                instructions=f"Generated quiz about {question_json.get('topic', 'course content')}"
            )
        
        # Create the question
        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_text=question_json.get('question_text', ''),
            question_type=question_json.get('question_type', 'multiple_choice'),
            points=question_json.get('points', 1),
            order=QuizQuestion.objects.filter(quiz=quiz).count() + 1
        )
        
        # Create options for multiple-choice questions
        if question.question_type == 'multiple_choice' and question_json.get('options'):
            for i, option_text in enumerate(question_json['options']):
                QuizOption.objects.create(
                    question=question,
                    option_text=option_text,
                    is_correct=(i == question_json.get('correct_answer', 0) or 
                               option_text == question_json.get('correct_answer', ''))
                )
        
        messages.success(request, "Question added successfully!")
        return redirect('quiz_detail', quiz_id=quiz.id)
        
    except json.JSONDecodeError:
        messages.error(request, "Invalid question data format.")
    except Exception as e:
        messages.error(request, f"Error adding question: {str(e)}")
    
    return redirect('generate_quiz_question', module_id=module_id)
