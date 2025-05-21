from rest_framework import serializers
from .models import Course, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class CourseSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    instructor = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'instructor', 'categories',
            'difficulty', 'duration', 'is_public', 'created_at'
        ] 