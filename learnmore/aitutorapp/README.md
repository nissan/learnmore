# AI Tutor App for LearnMore Platform

The AI Tutor app provides an intelligent, context-aware assistant for both students and instructors. It uses OpenAI's API with RAG (Retrieval Augmented Generation) to provide course-specific assistance.

## Features

- **For Students**: Chat-based AI tutor that understands course content and can answer questions
- **For Instructors**: AI-assisted quiz question generation and course content assistance
- **RAG Integration**: Uses course content as context to provide more relevant and accurate responses
- **Course-specific Settings**: Each course can have its own AI tutor settings

## Setup Guide

### 1. Prerequisites

- An OpenAI API key (from https://platform.openai.com/api-keys)
- Python 3.8+ with Django 4.0+
- Required packages (see requirements.txt)

### 2. Installation

The AI Tutor app is integrated into the LearnMore platform. No separate installation is needed.

### 3. Configuration

#### Environment Variables

Set the OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your_api_key_here
```

Or add it to your `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

#### Admin Settings

Navigate to `/ai/settings/` in the admin interface to configure:
- OpenAI model (GPT-3.5-turbo, GPT-4, etc.)
- Temperature (creativity level)
- Max tokens (response length)

### 4. Course Data Ingestion for RAG

Course content is automatically ingested for RAG when:

1. **Creating New Courses**: When a new course is created, its content is automatically processed for RAG
2. **Updating Course Content**: When course content is updated, the RAG context is refreshed
3. **Seeding Data**: Using the `seed_courses` management command

To manually seed courses with AI integration:

```bash
# Reset and recreate all course data with AI integration
python manage.py seed_courses --reset

# Add new courses with AI integration without deleting existing data
python manage.py seed_courses
```

The seeding process:
1. Creates demo courses, modules, and quizzes
2. Generates rich content for each module
3. Creates AI settings for each course
4. Ingests all course content into the RAG system

### 5. Usage

#### For Instructors

1. **AI Settings**: Access course-specific AI settings via the "AI Tutor Settings" button on the course detail page
2. **Generate Quiz Questions**: From the "Edit Modules" page, use the "Generate Quiz" button next to any module
3. **Chat with AI**: Use the "Ask AI Tutor" button on the course detail page for assistance with content creation

#### For Students

1. **Chat with AI Tutor**: Click the "Ask AI Tutor" button on any enrolled course's detail page
2. **Start a New Chat**: Use the "New Chat" button to start a fresh conversation
3. **View Chat History**: All previous conversations are saved and can be accessed from the sidebar

## Troubleshooting

- **API Key Issues**: Ensure your OpenAI API key is valid and has sufficient credits
- **Context Limitations**: If the AI seems to lack knowledge about specific course content, try updating the course modules with more detailed information
- **Performance Issues**: Large courses with extensive content may experience some latency in AI responses

## Advanced Configuration

### Custom System Prompts

Instructors can customize how the AI responds by modifying the system prompt in the course AI settings. This allows for:

- Course-specific instruction styles
- Emphasis on certain teaching methodologies
- Custom response formats or structures

### Enabling/Disabling AI Features

Instructors can:
- Enable/disable AI tutor for students
- Enable/disable AI tutor for instructors
- Control AI-assisted quiz generation

## Technical Implementation

The AI tutor uses a hybrid approach:
1. **RAG (Retrieval Augmented Generation)**: Course content is used as context for more accurate responses
2. **OpenAI Integration**: Uses OpenAI's API to generate responses based on the course context and user questions
3. **Django Integration**: Seamlessly integrated with the course management system 