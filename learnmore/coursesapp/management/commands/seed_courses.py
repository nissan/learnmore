from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from coursesapp.models import Course, Category, Module, Quiz
import random
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with demo courses, categories, and instructors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all courses, modules, quizzes, and categories before seeding.'
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

    def handle(self, *args, **kwargs):
        reset = kwargs.get('reset', False)
        if reset:
            self.stdout.write(self.style.WARNING('Resetting courses, modules, quizzes, and categories...'))
            from coursesapp.models import Course, Module, Quiz, Category
            Course.objects.all().delete()
            Module.objects.all().delete()
            Quiz.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All course data cleared.'))

        self.stdout.write('Ensuring core demo users (admin/instructor/student)...')
        core_users = self.ensure_core_demo_users()

        self.stdout.write('Creating demo instructors...')
        instructors = self.create_demo_instructors(core_users)
        
        self.stdout.write('Creating categories...')
        categories = self.create_categories()
        
        self.stdout.write('Creating courses...')
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
                    order=m
                )
                # Create 1-3 quizzes for each module
                num_quizzes = random.randint(1, 3)
                for q in range(1, num_quizzes + 1):
                    Quiz.objects.create(
                        module=module,
                        title=f"Quiz {q} for {module.title}",
                        instructions=f"Instructions for quiz {q} in module {m} of {course.title}."
                    )
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!')) 