import openai
import os
import logging
import json
from .models import OpenAISettings, ChatSession, ChatMessage, CourseAISettings
from coursesapp.models import Course, Module

logger = logging.getLogger(__name__)

def get_openai_settings():
    """Retrieve OpenAI settings from the database or create default ones"""
    settings, created = OpenAISettings.objects.get_or_create(id=1)
    return settings

def get_course_content(course_id):
    """Extract course content for use as context in the AI tutor"""
    try:
        course = Course.objects.get(id=course_id)
        modules = Module.objects.filter(course=course).order_by('order')
        
        # Compile all course content into a single document
        documents = []
        
        # Add course information
        course_info = f"Course: {course.title}\nDescription: {course.description}\n\n"
        documents.append(course_info)
        
        # Add module content
        for module in modules:
            module_content = f"Module: {module.title}\nDescription: {module.description}\n\nContent: {module.content}\n\n"
            documents.append(module_content)
            
        return "\n".join(documents)
    except Course.DoesNotExist:
        logger.error(f"Course with ID {course_id} not found")
        return "No course content available."
    except Exception as e:
        logger.error(f"Error getting course content: {str(e)}")
        return "Error retrieving course content."

def get_course_ai_settings(course_id):
    """Get or create AI settings for a specific course"""
    try:
        course = Course.objects.get(id=course_id)
        settings, created = CourseAISettings.objects.get_or_create(course=course)
        return settings
    except Course.DoesNotExist:
        logger.error(f"Course with ID {course_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting course AI settings: {str(e)}")
        return None

def process_message(session_id, user_message):
    """Process a user message and get a response from the AI tutor"""
    try:
        # Get the chat session
        session = ChatSession.objects.get(id=session_id)
        
        # Save the user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        # Get settings
        settings = get_openai_settings()
        
        # Get API key from settings or environment
        api_key = settings.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            error_message = "OpenAI API key not found. Please configure it in the settings."
            ChatMessage.objects.create(
                session=session,
                role='system',
                content=f"Error: {error_message}"
            )
            return {"status": "error", "message": error_message}
        
        # Set up the OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Get course content
        course_content = get_course_content(session.course.id)
        
        # Get course-specific AI settings
        course_ai_settings = get_course_ai_settings(session.course.id)
        custom_prompt = ""
        if course_ai_settings and course_ai_settings.system_prompt:
            custom_prompt = course_ai_settings.system_prompt
        
        # Create system message with course content
        system_message = f"""
        You are an AI tutor specifically knowledgeable about the following course material:
        
        {course_content}
        
        Your role is to help the student understand the course material, answer their questions,
        and provide additional explanations or examples when needed. Always be encouraging, 
        supportive, and focus on educational content relevant to the course.
        
        If a question is outside the scope of the course material, politely redirect the conversation
        to the course topics. If you don't know the answer to a specific question about the course,
        admit that and suggest the student ask their human instructor.
        
        {custom_prompt}
        """
        
        # Get previous messages for context (limit to the last 10 for simplicity)
        previous_messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:20]
        previous_messages = reversed(list(previous_messages))  # Reverse to get chronological order
        
        # Format messages for OpenAI
        messages = [{"role": "system", "content": system_message}]
        
        for msg in previous_messages:
            if msg.role in ['user', 'assistant']:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Send request to OpenAI
        try:
            response = client.chat.completions.create(
                model=settings.model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            ai_response = response.choices[0].message.content
            
            # Save the AI response
            ai_msg = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_response
            )
            
            # Update the session timestamp
            session.save()  # This will update the updated_at field
            
            return {"status": "success", "message": ai_response}
        except Exception as e:
            error_message = f"OpenAI API error: {str(e)}"
            logger.error(error_message)
            
            # Save the error as a system message
            ChatMessage.objects.create(
                session=session,
                role='system',
                content=f"Error: {error_message}"
            )
            
            return {"status": "error", "message": error_message}
            
    except ChatSession.DoesNotExist:
        return {"status": "error", "message": "Chat session not found"}
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}"}

def generate_quiz_questions(course_id, question_type, topic, difficulty, number_of_questions=1):
    """Generate quiz questions using the OpenAI API"""
    try:
        # Get settings
        settings = get_openai_settings()
        
        # Get API key from settings or environment
        api_key = settings.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"status": "error", "message": "OpenAI API key not found. Please configure it in the settings."}
        
        # Set up the OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Get course content
        course_content = get_course_content(course_id)
        
        # Create the prompt for generating quiz questions
        system_message = f"""
        You are an expert educational quiz creator. Your task is to create {number_of_questions} {difficulty} {question_type} question(s) about the topic: "{topic}" for the following course material:
        
        {course_content}
        
        The questions should be directly related to the course content and be appropriate for a university-level course.
        
        For multiple-choice questions, provide 4 options with only one correct answer.
        For true/false questions, clearly state whether the statement is true or false.
        For short-answer questions, provide a model answer.
        
        Format your response as a JSON array with these fields:
        - question_text: The text of the question
        - question_type: The type of question ({question_type})
        - options: An array of options for multiple-choice questions, or null for other types
        - correct_answer: The correct answer or index of the correct option
        - explanation: A brief explanation of why the answer is correct
        - points: Suggested point value (1-5 based on difficulty)
        """
        
        # Send request to OpenAI
        try:
            response = client.chat.completions.create(
                model=settings.model,
                messages=[
                    {"role": "system", "content": system_message},
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                # Extract JSON from the response (it might be surrounded by markdown code blocks)
                if "```json" in ai_response:
                    json_text = ai_response.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_response:
                    json_text = ai_response.split("```")[1].strip()
                else:
                    json_text = ai_response
                
                questions = json.loads(json_text)
                return {"status": "success", "questions": questions}
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {str(e)}")
                return {
                    "status": "error", 
                    "message": "Error parsing the AI-generated questions. Please try again.",
                    "raw_response": ai_response
                }
                
        except Exception as e:
            error_message = f"OpenAI API error: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
            
    except Exception as e:
        logger.error(f"Error generating quiz questions: {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}"} 