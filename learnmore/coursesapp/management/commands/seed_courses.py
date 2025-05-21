from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from coursesapp.models import Course, Category
import random
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with demo courses, categories, and instructors'

    def create_demo_instructors(self):
        User = get_user_model()
        instructors = []
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
        self.stdout.write('Creating demo instructors...')
        instructors = self.create_demo_instructors()
        
        self.stdout.write('Creating categories...')
        categories = self.create_categories()
        
        self.stdout.write('Creating courses...')
        for i in range(25):  # Create 25 courses
            course_data = self.generate_course_data()
            base_slug = slugify(course_data['title'])
            unique_slug = self.get_unique_slug(base_slug)
            # Create the course
            course = Course.objects.create(
                title=course_data['title'],
                slug=unique_slug,
                description=course_data['description'],
                instructor=random.choice(instructors),
                difficulty=course_data['difficulty'],
                duration=course_data['duration'],
                is_public=True,
                created_at=timezone.now() - timedelta(days=random.randint(0, 60))
            )
            # Add 2-3 random categories
            course.categories.add(*random.sample(categories, random.randint(2, 3)))
            self.stdout.write(f'Created course: {course.title}')
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!')) 