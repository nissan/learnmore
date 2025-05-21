from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from coursesapp.models import Course, Category, Module, Quiz
from aitutorapp.models import CourseAISettings, OpenAISettings
from aitutorapp.utils import get_course_content
import random
from datetime import timedelta
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Seeds the database with demo courses, categories, instructors, and AI settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all courses, modules, quizzes, categories, and AI settings before seeding.'
        )

    def ensure_core_demo_users(self):
        User = get_user_model()
        users = {}
        # Admin
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'is_superuser': True, 'is_staff': True, 'email': 'admin@example.com'}
        )
        admin.set_password('nissan')
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        users['admin'] = admin
        # Instructor
        instructor, _ = User.objects.get_or_create(
            username='instructor',
            defaults={'is_staff': True, 'email': 'instructor@example.com'}
        )
        instructor.set_password('instructorpass')
        instructor.is_staff = True
        instructor.save()
        users['instructor'] = instructor
        # Student
        student, _ = User.objects.get_or_create(
            username='student',
            defaults={'is_staff': False, 'email': 'student@example.com'}
        )
        student.set_password('studentpass')
        student.is_staff = False
        student.save()
        users['student'] = student
        return users

    def create_demo_instructors(self, core_users):
        User = get_user_model()
        instructors = [core_users['instructor']]
        instructor_data = [
            {'username': 'prof_smith', 'first_name': 'John', 'last_name': 'Smith', 'email': 'smith@example.com'},
            {'username': 'dr_jones', 'first_name': 'Emma', 'last_name': 'Jones', 'email': 'jones@example.com'},
            {'username': 'prof_zhang', 'first_name': 'Wei', 'last_name': 'Zhang', 'email': 'zhang@example.com'},
            {'username': 'dr_patel', 'first_name': 'Priya', 'last_name': 'Patel', 'email': 'patel@example.com'},
            {'username': 'prof_miller', 'first_name': 'David', 'last_name': 'Miller', 'email': 'miller@example.com'},
        ]

        for data in instructor_data:
            instructor, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'is_staff': True
                }
            )
            if created:
                instructor.set_password('demo123')  # Set a default password for demo accounts
                instructor.save()
            instructors.append(instructor)
        return instructors

    def create_categories(self):
        categories = [
            'Python Programming',
            'Web Development',
            'Data Science',
            'Machine Learning',
            'Cloud Computing',
            'DevOps',
            'Mobile Development',
            'Cybersecurity',
            'UI/UX Design',
            'Database Management'
        ]
        
        created_categories = []
        for cat_name in categories:
            category, _ = Category.objects.get_or_create(
                name=cat_name,
                slug=slugify(cat_name)
            )
            created_categories.append(category)
        
        return created_categories

    def generate_course_data(self):
        course_prefixes = ['Introduction to', 'Advanced', 'Mastering', 'Professional', 'Complete Guide to']
        course_topics = [
            'Python', 'JavaScript', 'React', 'Node.js', 'Django',
            'Data Analysis', 'Machine Learning', 'AWS', 'Docker',
            'Web Security', 'UI Design', 'API Development'
        ]
        course_suffixes = ['Fundamentals', 'in Practice', 'from Scratch', 'Bootcamp', 'Masterclass']

        title = f"{random.choice(course_prefixes)} {random.choice(course_topics)} {random.choice(course_suffixes)}"
        
        descriptions = [
            f"Learn {title} from industry experts. This comprehensive course covers everything from basics to advanced concepts.",
            f"Master {title} through hands-on projects and real-world applications. Perfect for beginners and intermediate learners.",
            f"Dive deep into {title} with practical examples and industry best practices. Includes certification preparation.",
        ]

        durations = ['4 weeks', '6 weeks', '8 weeks', '10 weeks', '12 weeks']
        difficulties = [100, 200, 300, 400, 500, 600]

        return {
            'title': title,
            'description': random.choice(descriptions),
            'difficulty': random.choice(difficulties),
            'duration': random.choice(durations)
        }

    def get_unique_slug(self, base_slug):
        slug = base_slug
        counter = 1
        while Course.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def setup_ai_settings(self):
        """Setup global OpenAI settings"""
        self.stdout.write('Setting up OpenAI configuration...')
        
        # Create default OpenAI settings if they don't exist
        openai_settings, created = OpenAISettings.objects.get_or_create(
            id=1,
            defaults={
                'api_key': os.environ.get('OPENAI_API_KEY', ''),
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created default OpenAI settings'))
        else:
            self.stdout.write('Using existing OpenAI settings')
        
        return openai_settings

    def create_course_ai_settings(self, course):
        """Create AI settings for a specific course and ingest its content for RAG"""
        self.stdout.write(f'Setting up AI for course: {course.title}')
        
        # Create or update course AI settings
        course_ai_settings, created = CourseAISettings.objects.get_or_create(
            course=course,
            defaults={
                'is_enabled_for_students': True,
                'is_enabled_for_instructors': True,
                'system_prompt': self.generate_system_prompt(course)
            }
        )
        
        # Get course content for RAG context
        course_content = get_course_content(course.id)
        self.stdout.write(f'Ingested {len(course_content)} characters of content for RAG')
        
        return course_ai_settings

    def generate_system_prompt(self, course):
        """Generate a custom system prompt based on the course topic"""
        prompts = [
            f"Focus on providing clear explanations about {course.title} concepts with real-world examples.",
            f"When explaining {course.title}, use analogies that are easy to understand for beginners.",
            f"For this {course.title} course, emphasize practical applications and industry relevance.",
            f"Encourage experimentation and learning by doing when discussing topics in {course.title}.",
        ]
        return random.choice(prompts)

    def handle(self, *args, **kwargs):
        reset = kwargs.get('reset', False)
        if reset:
            self.stdout.write(self.style.WARNING('Resetting courses, modules, quizzes, categories, and AI settings...'))
            from coursesapp.models import Course, Module, Quiz, Category
            from aitutorapp.models import CourseAISettings, ChatSession, ChatMessage
            
            # Delete AI-related data first (to maintain foreign key integrity)
            ChatMessage.objects.all().delete()
            ChatSession.objects.all().delete()
            CourseAISettings.objects.all().delete()
            
            # Then delete course data
            Course.objects.all().delete()
            Module.objects.all().delete()
            Quiz.objects.all().delete()
            Category.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS('All course and AI data cleared.'))

        # Set up OpenAI settings
        openai_settings = self.setup_ai_settings()

        self.stdout.write('Ensuring core demo users (admin/instructor/student)...')
        core_users = self.ensure_core_demo_users()

        self.stdout.write('Creating demo instructors...')
        instructors = self.create_demo_instructors(core_users)
        
        self.stdout.write('Creating categories...')
        categories = self.create_categories()
        
        self.stdout.write('Creating courses with AI integration...')
        for i in range(25):  # Create 25 courses
            course_data = self.generate_course_data()
            base_slug = slugify(course_data['title'])
            unique_slug = self.get_unique_slug(base_slug)
            # Assign instructor: use the main instructor for the first few courses
            if i < 3:
                instructor = core_users['instructor']
            else:
                instructor = random.choice(instructors)
            # Create the course
            course = Course.objects.create(
                title=course_data['title'],
                slug=unique_slug,
                description=course_data['description'],
                instructor=instructor,
                difficulty=course_data['difficulty'],
                duration=course_data['duration'],
                is_public=True,
                is_published=True,  # Ensure published for catalog visibility
                created_at=timezone.now() - timedelta(days=random.randint(0, 60))
            )
            # Add 2-3 random categories
            course.categories.add(*random.sample(categories, random.randint(2, 3)))
            self.stdout.write(f'Created course: {course.title}')

            # Create 3-5 modules for each course
            num_modules = random.randint(3, 5)
            for m in range(1, num_modules + 1):
                module = Module.objects.create(
                    course=course,
                    title=f"Module {m}: {course.title} - Part {m}",
                    description=f"This is the description for module {m} of {course.title}.",
                    order=m,
                    content=self.generate_module_content(course.title, m)
                )
                # Create 1-3 quizzes for each module
                num_quizzes = random.randint(1, 3)
                for q in range(1, num_quizzes + 1):
                    Quiz.objects.create(
                        module=module,
                        title=f"Quiz {q} for {module.title}",
                        instructions=f"Instructions for quiz {q} in module {m} of {course.title}."
                    )
            
            # Set up AI for this course - this ingests the course content for RAG
            self.create_course_ai_settings(course)
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with courses and AI integration!'))
    
    def generate_module_content(self, course_title, module_number):
        """Generate more detailed content for modules to provide better RAG context"""
        topic = course_title.split()[-2] if len(course_title.split()) > 2 else course_title
        
        sections = [
            f"# Introduction to Module {module_number}\n\nThis module will cover key concepts in {topic} that will build on previous modules and prepare you for more advanced topics.\n",
            f"## Key Concepts\n\n- Understanding {topic} fundamentals\n- Working with {topic} in practice\n- Advanced {topic} techniques\n- Industry applications of {topic}\n",
            f"## Learning Objectives\n\nBy the end of this module, you will be able to:\n\n1. Explain core principles of {topic}\n2. Implement basic {topic} solutions\n3. Apply {topic} in real-world scenarios\n4. Evaluate different {topic} approaches\n",
            f"## Detailed Content\n\nIn this section, we'll dive deeper into {topic} and explore how it works in various contexts. We'll cover theoretical foundations as well as practical implementations.\n\nThe most important aspects of {topic} that you should understand are the underlying principles and how they connect to other related technologies and methods.\n",
            f"## Additional Resources\n\n- Recommended reading on {topic}\n- Practice exercises for {topic}\n- Online resources for further learning\n- Community forums discussing {topic}"
        ]
        
        return "\n\n".join(sections) 