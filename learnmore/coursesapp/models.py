from django.db import models
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    instructor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='courses')
    categories = models.ManyToManyField(Category, related_name='courses')
    difficulty = models.PositiveIntegerField(default=100)
    duration = models.CharField(max_length=50, help_text='e.g. 8 weeks, 10 hours')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
